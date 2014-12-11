#! /usr/bin/python
# -*- coding: utf-8 -*-

""" Sniff tcp socket zep messages and save them as pcap """

import argparse
import sys
import signal

import iotlabaggregator
from iotlabaggregator import connections, common, zeptopcap


class SnifferConnection(connections.Connection):  # pylint:disable=R0904
    port = 30000
    pkt_length_offset = 32

    def __init__(self, hostname, message_handler=(lambda data: None)):
        super(SnifferConnection, self).__init__(hostname)
        self.message_handler = message_handler

    def handle_data(self, data):
        """ Print the data received line by line """

        while True:
            data = self._strip_until_pkt_start(data)
            # has header
            if not data.startswith('EX\2'):
                break

            # has enough data to read length
            if len(data) < self.pkt_length_offset:
                break
            pkt_len = ord(data[self.pkt_length_offset - 1])
            full_len = self.pkt_length_offset + pkt_len

            # packet is full
            if len(data) < full_len:
                break

            iotlabaggregator.LOGGER.info("Got one message")
            self.message_handler(data[0:full_len])
            data = data[full_len:]
        return data

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
        if whole_index == 0:   # is stripped
            return msg
        if whole_index != -1:  # found, strip first lines
            return msg[whole_index:]

        # not found but remove some chars from the buffer
        # at max 2 required in this case
        # might be invalid packet but keeps buffer small anymay
        return msg[-2:]


def opts_parser():
    """ Argument parser object """
    parser = argparse.ArgumentParser()
    common.add_nodes_selection_parser(parser)
    parser.add_argument(
        '-o', '--outfile', required=True, type=argparse.FileType('wb'),
        help="File wher the pcap will be saved. Use '-' for stdout.")
    return parser


def select_nodes(nodes):
    """ Select all gateways that support sniffer """
    nodes_list = [n for n in nodes if n.startswith(('m3', 'a8'))]
    return nodes_list


def main():
    opts = opts_parser().parse_args()
    try:
        # parse arguments
        nodes = common.get_nodes_selection(**vars(opts))
        nodes_list = select_nodes(nodes)

        zpcap = zeptopcap.ZepPcap(opts.outfile)

        # Create the aggregator
        aggregator = connections.Aggregator(
            nodes_list, SnifferConnection,
            message_handler=zpcap.write)  # SnifferArgs
    except (ValueError, RuntimeError) as err:
        sys.stderr.write("%s\n" % err)
        exit(1)

    try:
        aggregator.start()
        signal.pause()
    except KeyboardInterrupt:
        iotlabaggregator.LOGGER.info("Stopping")
    finally:
        aggregator.stop()


if __name__ == '__main__':
    main()
