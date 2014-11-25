#! /usr/bin/python
# -*- coding: utf-8 -*-
#  http://www.codeproject.com/Tips/612847/Generate-a-quick-and-easy-custom-pcap-file-using-P

import sys
import binascii

pcap_global_header = (
    'D4 C3 B2 A1'
    '02 00'         #File format major revision (i.e. pcap <2>.4)
    '04 00'         #File format minor revision (i.e. pcap 2.<4>)
    '00 00 00 00'
    '00 00 00 00'
    'FF FF 00 00'
    '01 00 00 00'
)

# pcap packet header that must preface every packet
pcap_packet_header = (
    'AA 77 9F 47'  # timestamp seconds  # TODO
    '90 A2 04 00'  # timestamps microseconds TODO
    'XX XX XX XX'  # Frame size (little endian) // number of octets in file
    'YY YY YY YY'  # Frame size (little endian) // real size not truncated
)

eth_header = (
    '00 00 00 00 00 00'  # Source Mac
    '00 00 00 00 00 00'  # Dest Mac
    '08 00'              # Protocol (0x0800 = IP)
)

ip_header = (
    '45'           # IP version and healer length (multiples of 4 bytes)
    '00'
    'XX XX'        # Length - Will be calculated and replaced later
    '00 00'
    '40 00 40'
    '11'           # Protocol (0x11 = UDP)
    'YY YY'        # Checksum - Will be calculated and replaced later
    '7F 00 00 01'  # Source IP (Default: 127.0.0.1)
    '7F 00 00 01'  # Dest IP   (Default: 127.0.0.1)
)

udp_header = (
    '80 01'
    '45 5a'  # Port: ZepPort 17754 in hexa
    'YY YY'  # Length - Will be calculated and replaced later
    '00 00'
)

def get_byte_len(byte_str):
    return len(''.join(byte_str.split())) / 2

def generatePCAP(zep_message):

    udp_len = len(zep_message) + get_byte_len(udp_header)
    udp = udp_header.replace('YY YY', '%04x' % udp_len)

    ip_len = udp_len + get_byte_len(ip_header)
    ip = ip_header.replace('XX XX', '%04x' % ip_len)
    checksum = ip_checksum(ip.replace('YY YY', '00 00'))
    ip = ip.replace('YY YY', "%04x" % checksum)

    pcap_len = ip_len + get_byte_len(eth_header)
    hex_str = "%08x" % pcap_len
    # TODO check this with endiannes
    reverse_hex_str = hex_str[6:] + hex_str[4:6] + hex_str[2:4] + hex_str[:2]
    pcap_h = pcap_packet_header.replace('XX XX XX XX', reverse_hex_str)
    pcap_h = pcap_h.replace('YY YY YY YY', reverse_hex_str)

    bytestring = to_bin(pcap_h + eth_header + ip + udp) + zep_message
    return bytestring




#Splits the string into a list of tokens every n characters
def splitN(str1,n):
        return [str1[start:start+n] for start in range(0, len(str1), n)]

#Calculates and returns the IP checksum based on the given IP Header
def ip_checksum(iph):
    #split into bytes
    words = splitN(''.join(iph.split()),4)
    csum = 0;
    for word in words:
        csum += int(word, base=16)
    csum += (csum >> 16)
    csum = csum & 0xFFFF ^ 0xFFFF

    return csum

def to_bin(byte_string):
    # Remove all whitespaces and return binary
    return binascii.a2b_hex(''.join(byte_string.split()))


MESSAGE =  (
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

pcap_hdr = to_bin(pcap_global_header)
pcap_msg = generatePCAP(to_bin(MESSAGE))

try:
    out_file = sys.argv[1]
    with open(out_file, 'w') as pcap_file:
        pcap_file.write(pcap_hdr)
        pcap_file.write(pcap_msg)
except IndexError:
    out = binascii.b2a_hex(pcap_hdr)
    out += binascii.b2a_hex(pcap_msg)
    print  out

