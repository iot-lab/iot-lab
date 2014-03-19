#! /usr/bin/env python


import asyncore
import socket
import logging
import threading

PORT = 20000

NODES_ARCHIS = ("wsn430:cc2420", "wsn430:cc1101", "m3:at86rf231")

logging.basicConfig(format="%(created)f;%(message)s")
LOGGER = logging.getLogger()


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

    """
    def __call__(self, *args, **kwargs):
        for func in self:
            func(*args, **kwargs)

    def __repr__(self):
        return "Event(%r)" % list.__repr__(self)


class NodeConnection(asyncore.dispatcher):
    def __init__(self, hostname, line_handler=None):
        asyncore.dispatcher.__init__(self)
        self.node_id = hostname.split('.')[0]  # node identifier for the user

        self.line_handler = Event([line_handler or self._print_line])
        self.read_buff = ''      # received data buffer

    def start(self):
        ''' Connects to node serial port '''
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.node_id, PORT))

    def handle_close(self):
        ''' Print the last data still not printed and close the connection '''
        # Do not print empty lines
        if self.read_buff != '':
            self.line_handler(self.node_id, self.read_buff)
        self.read_buff = ''

        LOGGER.error('%s;Connection closed', self.node_id)
        self.close()

    def handle_read(self):
        '''
        Append read bytes to buffer and run data handler,
        Close socket if read string is empty
        '''
        rec_data = self.recv(8192)
        if rec_data != '':
            self.read_buff += rec_data
            self._handle_data()
        else:
            pass  # connection will be closed

    def handle_error(self):
        LOGGER.error('%s;Connection error', self.node_id)

    def _handle_data(self):
        ''' Print the data received line by line '''

        lines = self.read_buff.splitlines(True)
        for line in lines:
            if line[-1] == '\n':
                self.line_handler(self.node_id, line[:-1])
            else:
                self.read_buff = line  # incomplete line

    @staticmethod
    def _print_line(identifier, line):
        ''' Print one line prefixed by id in format: '''
        LOGGER.debug("%s;%s", identifier, line)


class NodeAggregator(dict):
    def __init__(self, nodes_list):
        super(NodeAggregator, self).__init__()
        self.thread = threading.Thread(target=asyncore.loop,
                                       kwargs={'timeout': 1, 'use_poll': True})
        # create all the Nodes
        for node_url in nodes_list:
            node = NodeConnection(node_url)
            self[node.node_id] = node

    def start(self):
        for node in self.itervalues():
            node.start()
        self.thread.start()

    def stop(self):
        for node in self.itervalues():
            node.close()
        self.thread.join()

    def broadcast(self, message):
        for node in self.itervalues():
            node.send(message)


def extract_nodes(ressources_json, server_hostname):
    nodes = [node['network_address'] for node in ressources_json['items'] if
             node['archi'] in NODES_ARCHIS and node['site'] == server_hostname]
    return nodes


def extract_json(stdin):
    import json
    try:
        json_dict = json.loads(stdin.read())
    except ValueError:
        print 'Could not load JSON object from stdin.'
        exit(1)
    return json_dict


def main():
    '''
    Reads nodes from ressource json and aggregate serial links of all nodes
    '''
    import sys
    import signal
    import os

    json_dict = extract_json(sys.stdin)

    nodes_list = extract_nodes(json_dict, os.uname()[1])

    aggregator = NodeAggregator(nodes_list)

    LOGGER.setLevel(logging.DEBUG)

    aggregator.start()
    try:

        signal.signal(signal.SIGINT, (lambda signal, frame: 0))
        signal.pause()
        print "Closing connections"
    finally:
        aggregator.stop()

if __name__ == "__main__":
    main()
