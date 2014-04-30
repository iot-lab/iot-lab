#! /bin/bash -e

exp_id=$1

[ ! $exp_id ] && echo "usage: $0 <exp_id>" && false

parse_json="$(dirname "$0")/parse_json.py"

experiment-cli get -i $exp_id -p \
| $parse_json "
	[sys.stdout.write(node + '\n')
	for node in x['deploymentresults']['1']]
	if '1' in x['deploymentresults'] else '' " \
| grep -v -e None -e format
