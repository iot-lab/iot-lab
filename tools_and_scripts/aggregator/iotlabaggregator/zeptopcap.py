#! /usr/bin/python
# -*- coding: utf-8 -*-


""" Generate pcap files from zep messages """

#
#  http://www.codeproject.com/Tips/612847/ \
#      Generate-a-quick-and-easy-custom-pcap-file-using-P

import sys
import datetime
import calendar
import struct


class ZepPcap(object):  # pylint:disable=too-few-public-methods
    """ Zep to Pcap converter
    On `write` encapsulate the message as a zep packet in `outfile` pcap format
    """
    zep_port = 17754
    # PCAP headers as native endian
    pcap_global_hdr = struct.pack(
        '=LHHLLLL',
        0xa1b2c3d4,    # Pcap header Little Endian
        2,             # File format major revision (i.e. pcap <2>.4)
        4,             # File format minor revision (i.e. pcap 2.<4>)
        0,             # GMT to local correction: 0 if timestamps are UTC
        0,             # accuracy of timestamps -> set it to 0
        0xffff,        # packet capture limit -> typically 65535
        1,             # Link: Ethernet
    )

    # Network headers as network endian
    eth_hdr = struct.pack('!3H3HH',
                          0, 0, 0,  # dst mac addr
                          0, 0, 0,  # src mac addr
                          0x0800)   # Protocol: (0x0800 == IP)

    def __init__(self, outfile):
        self.out = outfile
        # Write global header
        self.out.write(self.pcap_global_hdr)
        self.out.flush()

    def write(self, packet):
        """ Save packet in pcap outfile """
        date = datetime.datetime.utcnow()
        timestamp = (calendar.timegm(date.utctimetuple()), date.microsecond)

        # Calculate all headers
        length = len(packet)

        udp_hdr = self._udp_header(length)
        length += len(udp_hdr)

        ip_hdr = self._ip_header(length)
        length += len(ip_hdr)

        eth_hdr = self._eth_header(length)
        length += len(eth_hdr)

        pcap_hdr = self._pcap_header(length, timestamp[0], timestamp[1])
        length += len(pcap_hdr)

        # Actually write the data
        self.out.write(pcap_hdr)
        self.out.write(eth_hdr)
        self.out.write(ip_hdr)
        self.out.write(udp_hdr)
        self.out.write(packet)
        self.out.flush()

    def _udp_header(self, pkt_len):
        """ Get UDP Header

        2B - src_port: ZEP_PORT also but not required
        2B - dst_port: ZEP_PORT == 17754
        2B - length:   header + packet length
        2B - checksum: Disable == 0

        """
        hdr_struct = struct.Struct('!HHHH')
        udp_len = hdr_struct.size + pkt_len
        udp_hdr = hdr_struct.pack(self.zep_port, self.zep_port, udp_len, 0)
        return udp_hdr

    def _ip_header(self, pkt_len):
        """ Get the IP Header

        1B - Version | IHL:           0x45: [4 | 5] : [4b | 4b]
        1B - Type of Service:         0
        2B - Length:                  pkt_len + Header length
        2B - Identification:          0
        2B - Flags | Fragment offset: 0x4000: [2 | 0] : [3b | 13b]
        1B - TTL:                     0xff
        1B - Protocol:                0x11 UDP
        2B - Checksum:                calculated
        4B - Source Address:          0x7F000001 (127.0.0.1)
        4B - Destination Address:     0x7F000001 (127.0.0.1)

        """
        hdr_struct = struct.Struct('!BBHHHBBHLL')
        ip_len = hdr_struct.size + pkt_len

        # generate header with checksum == 0 to calculate checksum
        checksum = 0
        ip_hdr_csum = hdr_struct.pack(0x45, 0, ip_len, 0, 0x4000, 0xff, 0x11,
                                      checksum, 0x7F000001, 0x7F000001)
        checksum = self._ip_checksum(ip_hdr_csum)

        # Generate header with correct checksum
        ip_hdr = hdr_struct.pack(0x45, 0, ip_len, 0, 0x4000, 0xff, 0x11,
                                 checksum, 0x7F000001, 0x7F000001)
        return ip_hdr

    def _eth_header(self, pkt_len):  # pylint:disable=unused-argument
        """ Return a static empty ethernet header

        6B - dst mac addr: 0
        6B - src mac addr: 0
        2B - protocol:     0x0800 (IP)
        """
        return self.eth_hdr

    @staticmethod
    def _pcap_header(pkt_len, t_s, t_us):
        """ Get the PCAP Header

        4B - Timestamp seconds:      current time
        4B - Timestamp microseconds: current time
        4B - Number of octet saved:  pkt_len
        4B - Actual lengt of packet: pkt_len
        """

        hdr_struct = struct.Struct('=LLLL')
        pcap_len = pkt_len
        pcap_hdr = hdr_struct.pack(t_s, t_us, pcap_len, pcap_len)
        return pcap_hdr

    @staticmethod
    def _ip_checksum(hdr):
        """ Calculate the ip checksum for given header """
        assert 0 == (len(hdr) % 2)  # hdr has even length
        word_pack = struct.Struct('!H')

        # Sum all 16bits
        hdr_split = (hdr[i:i+2] for i in range(0, len(hdr), 2))
        csum = sum((word_pack.unpack(word)[0] for word in hdr_split))

        # Reduce to 16b and save the one complement
        checksum = (csum + (csum >> 16)) & 0xFFFF ^ 0xFFFF
        return checksum


def main():
    """ Main function """

    import binascii
    zep_message_str = (
        '45 58 02 01'   # Base Zep header
        '0B 00 01 00 ff'   # chan | dev_id | dev_id| LQI/CRC_MODE |  LQI
        '00 00 00 00'   # Timestamp msb
        '00 00 00 00'   # timestamp lsp

        '00 00 00 01'   # seqno

        '00 01 02 03'   # reserved 0-3/10
        '04 05 16 07'   # reserved 4-7/10
        '08 09'         # reserved 8-9 / 10
        '08'            # Length 2 + data_len
        '61 62 63'      # Data
        '41 42 43'      # Data
        'FF FF'         # CRC)
    )
    zep_message = binascii.a2b_hex(''.join(zep_message_str.split()))

    out_file = sys.argv[1]
    with open(out_file, 'w') as pcap_file:
        zep_pcap = ZepPcap(pcap_file)

        zep_pcap.write(zep_message)
        zep_pcap.write(zep_message)
        zep_pcap.write(zep_message)
        zep_pcap.write(zep_message)
        zep_pcap.write(zep_message)


if __name__ == '__main__':
    main()
