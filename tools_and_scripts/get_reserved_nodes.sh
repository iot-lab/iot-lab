#!/bin/bash

cd "$(dirname "$0")"

if [ "$1" ]; then exp="-i $1"; fi

experiment-cli get $exp -r | ./parse_json.py "
'+'.join(
[ node['network_address'].split('.')[0].split('-')[1]
  for node in x['items']
]
)" 
