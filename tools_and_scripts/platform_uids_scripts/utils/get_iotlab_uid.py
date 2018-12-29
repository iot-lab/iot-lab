#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Get the iotlab-uip for all experiment nodes """

import sys
import re
import json
import signal

import iotlabaggregator.common
from iotlabaggregator.serial import SerialAggregator


def opts_parser():
    """ Argument parser object """
    import argparse
    parser = argparse.ArgumentParser()
    iotlabaggregator.common.add_nodes_selection_parser(parser)
    return parser


NODES_UID = {}


def handle_uid(identifier, line):
    """ Print one line prefixed by id in format: """
    node_id = re.sub('^node-', '', identifier)  # remove node- from a8 nodes
    url = '%s.%s.iot-lab.info' % (node_id, iotlabaggregator.common.HOSTNAME)

    if url in NODES_UID:
        return
    if 'iotlab_uid' not in line:
        return

    signal.alarm(10)  # watchdog, stop after 10 seconds without messages

    uid = re.sub('.* ', '', line).lower()

    NODES_UID[url] = uid
    sys.stderr.write("%s : %s\n" % (uid, url))


def get_uids(nodes_list):
    """ Get the given nodes uid """
    signal.signal(signal.SIGALRM, (lambda signal, frame: 0))
    signal.signal(signal.SIGALRM, (lambda signal, frame: 0))
    with SerialAggregator(nodes_list, line_handler=handle_uid):
        # as aggr:
        signal.pause()
    return NODES_UID


def main():
    """ Reads nodes from ressource json in stdin and
    aggregate serial links of all nodes
    """
    parser = opts_parser()
    opts = parser.parse_args()
    opts.with_a8 = True

    try:
        nodes_list = SerialAggregator.select_nodes(opts)
        # nodes_list = SerialAggregator.select_nodes(**var(opts))

    except RuntimeError as err:
        sys.stderr.write("%s\n" % err)
        exit(1)

    uids = get_uids(nodes_list)
    print json.dumps(uids, indent=4, sort_keys=True)


if __name__ == "__main__":
    main()
