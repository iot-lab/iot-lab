#!/bin/bash

site=${site:-grenoble}
arch=${arch:-m3}


usage() {
	echo "usage: `basename $0` <node id> [<node id> ...]"
	echo
	echo "       runs serial_aggregator.py on site=$site, arch=$arch"
	echo "       to specify alternative site or arch (m3|wsn1|wsn2):"
	echo "       site=<site> arch=<arch> ./`basename $0` <node id> ..."
}

main() {
	case $1 in "" | -h | --help) usage && exit 0 ;; esac

	sanity_check "$@"

	ssh $site".iot-lab.info" "
		./serial_aggregator.py 2>&1 <<< '`targets_json "$@"`' &
		cat > /dev/null
		kill %1
	"
}

targets_json() {
	for node_id in $*; do
		nodes_spec="$nodes_spec"'
		{ "archi": "'${!arch}'", "site": "'$site'",
		  "network_address": "'$node_type-$node_id'" },'
	done
	echo '{ "items": [ '${nodes_spec%,}' ] }'
}

is_number() {
	[[ $1 =~ ^[0-9]+$ ]] || false
}

fatal() {
	echo "$@" >&2 ; exit 1
}

sanity_check() {
	while [ "$1" ]; do
		is_number $1 || fatal "invalid node id: $1"
		shift
	done
	[ "$node_type" ] || fatal "invalid arch: $arch"
	if ! ssh $site".iot-lab.info" "test -f ./serial_aggregator.py"; then
		fatal "cannot find ./serial_aggregator.py on ssh frontend $site"
	fi
}

m3="m3:at86rf231"
wsn1="wsn430:cc1101"
wsn2="wsn430:cc2420"
node_type=`cut -d : -f 1 <<< "${!arch}"`

main "$@"
