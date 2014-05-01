#! /bin/bash -e

exp_id=$1

[ ! $exp_id ] && echo "usage: $0 <exp_id>" && false

parse_json="$(dirname "$0")/parse_json.py"

experiment-cli get -i $exp_id -p \
| $parse_json "
	'\n'.join(
	[ node for node in x['deploymentresults']['0']]
	if '0' in x['deploymentresults'] else ''
	)"
