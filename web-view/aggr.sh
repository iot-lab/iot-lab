#!/bin/bash

site=${site:-grenoble}
arch=${arch:-m3}


usage() {
	echo "usage: `basename $0` <node id> [<node id> ...]"
	echo
	echo "       runs serial_aggregator on site=$site, arch=$arch"
	echo "       to specify alternative site or arch (m3|wsn430):"
	echo "       site=<site> arch=<arch> ./`basename $0` <node id> ..."
}

main() {
	case $1 in "" | -h | --help) usage && exit 0 ;; esac

	nodes="$@"
	sanity_check $nodes
	ssh $site".iot-lab.info" "
		serial_aggregator -l $site,$arch,${nodes// /+}
	"
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
}


main "$@"
