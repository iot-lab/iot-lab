#! /bin/bash

if [[ $# != 1 ]]
then
    echo "Usage: $0 <experiment_id>"
    echo "       Return the status for nodes belonging to specified experiment"
    exit 1
fi

cd "$(dirname "$0")"
experiment-cli get -i $1 -p  \
| ./parse_json.py "[len(nodes) for nodes in x['deploymentresults'].values()]" \
| tr -d '][,' \
| awk '{print "ok: " $2 ", failed: " $1 ", total: " $1+$2}'
