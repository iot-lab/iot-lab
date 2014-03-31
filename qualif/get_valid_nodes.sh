#! /bin/bash

site=${site:-devgrenoble}

if [[ $# != 1 ]]
then
    echo "Usage: $0 <node_type>"
    echo "       Return the valid nodes for $site of type 'node_type'"
    echo "       To specify as site, use: site=<site> $0 <node_type>"
    exit 1
fi

cd "$(dirname "$0")"
experiment-cli info --site $site -li | ./parse_json.py "x['items'][0]['$site']['$1']['Alive']"
