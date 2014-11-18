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
# work with new version

import iotlabcli
from iotlabcli import experiment
from iotlabcli.node import node_command

HOSTNAME = os.uname()[1]
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

_RUNNING_EXP = "state=Running&limit=0&offset=0"


class AutomatedIoTLABTests(unittest.TestCase):  # pylint:disable=I0011,R0904
    """ Class wrapping firmwares tests """

    nodes_aggregator = None
    api = None
    exp_id = None

    @classmethod
    def setUpClass(cls):  # pylint:disable=I0011,C0103
        """ unittest.TestCase setUpClass """
        user, passwd = iotlabcli.get_user_credentials()

        cls.api = iotlabcli.Api(user, passwd)
        cls.exp_id = iotlabcli.get_current_experiment(cls.api)

        res_dict = experiment.get_experiment(cls.api, cls.exp_id, 'resources')
        nodes_list = serial_aggregator.extract_nodes(res_dict)

        cls.aggregator = serial_aggregator.NodeAggregator(nodes_list)

    def setUp(self):
        self.state = {}
        self.finished = threading.Event()
        self.aggregator.start()

    def tearDown(self):
        self.aggregator.stop()

    @classmethod
    def nodes_cli(cls, command, nodes_list=(), firmware=None):
        """ Run node-cli on nodes_list """
        return node_command(cls.api, command, cls.exp_id, nodes_list, firmware)
