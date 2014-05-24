#!/bin/bash

cd "$(dirname "$0")"

if [ "$1" ]; then exp="-i $1"; fi

experiment-cli get $exp -p | ./parse_json.py "
'+'.join(
[ node.split('.')[0].split('-')[1]
  for node in x['deploymentresults']['0']
]
if '0' in x['deploymentresults'] else ''
)" 
