#! /usr/bin/python
# -*- coding:utf-8 -*-

# pylint:disable=missing-docstring

import unittest
from mock import patch, Mock

from iotlabaggregator import sniffer


class TestSnifferHandleRead(unittest.TestCase):
    """ Test the packet reading code """
    import binascii
    zep_message = binascii.a2b_hex(''.join((
        '45 58 02 01'   # Base Zep header
        '0B 00 01 00 ff'   # chan | dev_id | dev_id| LQI/CRC_MODE |  LQI
        '00 00 00 00'   # Timestamp msb
        '00 00 00 00'   # timestamp lsp

        '00 00 00 01'   # seqno

        '00 01 02 03'   # reserved 0-3/10
        '04 05 06 07'   # reserved 4-7/10
        '08 09'         # reserved 8-9 / 10
        '08'            # Length 2 + data_len
        '61 62 63'      # Data
        '41 42 43'      # Data
        'FF FF'         # CRC)
    ).split()))

    def setUp(self):
        self.outfd = Mock()

    def tearDown(self):
        patch.stopall()

    def test_simple(self):

        def recv(_):
            return self.zep_message

        sniff = sniffer.SnifferConnection('m3-1', self.outfd.write)
        sniff.recv = Mock(side_effect=recv)
        sniff.handle_read()
        sniff.handle_read()
        self.outfd.write.assert_called_with(self.zep_message)

    def test_invalid_data_start(self):
        def recv(_):
            return 'invaEEEXlidE_data' + self.zep_message

        sniff = sniffer.SnifferConnection('m3-1', self.outfd.write)
        sniff.recv = Mock(side_effect=recv)

        sniff.handle_read()
        sniff.handle_read()

        self.assertEqual(2, self.outfd.write.call_count)
        self.outfd.write.assert_called_with(self.zep_message)

    def test_read_ret_values(self):
        for i in range(1, 100):
            self.outfd.reset_mock()
            print i
            self.read_return_n_char_per_call(i)

    def read_return_n_char_per_call(self, num_chars):
        msg = list(self.zep_message * 10)

        def recv(_):
            ret = msg[0:num_chars]
            del msg[0:num_chars]
            return ''.join(ret)

        sniff = sniffer.SnifferConnection('m3-1', self.outfd.write)
        sniff.recv = Mock(side_effect=recv)

        while msg:
            sniff.handle_read()
        self.assertEqual(10, self.outfd.write.call_count)
        self.outfd.write.assert_called_with(self.zep_message)
