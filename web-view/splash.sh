#!/bin/bash

main() {
	init
	splash_consumer &
	ticker_producer &
	$producer | tee -a $fifo
}

init() {
	fifo=/tmp/tiles.$$
	trap 'rm $fifo' EXIT
	mkfifo $fifo
}

splash_consumer() {
	while [ -p $fifo ] && read line < $fifo; do
		data=`echo -e "$data\n$line " | tail -$queue_size`
		state=`awk <<< "$data" '
		$1 != "" { print $1 ": { style: \"splash\" }," }'`
		echo "{ $state }" > user-state.json
	done
}

ticker_producer() {
	while [ -p $fifo ]; do
		echo >> $fifo
		sleep 1
	done
}

mock_producer() {
	while true; do
		echo $(( 70 + (RANDOM * 220 >> 15) ))
		sleep $(( RANDOM * 2 >> 15 )).$(( 1 + (RANDOM * 9 >> 15) ))
	done
}

usage() {
	echo "usage: `basename $0` [--mock|-m] [-s|--size <queue size>]"
	echo
	echo "       feeds user-state.json with splash events based on node ids"
	echo "       that come on stdin - or uses random nodes ids with --mock."
	echo
	echo "       events are aged every second and progressively pushed out,"
	echo "       the queue contains at most the last $queue_size events."
}

parse_args() {
	while [ "$1" ]; do
		case $1 in
		-h|--help) usage && exit 0 ;;
		-m|--mock) producer=mock_producer ;;
		-s|--size) queue_size=$2 && shift ;;
		""|--stdin) ;;
		*) echo "unknown option: $1" >&2 && exit 1 ;;
		esac
		shift
	done
}

queue_size=${queue_size:-5}
producer=${producer:-cat}
parse_args "$@"
main
