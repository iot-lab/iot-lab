#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Check the given uids jsons files against platform stored ones """

import os
import sys
import json
import logging
import argparse

import iotlabcli
from iotlabcli import experiment
from iotlabcli.parser import common as common_parser
from iotlabcli.helpers import node_url_sort_key

LOGGER = logging.getLogger('check_uids_jsons')
LOGGER.setLevel(logging.DEBUG)


def opts_parser():
    """ Argument parser object """
    parser = argparse.ArgumentParser()
    common_parser.add_auth_arguments(parser)

    parser.add_argument('uids_json_files', nargs='+', help='uids json files')
    parser.add_argument('--outdir', default='.',
                        help='out directory for result files')
    return parser


def oar_uids(api):
    """ Extract nodes uids from oar infos """
    oar_uids_dict = {}
    resources = experiment.info_experiment(api)
    for node in resources['items']:
        uid = node['uid'].lower().strip()
        oar_uids_dict[node['network_address']] = uid

    return oar_uids_dict


def nodes_read_uids(json_files_list):
    """ Extract nodes uids from given json files list """
    nodes_uids_dict = {}
    for json_file_path in json_files_list:
        with open(json_file_path) as json_file:
            nodes_uids = json.load(json_file)
            nodes_uids_dict.update(nodes_uids)

    return nodes_uids_dict


def compare_nodes_uids(old, new):
    """ Return a comparison dict of the two given ones """
    result_dict = {
        'no_data': None,
        'ok': [],
        'outdated': [],
    }

    not_tested = set(old.items())

    # compare
    for node, uid in new.iteritems():
        logging.debug("%s old: %s - new %s", node, uid, old[node])
        if uid == old[node]:
            result_dict['ok'].append((node, uid))
        else:
            result_dict['outdated'].append((node, uid))
        not_tested.remove((node, old[node]))

    result_dict['no_data'] = list(not_tested)

    # sort values
    for nodes in result_dict.values():
        nodes.sort(key=lambda x: node_url_sort_key(x[0]))
    return result_dict


def write_outputs(diff_dict, filename_prefix):
    """ Write result files in files starting with `filename_prefix` """
    for status, nodes in diff_dict.iteritems():
        print "%s: %u" % (status, len(nodes))
        with open("%s_%s.csv" % (filename_prefix, status), 'w') as out_f:
            for node in nodes:
                out_f.write("%s,%s\n" % (node[0], node[1]))


def main():
    """ Check the oar uids using given jsons dicts """

    parser = opts_parser()
    opts = parser.parse_args()
    os.listdir(opts.outdir)  # existing directory

    try:
        username, password = iotlabcli.get_user_credentials(
            opts.username, opts.password)
        api = iotlabcli.Api(username, password)
        server_uids = oar_uids(api)
    except RuntimeError as err:
        sys.stderr.write("%s\n" % err)
        exit(1)

    nodes_uids = nodes_read_uids(opts.uids_json_files)

    nodes_cmp = compare_nodes_uids(server_uids, nodes_uids)
    write_outputs(nodes_cmp, os.path.join(opts.outdir, 'uid_cmp'))


if __name__ == '__main__':
    main()
