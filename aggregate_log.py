#! /usr/bin/env python


import asyncore
import sys
import json
import re
import socket


PORT    = 20000
LINE_RE = re.compile('[^\n]*\n')



class NodeConnection(asyncore.dispatcher):
    def __init__(self, ip, port, id):
        asyncore.dispatcher.__init__(self)
        self.ip   = ip     # remote ip
        self.port = port   # remote port
        self.id   = id     # node identifier for the user
        self.read_buff = ''# received data buffer
        self.__connect()

    def __connect(self):
        ''' Connects to node serial port '''
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.ip, self.port))

    def __print_line(self, line):
        '''
        Print one line prefixed by id in format:
        id;text
        No newline added
        '''
        sys.stdout.write('%s;%s' % (self.id, line))

    def handle_close(self):
        '''
        Print the last data still not printed and close the connection
        '''
        # Do not print empty lines
        if self.read_buff != '':
            self.__print_line(self.read_buff + '\n')
            self.read_buff = ''
        self.close()

    def handle_read(self):
        '''
        Append read bytes to buffer and run data handler,
        Close socket if read string is empty
        '''
        rec_data = self.recv(8192)
        if rec_data == '':
            self.handle_close()
        else:
            self.read_buff += rec_data
            self.__handle_data()

    def handle_error(self):
        print >> sys.stderr, "Could not connect to %s" % self.ip

    def __handle_data(self):
        ''' Print the data received line by line '''
        for line in LINE_RE.finditer(self.read_buff):
            self.read_buff = LINE_RE.sub('', self.read_buff)
            self.__print_line(line.group())
        assert '\n' not in self.read_buff, 'Newline still present after data handling'


def extract_nodes(experiment_ressources_json):
    nodes = [ i['network_address'] for i in experiment_ressources_json['items'] ]
    for node in nodes:
        assert re.match('node\d*\.[a-z]*\.senslab\.info', node), \
                "Node name not recognized: %s" % node
    return nodes




if __name__ == "__main__":
    '''
    Reads nodes from ressource json and aggregate serial links of all nodes
    '''

    try:
        j = json.loads(sys.stdin.read())
    except ValueError, e:
        print >> sys.stderr, 'Could not load JSON object from stdin.'
        sys.exit(1)

    nodes_list = extract_nodes(j)

    # create all the connections
    for node in nodes_list:
        id = re.findall('^node\d*', node)[0]
        NodeConnection(node, PORT, id)

    asyncore.loop(timeout=5)

