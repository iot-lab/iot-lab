#! /usr/bin/python
# -*- coding: utf-8 -*-

""" Sniff tcp socket zep messages and save them as pcap """

import asyncore
import argparse
import sys
import socket

import zeptopcap



class SnifferConnection(asyncore.dispatcher):  # pylint:disable=R0904
    port = 30000
    def __init__(self, hostname, message_handler=None):
        asyncore.dispatcher.__init__(self)
        self.node_id = hostname.split('.')[0]  # node identifier for the user

        #self.message_handler = Event()
        if message_handler:
            self.message_handler = message_handler
        else:
            self.message_handler = (lambda *args, **kwargs:None)
        self.data_buff = ''      # received data buffer

    def start(self):
        """ Connects to node serial port """
        self.data_buff = ''      # reset data
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.node_id, self.port))

    def handle_close(self):
        """ Print the last data still not printed and close the connection """
        # Do not print empty lines
        self.data_buff = ''
        LOGGER.error('%s;Connection closed', self.node_id)
        self.close()

    def handle_read(self):
        """ Append read bytes to buffer and run data handler. """
        self.data_buff += self.recv(8192)
        self.data_buff = self._handle_data(self.data_buff)

    def handle_error(self):
        """ Connection failed """
        LOGGER.error('%s;%r', self.node_id, sys.exc_info())

    @staticmethod
    def _strip_until_pkt_start(msg):
        """
        >>> msg = 'abcdEEEEEEEEEX\2'
        >>> 'EX\2' == SnifferConnection._strip_until_pkt_start(msg)
        True

        >>> msg = 'abcdEEEEEEEEEX\2' '12345'
        >>> 'EX\2''12345' == SnifferConnection._strip_until_pkt_start(msg)
        True

        >>> msg = 'abcdEEE'
        >>> 'EE' == SnifferConnection._strip_until_pkt_start(msg)
        True

        >>> msg = 'abcdEEEa'
        >>> 'Ea' == SnifferConnection._strip_until_pkt_start(msg)
        True

        >>> msg = 'a'
        >>> 'a' == SnifferConnection._strip_until_pkt_start(msg)
        True

        """
        whole_index = msg.find('EX\2')
        if whole_index == 0:  # is stripped
            return msg
        if whole_index != -1: # found, strip first lines
            return msg[whole_index:]

        # not found but remove some chars from the buffer
        # at max 2 required in this case
        # might be invalid packet but keeps buffer small anymay
        return msg[-2:]


    def _handle_data(self, data):
        """ Print the data received line by line """
        LENGTH_OFFSET = 32

        while True:
            data = self._strip_until_pkt_start(data)
            # has header
            if not data.startswith('EX\2'):
                break

            # has enough data to read length
            if len(data) < LENGTH_OFFSET:
                break
            pkt_len = ord(data[LENGTH_OFFSET-1])
            full_len = LENGTH_OFFSET + pkt_len

            # packet is full
            if len(data) < full_len:
                break

            self.message_handler(data[0:full_len])
            data = data[full_len:]
        return data

def opts_parser():
    """ Argument parser object """
    parser = argparse.ArgumentParser()
    parser.add_argument('node_id', help="Node Id to sniff")
    parser.add_argument('-o', '--outfile', required=True,
                        type=argparse.FileType('w'),
                        help="File wher the pcap will be saved")
    return parser


def main(args):
    opts = opts_parser().parse_args(args[1:])
    zpcap = zeptopcap.ZepPcap(opts.outfile)
    conn = SnifferConnection(opts.node_id, zpcap.write)
    conn.start()
    asyncore.loop()


if __name__ == '__main__':
    main(sys.argv)
