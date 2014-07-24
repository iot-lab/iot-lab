#!/bin/bash

site=${site:-"grenoble"}

targets_json() {
	echo '{ "items": [ '
	target $1
	shift
	for n in $*; do echo ","; target $n; done
	echo "]}"
}

target() {
	node_id=$1
	echo '{ "archi": "m3:at86rf231", "site": "'$site'",
		"network_address": "m3-'$node_id'" }'
}

usage() {
	echo "usage: `basename $0` <node id> [<node is> ...]"
}

case $1 in
	"" | -h | --help)
		usage && exit 0
		;;
esac
ssh $site".iot-lab.info" "
	./serial_aggregator.py 2>&1 <<< '`targets_json "$@"`' &
	read; kill %1
"
