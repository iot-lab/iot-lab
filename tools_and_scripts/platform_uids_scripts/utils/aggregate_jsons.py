#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Aggregate multiple json dicts into one

Last given file updates value at last
"""


import argparse
import json

PARSER = argparse.ArgumentParser()
PARSER.add_argument('input_file', nargs='+', help='input json dicts')
PARSER.add_argument('-o', '--out-file', required=True, help='output json')


def main():
    """ Aggregate all inputs to output """
    opts = PARSER.parse_args()
    # Read input files
    out_dict = {}
    for in_file in opts.input_file:
        with open(in_file) as in_fd:
            print "Using %s" % in_fd.name
            out_dict.update(json.load(in_fd))

    with open(opts.out_file, 'w') as out_fd:
        out_fd.write(json.dumps(out_dict, indent=4, sort_keys=True))


if __name__ == '__main__':
    main()
