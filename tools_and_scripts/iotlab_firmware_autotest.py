#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Run automated firmwares tests on nodes """

# pylint:disable=I0011,R0904

import os
import logging
import threading
import serial_aggregator
import sys

import unittest

# relative import from iotlabcli
CUR_DIR = os.path.realpath(os.path.dirname(__file__))
sys.path.append(CUR_DIR + '/../parts/cli-tools/')
import iotlabcli
from iotlabcli import rest
import iotlabcli.node_parser

import json

HOSTNAME = os.uname()[1]
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

_RUNNING_EXP = "state=Running&limit=0&offset=0"


class AutomatedIoTLABTests(unittest.TestCase):  # pylint:disable=I0011,R0904
    """ Class wrapping firmwares tests """

    nodes_aggregator = None
    request = None
    exp_id = None

    @classmethod
    def setUpClass(cls):  # pylint:disable=I0011,C0103
        """ unittest.TestCase setUpClass """
        cls.request = rest.Api()

        cls.exp_id = iotlabcli.helpers.check_experiments_running(
            json.loads(cls.request.get_experiments(_RUNNING_EXP)), parser=None)

        ressources = cls.request.get_experiment_resources(cls.exp_id)
        json_dict = serial_aggregator.extract_json(ressources)
        nodes_list = serial_aggregator.extract_nodes(json_dict, HOSTNAME)

        cls.nodes_aggregator = serial_aggregator.NodeAggregator(nodes_list)

    def setUp(self):
        self.state = {}
        self.finished = threading.Event()
        self.nodes = type(self).nodes_aggregator
        self.nodes.start()

    def tearDown(self):
        self.nodes.stop()

    @staticmethod
    def nodes_cli(command, nodes_list=None, firmware=None):
        """ Run node-cli on nodes_list """
        if command not in ['--reset', '--update']:
            raise ValueError
        _cmd_list = HOSTNAME + ',{node_type},{nodes}'

        nodes_list = nodes_list or []
        fw_args = []
        if firmware is not None:
            fw_args.append(firmware)

        cmd_list = []

        _split = [node.split('-') for node in nodes_list]
        nodes_m3 = '+'.join([num for archi, num in _split if archi == 'm3'])

        if nodes_m3:
            cmd_list.append('--list')
            cmd_list.append(_cmd_list.format(
                node_type='m3', nodes='+'.join(nodes_m3)))

        arguments = cmd_list + [command] + fw_args

        iotlabcli.node_parser.main(arguments)
