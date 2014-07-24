#!/bin/bash

site=${site:-grenoble}
arch=${arch:-m3}

m3="m3:at86rf231"
wsn1="wsn430:cc1101"
wsn2="wsn430:cc2420"

targets_json() {
	echo '{ "items": [ '
	target $1
	shift
	for n in $*; do echo ","; target $n; done
	echo "]}"
}

target() {
	node_id=$1
	echo '{ "archi": "'${!arch}'", "site": "'$site'",
		"network_address": "'`node_type`'-'$node_id'" }'
}

node_type() {
	cut -d : -f 1 <<< "${!arch}"
}

is_number() {
	[[ $1 =~ ^[0-9]+$ ]] || false
}

fatal() {
	echo "$@" >&2 ; exit 1
}

usage() {
	echo "usage: `basename $0` <node id> [<node is> ...]"
	echo
	echo "       to specify alternative site or arch (m3|wsn1|wsn2):"
	echo "       site=<site> arch=<arch> ./`basename $0` <node id> ..."
	echo "       site=$site, arch=$arch"
}

case $1 in "" | -h | --help) usage && exit 0 ;; esac

[ ! `node_type` ] && fatal "invalid arch: $arch"
for id in $*; do is_number $id || fatal "invalid node id: $id"; done

ssh $site".iot-lab.info" "
	./serial_aggregator.py 2>&1 <<< '`targets_json "$@"`' &
	cat > /dev/null
	kill %1
"
