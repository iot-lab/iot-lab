#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""
Serial aggregator
=================

Take an experiment description as input.
Gather all nodes output to stdout, prefixed by the node number and timestamp.

    1395240359.286712;node46; Type Enter to stop printing this help
    1395240359.286853;node46;
    1395240359.292523;node9;
    1395240359.292675;node9;Senslab Simple Demo program

Usage
-----

On each server your experiment is run on:

    $ ./serial_aggregator.py [opts]
    1395240359.286712;node46; Type Enter to stop printing this help
    1395240359.286853;node46;
    1395240359.292523;node9;
    1395240359.292675;node9;Senslab Simple Demo program


Warning
-------

If a node sends only characters without newlines, the output is never printed.
To give a 'correct' looking output, only lines are printed.


### Multi sites experiments ###

The script will get the serial links current site nodes.
For multi-sites experiments, you should run the script on each site server.
"""

# use readline for 'raw_input'
import readline  # pylint:disable=unused-import

import asyncore
import socket
import logging
import threading
import sys
import argparse
import os

import iotlabcli
from iotlabcli import experiment
from iotlabcli.parser import common as common_parser
from iotlabcli.parser import node as node_parser

PORT = 20000

NODES_ARCHIS = ("wsn430:cc2420", "wsn430:cc1101", "m3:at86rf231")
HOSTNAME = os.uname()[1]

# Use loggers for all outputs to have the same config
_FORMAT = logging.Formatter("%(created)f;%(message)s")
# error logger
LOGGER = logging.getLogger('serial_aggregator')
_LOGGER = logging.StreamHandler(sys.stderr)
_LOGGER.setFormatter(_FORMAT)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(_LOGGER)
# debug logger for lines
LINE_LOGGER = logging.getLogger('serial_aggregator_line')
_LINE_LOGGER = logging.StreamHandler(sys.stdout)
_LINE_LOGGER.setFormatter(_FORMAT)
LINE_LOGGER.setLevel(logging.INFO)
LINE_LOGGER.addHandler(_LINE_LOGGER)


# http://stackoverflow.com/questions/1092531/event-system-in-python
class Event(list):
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

    Example Usage:
    >>> def f(x):
    ...     print 'f(%s)' % x
    >>> def g(x):
    ...     print 'g(%s)' % x

    >>> e = Event()
    >>> e()
    >>> e.append(f)
    >>> e(123)
    f(123)
    >>> e.remove(f)
    >>> e()

    >>> e += (f, g)
    >>> e(10)
    f(10)
    g(10)
    >>> del e[0]
    >>> e(2)
    g(2)


    >>> e   # doctest: +ELLIPSIS
    Event('[<function g at 0x...>]')

    """

    def __call__(self, *args, **kwargs):
        for func in self:
            func(*args, **kwargs)

    def __repr__(self):
        return "Event(%r)" % list.__repr__(self)


class NodeConnection(asyncore.dispatcher):  # pylint:disable=R0904
    """
    Handle the connection to one node serial link.
    Data is managed with asyncore. So to work asyncore.loop() should be run.

    :param print_lines: should lines be printed to stdout
    :param line_handler: additional function to call on received lines.
        `line_handler(identifier, line)`

    """
    def __init__(self, hostname, print_lines=False, line_handler=None):
        asyncore.dispatcher.__init__(self)
        self.node_id = hostname.split('.')[0]  # node identifier for the user

        self.line_handler = Event()
        if print_lines:
            self.line_handler.append(self._print_line)
        if line_handler:
            self.line_handler.append(line_handler)
        self.read_buff = ''      # received data buffer

    def start(self):
        """ Connects to node serial port """
        self.read_buff = ''      # reset data
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.node_id, PORT))

    def handle_close(self):
        """ Print the last data still not printed and close the connection """
        # Do not print empty lines
        self.read_buff = ''
        LOGGER.error('%s;Connection closed', self.node_id)
        self.close()

    def handle_read(self):
        """ Append read bytes to buffer and run data handler. """
        self.read_buff += self.recv(8192)
        self._handle_data()

    def handle_error(self):
        """ Connection failed """
        LOGGER.error('%s;%r', self.node_id, sys.exc_info())

    def _handle_data(self):
        """ Print the data received line by line """

        lines = self.read_buff.splitlines(True)
        self.read_buff = ''
        for line in lines:
            if line[-1] == '\n':
                # Handle Unicode.
                self.line_handler(
                    self.node_id, line[:-1].decode('utf-8', 'replace'))
            else:
                self.read_buff = line  # last incomplete line

    @staticmethod
    def _print_line(identifier, line):
        """ Print one line prefixed by id in format: """
        LINE_LOGGER.info("%s;%s", identifier, line)


class NodeAggregator(dict):  # pylint:disable=too-many-public-methods
    """
    Create a list of nodes Aggregator from 'nodes_list'
    Each node is stored in the entry with it's node_id

    It as a thread that runs asyncore.loop() in the background.

    After init, it can be manipulated like a dict.
    """
    def __init__(self, nodes_list, *args, **kwargs):
        if not nodes_list:
            raise ValueError("NodeAggregator: Empty nodes list %r" %
                             nodes_list)

        super(NodeAggregator, self).__init__()
        self.thread = threading.Thread(target=asyncore.loop,
                                       kwargs={'timeout': 1, 'use_poll': True})
        # create all the Nodes
        for node_url in nodes_list:
            node = NodeConnection(node_url, *args, **kwargs)
            self[node.node_id] = node

    def start(self):
        """ Connect all nodes and run asyncore.loop in a thread """
        for node in self.itervalues():
            node.start()
        self.thread.start()
        LOGGER.info("Aggregator started")

    def stop(self):
        """ Stop the nodes connection and stop asyncore.loop thread """
        for node in self.itervalues():
            node.close()
        self.thread.join()

    def send_nodes(self, nodes_list, message):
        """ Send the `message` to `nodes_list` nodes

        If nodes_list is None, send to all nodes """
        if nodes_list is None:
            LOGGER.debug("Broadcast: %r", message)
            self.broadcast(message)
        else:
            LOGGER.debug("Send: %r to %r", message, nodes_list)
            for node in nodes_list:
                self._send(node, message)

    def _send(self, node_id, message):
        """ Safe send message to node """
        try:
            self[node_id].send(message)
        except KeyError:
            LOGGER.warning("Node not managed: %s", node_id)

    def broadcast(self, message):
        """ Send a message to all the nodes serial links """
        for node in self.itervalues():
            node.send(message)


def extract_nodes(resources, with_a8=False):
    """ Extract the nodes with an serial link accessible from this server """
    sites_nodes = [n for n in resources['items'] if n['site'] == HOSTNAME]
    nodes = [n['network_address'] for n in sites_nodes if
             n['archi'] in NODES_ARCHIS]

    if with_a8:
        nodes += ['node-' + n['network_address'] for n in sites_nodes if
                  n['archi'] == 'a8:at86rf231']
    return nodes


def opts_parser():
    """ Argument parser object """
    parser = argparse.ArgumentParser()
    common_parser.add_auth_arguments(parser)

    nodes_group = parser.add_argument_group(
        description="By default, select currently running experiment nodes",
        title="Nodes selection")

    nodes_group.add_argument('-i', '--id', dest='experiment_id', type=int,
                             help='experiment id submission')

    nodes_group.add_argument(
        '-l', '--list', type=node_parser.nodes_list_from_str,
        dest='nodes_list', help='nodes list, may be given multiple times')

    nodes_group.add_argument(
        '--with-a8', action='store_true',
        help=('redirect open-a8 serial port. ' +
              '`serial_redirection` must be run on the node'))
    return parser


def get_nodes(api, exp_id=None, nodes_list=None, with_a8=False):
    """ Get nodes list from experiment and/or nodes_list.
    Or currently running experiment if none provided """

    nodes = []
    if exp_id is None and nodes_list is None:
        # Try to get current experiment
        exp_id = iotlabcli.get_current_experiment(api)

    if exp_id is not None:
        res = experiment.get_experiment(api, exp_id, 'resources')
        nodes.extend(extract_nodes(res, with_a8))

    if nodes_list is not None:
        nodes.extend([n for n in nodes_list if HOSTNAME in n])

    return nodes


def extract_nodes_and_message(line):
    """
    >>> extract_nodes_and_message('')
    (None, '')

    >>> extract_nodes_and_message(' ')
    (None, ' ')

    >>> extract_nodes_and_message('message')
    (None, 'message')

    >>> extract_nodes_and_message('-;message')
    (None, 'message')

    >>> extract_nodes_and_message('my_message_csv;message')
    (None, 'my_message_csv;message')

    >>> extract_nodes_and_message('M3,1;message')
    (['m3-1'], 'message')

    >>> extract_nodes_and_message('m3,1-3+5;message')
    (['m3-1', 'm3-2', 'm3-3', 'm3-5'], 'message')

    >>> extract_nodes_and_message('wsn430,3+5;message')
    (['wsn430-3', 'wsn430-5'], 'message')

    >>> extract_nodes_and_message('a8,1+2;message')
    (['node-a8-1', 'node-a8-2'], 'message')

    # use dash in node destination
    >>> extract_nodes_and_message('m3-1;message')
    (['m3-1'], 'message')

    >>> extract_nodes_and_message('A8-1;message')
    (['node-a8-1'], 'message')

    >>> extract_nodes_and_message('node-a8-1;message')
    (['node-a8-1'], 'message')

    """
    try:
        nodes_str, message = line.split(';')
        if '-' == nodes_str:
            # -
            return None, message

        if ',' in nodes_str:
            # m3,1-5+4
            archi, list_str = nodes_str.split(',')
        else:
            # m3-1 , a8-2, node-a8-3, wsn430-4
            # convert it as if it was with a comma
            archi, list_str = nodes_str.rsplit('-', 1)
            int(list_str)  # ValueError if not int

        # normalize archi
        archi = archi.lower()
        archi = 'node-a8' if 'a8' == archi else archi

        # get nodes list
        nodes = common_parser.nodes_id_list(archi, list_str)

        return nodes, message
    except (IndexError, ValueError):
        return None, line


def read_input(aggregator):
    """ Read input and sends the messages to the given nodes """
    while True:
        line = raw_input()
        nodes, message = extract_nodes_and_message(line)

        if (None, '') != (nodes, message):
            aggregator.send_nodes(nodes, message + '\n')
        # else: Only hitting 'enter' to get spacing


def main():
    """ Reads nodes from ressource json in stdin and
    aggregate serial links of all nodes
    """
    parser = opts_parser()
    opts = parser.parse_args()

    try:
        username, password = iotlabcli.get_user_credentials(
            opts.username, opts.password)
        api = iotlabcli.Api(username, password)
        nodes_list = get_nodes(
            api, opts.experiment_id, opts.nodes_list, with_a8=opts.with_a8)
    except RuntimeError as err:
        sys.stderr.write("%s\n" % err)
        exit(1)

    try:
        aggregator = NodeAggregator(nodes_list, print_lines=True)
    except ValueError as err:
        sys.stderr.write("%r\n" % err)
        exit(1)

    aggregator.start()

    try:
        read_input(aggregator)
    except KeyboardInterrupt:
        LOGGER.info("Stopping")
    finally:
        aggregator.stop()

if __name__ == "__main__":
    main()
