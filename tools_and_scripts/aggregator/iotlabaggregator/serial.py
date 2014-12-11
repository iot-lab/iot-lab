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

import logging
import sys
import argparse

import iotlabaggregator
from iotlabaggregator import connections, common

from iotlabcli.parser import common as common_parser

NODES_ARCHIS = ("wsn430:cc2420", "wsn430:cc1101", "m3:at86rf231")

# debug logger for lines
LINE_LOGGER = logging.getLogger('serial_aggregator_line')
_LINE_LOGGER = logging.StreamHandler(sys.stdout)
_LINE_LOGGER.setFormatter(iotlabaggregator.LOG_FMT)
LINE_LOGGER.setLevel(logging.INFO)
LINE_LOGGER.addHandler(_LINE_LOGGER)


class SerialConnection(connections.Connection):  # pylint:disable=R0903,R0904
    """
    Handle the connection to one node serial link.
    Data is managed with asyncore. So to work asyncore.loop() should be run.

    :param print_lines: should lines be printed to stdout
    :param line_handler: additional function to call on received lines.
        `line_handler(identifier, line)`

    """
    port = 20000

    def __init__(self, hostname, print_lines=False, line_handler=None):
        super(SerialConnection, self).__init__(hostname)

        self.line_handler = common.Event()
        if print_lines:
            self.line_handler.append(self._print_line)
        if line_handler:
            self.line_handler.append(line_handler)

    def handle_data(self, data):
        """ Print the data received line by line """

        lines = data.splitlines(True)
        data = ''
        for line in lines:
            if line[-1] == '\n':
                # Handle Unicode.
                self.line_handler(
                    self.hostname, line[:-1].decode('utf-8', 'replace'))
            else:
                data = line  # last incomplete line
        return data

    @staticmethod
    def _print_line(identifier, line):
        """ Print one line prefixed by id in format: """
        LINE_LOGGER.info("%s;%s", identifier, line)


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


def opts_parser():
    """ Argument parser object """
    parser = argparse.ArgumentParser()
    common.add_nodes_selection_parser(parser)
    parser.add_argument(
        '--with-a8', action='store_true',
        help=('redirect open-a8 serial port. ' +
              '`/etc/init.d/serial_redirection` must be running on the nodes'))
    return parser


def select_nodes(nodes, with_a8):
    """ Select all gateways and open-a8 if `with_a8` """
    # all gateways urls except A8
    nodes_list = [n for n in nodes if not n.startswith('a8')]

    # add open-a8 urls with 'node-' in front all urls
    if with_a8:
        nodes_list += ['node-' + n for n in nodes if n.startswith('a8')]
    return nodes_list


def main():
    """ Aggregate all nodes outputs """
    opts = opts_parser().parse_args()

    try:
        # parse arguments
        nodes = common.get_nodes_selection(**vars(opts))
        nodes_list = select_nodes(nodes, opts.with_a8)

        # Create the aggregator
        aggregator = connections.Aggregator(nodes_list, SerialConnection,
                                            print_lines=True)  # SerialArgs
    except (ValueError, RuntimeError) as err:
        sys.stderr.write("%s\n" % err)
        exit(1)

    try:
        aggregator.start()
        read_input(aggregator)
    except (KeyboardInterrupt, EOFError):
        iotlabaggregator.LOGGER.info("Stopping")
    finally:
        aggregator.stop()

if __name__ == "__main__":
    main()
