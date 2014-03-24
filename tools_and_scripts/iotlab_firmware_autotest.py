#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Run automated firmwares tests on nodes """

# pylint:disable=I0011,R0904

import os
import logging
import threading
import serial_aggregator

import unittest
import iotlabcli
from iotlabcli import rest
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
    def setUpClass(cls):
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

if __name__ == "__main__":
    unittest.main()
