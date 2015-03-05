#! /usr/bin/env python
# -*- coding: utf-8 -*-


""" Update the iot-lab resources using the updated uids

input: uid_cmp_node_outdated

Can also use inputs:

    uid_cmp_node_ok  or uid_cmp_no_data

to check that the resources are up to date


resources-dir 'install-lib/resources'
"""


import os
import csv
import shutil
import argparse


def fmt_input_data(in_list):
    """
    Extract infos from input list
    (site, archi, num, uid)


    >>> fmt_input_data(['wsn430-56.euratech.iot-lab.info', 'b2f6'])
    ('euratech', 'wsn430', '56', 'b2f6')

    >>> fmt_input_data(['a8-223.grenoble.iot-lab.info', 'a061'])
    ('grenoble', 'a8', '223', 'a061')

    >>> fmt_input_data(['m3-362.grenoble.iot-lab.info', '2654'])
    ('grenoble', 'm3', '362', '2654')
    """
    assert len(in_list) == 2
    node_id, site = in_list[0].split('.')[0:2]
    archi, num = node_id.split('-')
    return site, archi, num, in_list[1]


def read_input_file(csv_in):
    """


    Input file

    wsn430-56.euratech.iot-lab.info,b2f6
    wsn430-64.euratech.iot-lab.info,bf1c
    a8-223.grenoble.iot-lab.info,a061
    m3-27.grenoble.iot-lab.info,b376
    m3-28.grenoble.iot-lab.info,a772
    m3-362.grenoble.iot-lab.info,2654

    output dict

    {
        ('grenoble', 'm3'): {'362': '2654', '28': 'a772'},
        ('euratech', 'wsn430'): {'56': 'b2f6', '64': 'bf1c'},
    }
    """
    input_dict = {}
    with open(csv_in) as in_file:
        reader = csv.reader(in_file, delimiter=',')
        for data in reader:
            site, archi, num, node_uid = fmt_input_data(data)
            input_dict.setdefault((site, archi), {})[num] = node_uid
    return input_dict


def update_csv_row(row, uid_dict):
    """ Update the row with the new uid """
    node_num = row[0]

    try:
        old = row[2]
        new = uid_dict[node_num]
        if old != new:
            print '%s %s: %r -> %r' % (node_num, row[1], old, new)
            row[2] = new
    except KeyError:
        pass

    return row


def update_csv_file(csv_fd, new_csv_fd, uid_dict):
    """ Update the csv_fd to new_csv_fd using uid_dict """
    reader = csv.reader(csv_fd, delimiter=',')
    writer = csv.writer(new_csv_fd, delimiter=',', lineterminator='\n')
    print "Update %s:" % csv_fd.name
    for row in reader:
        row = update_csv_row(row, uid_dict)
        writer.writerow(row)


PARSER = argparse.ArgumentParser()
PARSER.add_argument('-r', '--resources-dir', required=True, help='input files')
PARSER.add_argument('input_file', nargs='+', help='input files')


def main():
    """ Update the fit-dev/install-lib/resources csv files using the
    'uid_cmd_*' csv files passed as input """
    opts = PARSER.parse_args()

    # Read input files
    in_dict = {}
    for in_file in opts.input_file:
        in_dict.update(read_input_file(in_file))

    for (site, archi), uid_dict in in_dict.iteritems():
        csv_file = os.path.join(opts.resources_dir, site, archi + '.csv')
        new_csv_file = csv_file + '.new'
        with open(csv_file, 'rb') as csv_fd:
            with open(new_csv_file, 'w') as new_csv_fd:
                update_csv_file(csv_fd, new_csv_fd, uid_dict)
        shutil.move(new_csv_file, csv_file)


if __name__ == '__main__':
    main()
