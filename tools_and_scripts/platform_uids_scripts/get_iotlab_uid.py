#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Get the iotlab-uip for all experiment nodes """

import sys
import re
import json
import signal

import serial_aggregator
import iotlabcli
from iotlabcli import experiment
from iotlabcli.parser import common as common_parser
from iotlabcli.parser import node as node_parser

def opts_parser():
    """ Argument parser object """
    import argparse
    parser = argparse.ArgumentParser()
    common_parser.add_auth_arguments(parser)

    nodes_group = parser.add_argument_group(
        description="By default, select currently running experiment nodes",
        title="Nodes selection")

    nodes_group.add_argument('-i', '--id', dest='experiment_id', type=int,
                             help='experiment id submission')

    nodes_group.add_argument(
        '-l', '--list', type=node_parser.nodes_list_from_str,
        dest='nodes_list', help='nodes list, may be given multiple times')

    return parser


NODES_UID = {}
def handle_uid(identifier, line):
    """ Print one line prefixed by id in format: """
    url = re.sub('node-', '', identifier)  # remove node- from a8 nodes
    url += '.%s.iot-lab.info' % serial_aggregator.HOSTNAME

    if url in NODES_UID:
        return
    if 'iotlab_uid' not in line:
        return

    signal.alarm(10)  # watchdog, stop after 10 seconds without messages

    uid = re.sub('.* ', '', line)

    NODES_UID[url] = uid
    sys.stderr.write("%s : %s\n" % (uid, url))

def main():
    """ Reads nodes from ressource json in stdin and
    aggregate serial links of all nodes
    """
    parser = opts_parser()
    opts = parser.parse_args()

    try:
        username, password = iotlabcli.get_user_credentials(
            opts.username, opts.password)
        api = iotlabcli.Api(username, password)
        nodes_list = serial_aggregator.get_nodes(
            api, opts.experiment_id, opts.nodes_list, with_a8=True)
    except RuntimeError as err:
        sys.stderr.write("%s\n" % err)
        exit(1)


    aggregator = serial_aggregator.NodeAggregator(
        nodes_list, print_lines=False, line_handler=handle_uid)
    aggregator.start()
    try:
        signal.signal(signal.SIGALRM, (lambda signal, frame: 0))
        signal.signal(signal.SIGINT, (lambda signal, frame: 0))
        signal.pause()
        sys.stderr.write("Closing connections\n")
    finally:
        aggregator.stop()

    print json.dumps(NODES_UID, indent=4, sort_keys=True)


if __name__ == "__main__":
    main()
