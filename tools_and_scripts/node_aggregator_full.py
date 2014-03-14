#! /usr/bin/env python


import asyncore
import sys
import socket
import os
import logging
import threading


PORT = 20000

NODES_ARCHIS = ("wsn430:cc2420", "wsn430:cc1101", "m3:at86rf231")
HOSTNAME = os.uname()[1]

logging.basicConfig(format="%(message)s")
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)


class NodeConnection(asyncore.dispatcher):
    def __init__(self, ip, port, identifier, line_handler=None):
        asyncore.dispatcher.__init__(self)
        self.ip = ip             # remote ip
        self.port = port         # remote port
        self.id = identifier     # node identifier for the user
        self.line_handler = line_handler or self._print_line
        self.read_buff = ''      # received data buffer

    def start(self):
        ''' Connects to node serial port '''
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.ip, self.port))

    def handle_close(self):
        ''' Print the last data still not printed and close the connection '''
        # Do not print empty lines
        if self.read_buff != '':
            self.line_handler(self.id, self.read_buff)
        self.read_buff = ''

        print >> sys.stderr, '%s;Connection closed' % self.ip
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
        print >> sys.stderr, "%s;Connection error" % self.ip

    def _handle_data(self):
        ''' Print the data received line by line '''

        lines = self.read_buff.splitlines(True)
        for line in lines:
            if line[-1] == '\n':
                self.line_handler(self.id, line)
            else:
                self.read_buff = line  # incomplete line

    def _print_line(self, identifier, line):
        ''' Print one line prefixed by id in format: '''
        LOGGER.info((self.id, line))

class NodeAggregator(object):
    def __init__(self, nodes_list):
        self.nodes_dict = {}
        self.thread = threading.Thread(target=asyncore.loop,
                                       kwargs = {'timeout':1})

        # create all the Nodes
        for node in nodes_list:
            identifier = node.split('.')[0]
            node_conn = NodeConnection(node, PORT, identifier)
            self.nodes_dict[identifier] = node_conn

    def start(self):
        for node in self.nodes_dict.itervalues():
            node.start()
        self.thread.start()

    def stop(self):
        for node in self.nodes_dict.itervalues():
            node.close()
        self.thread.join()

    def send_message(self, identifier, message):
        if identifier is None:
            nodes = self.nodes_dict.itervalues()
        else:
            nodes = [self.nodes_dict[identifier]]

        for node in nodes:
            node.send(message)




def extract_nodes(ressources_json, hostname):
    nodes = [node['network_address'] for node in ressources_json['items'] if
             node['archi'] in NODES_ARCHIS and node['site'] == hostname]
    return nodes


def extract_json(stdin):
    import json
    try:
        json_dict = json.loads(sys.stdin.read())
    except ValueError:
        print >> sys.stderr, 'Could not load JSON object from stdin.'
        sys.exit(1)
    return json_dict


def _test_tp_serial_and_radio(aggregator):

    import time
    time.sleep(1)

    aggregator.send_message(None, '\n')
    aggregator.send_message(None, '\n')
    time.sleep(1)
    print "Should be stopped now"
    time.sleep(1)

    node_id = aggregator.nodes_dict.keys()[0]

    aggregator.send_message(node_id, 't')
    time.sleep(0.5)
    aggregator.send_message(node_id, 's')
    time.sleep(0.5)
    aggregator.send_message(node_id, 't')
    time.sleep(0.5)
    aggregator.send_message(node_id, 'l')
    time.sleep(0.5)
    aggregator.send_message(node_id, 'l')
    time.sleep(0.5)



def main():
    '''
    Reads nodes from ressource json and aggregate serial links of all nodes
    '''

    import signal
    json_dict = extract_json(sys.stdin)

    nodes_list = extract_nodes(json_dict, HOSTNAME)

    aggregator = NodeAggregator(nodes_list)
    aggregator.start()
    try:

        _test_tp_serial_and_radio(aggregator)


        signal.signal(signal.SIGINT, (lambda signal, frame: 0))
        signal.pause()
        print "closing connections"
    except Exception:
        pass
    finally:
        aggregator.stop()


if __name__ == "__main__":
    main()
