#! /usr/bin/python
# -*- coding:utf-8 -*-

import unittest
from mock import patch

from iotlabaggregator import common


class TestCommonFunctions(unittest.TestCase):

    @patch('iotlabaggregator.common.experiment.get_experiment')
    def test_get_experiment_nodes(self, get_exp):
        api = None
        # Already terminated experiment
        self.assertEqual([], common.get_experiment_nodes(api, exp_id=None))

        resources = {"items": [
            {'network_address': 'm3-1.grenoble.iot-lab.info',
             'site': 'grenoble'},
            {'network_address': 'wsn430-1.lille.iot-lab.info',
             'site': 'lille'},
            {'network_address': 'a8-1.strasbourg.iot-lab.info',
             'site': 'strasbourg'},
            {'network_address': 'wsn430-4.grenoble.iot-lab.info',
             'site': 'grenoble'},
            {'network_address': 'a8-1.grenoble.iot-lab.info',
             'site': 'grenoble'},
        ]}

        # Already terminated experiment
        get_exp.side_effect = (
            lambda a, e, req: {'state': {'state': 'Running'},
                               'resources': resources}[req])
        self.assertEqual(['m3-1', 'wsn430-4', 'a8-1'],
                         common.get_experiment_nodes(api, 123, 'grenoble'))
        get_exp.side_effect = None

        # Already terminated experiment
        get_exp.return_value = {'state': 'Terminated'}
        self.assertRaises(RuntimeError, common.get_experiment_nodes, api, 123)

    @patch('iotlabcli.get_current_experiment')
    @patch('iotlabaggregator.common.get_experiment_nodes')
    def test_query_nodes(self, get_exp_nodes, get_cur_exp):
        api = None
        get_exp_nodes.side_effect = (
            lambda a, exp, h: {
                123: ['m3-3'], 234: ['a8-1', 'm3-2'], None: []}[exp])
        get_cur_exp.return_value = 234

        # no parameters, use dynamic exp_id
        ret = common.query_nodes(api)
        self.assertEqual(['a8-1', 'm3-2'], ret)

        # exp_id
        ret = common.query_nodes(api, exp_id=123)
        self.assertEqual(['m3-3'], ret)

        # nodes_list_list
        ret = common.query_nodes(api, nodes_list_list=[
            ['m3-1.grenoble.iot-lab.info'],
            ['a8-10.grenoble.iot-lab.info']], hostname='grenoble')
        self.assertEqual(['a8-10', 'm3-1'], ret)

        # exp_id and nodes_list_list
        ret = common.query_nodes(api, exp_id=123, nodes_list_list=[
            ['m3-1.grenoble.iot-lab.info'],
            ['a8-10.grenoble.iot-lab.info']], hostname='grenoble')
        self.assertEqual(['a8-10', 'm3-1', 'm3-3'], ret)

    @patch('iotlabcli.get_user_credentials')
    @patch('iotlabcli.Api')
    @patch('iotlabaggregator.common.query_nodes')
    def test_get_nodes_selection(self, query_nodes, api, get_user):
        get_user.return_value = ('user', 'password')
        query_nodes.return_value = ['a8-1', 'm3-1']

        ret = common.get_nodes_selection(username=None, password=None,
                                         experiment_id=None, nodes_list=())
        self.assertEqual(['a8-1', 'm3-1'], ret)
        query_nodes.assert_called_with(api.return_value, None, ())
