#! /usr/bin/python
# -*- coding:utf-8 -*-


import unittest
import mock

from iotlabaggregator import sniffer


import binascii
ZEP_MESSAGE = binascii.a2b_hex(''.join((
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


class TestSniffer(unittest.TestCase):

    def test_data_handler_simple(self):
        msg_handler = mock.Mock()

        def recv(_):
            return ZEP_MESSAGE

        sniff = sniffer.SnifferConnection('m3-1', msg_handler)
        sniff.recv = mock.Mock(side_effect=recv)

        sniff.handle_read()
        sniff.handle_read()

        msg_handler.assert_called_with(ZEP_MESSAGE)

    def test_data_handler_invalid_start(self):
        msg_handler = mock.Mock()

        def recv(_):
            return 'invalid_data' + ZEP_MESSAGE

        sniff = sniffer.SnifferConnection('m3-1', msg_handler)
        sniff.recv = mock.Mock(side_effect=recv)

        sniff.handle_read()
        sniff.handle_read()

        msg_handler.assert_called_with(ZEP_MESSAGE)
        self.assertEqual(2, msg_handler.call_count)

    def test_data_handler_one_char_at_a_time(self):
        msg_handler = mock.Mock()
        msg = list(ZEP_MESSAGE)

        def recv(_):
            return msg.pop(0)

        sniff = sniffer.SnifferConnection('m3-1', msg_handler)
        sniff.recv = mock.Mock(side_effect=recv)

        while msg:
            sniff.handle_read()

    def test_many_values(self):
        for i in range(1, 100):
            print i
            self._test_data_handler_n_char_at_a_time(i)

    def _test_data_handler_n_char_at_a_time(self, num_chars):
        msg_handler = mock.Mock()

        msg = list(ZEP_MESSAGE * 10)

        def recv(_):
            ret = msg[0:num_chars]
            del(msg[0:num_chars])
            return ''.join(ret)

        sniff = sniffer.SnifferConnection('m3-1', msg_handler)
        sniff.recv = mock.Mock(side_effect=recv)

        while msg:
            sniff.handle_read()

        msg_handler.assert_called_with(ZEP_MESSAGE)
        self.assertEqual(10, msg_handler.call_count)
