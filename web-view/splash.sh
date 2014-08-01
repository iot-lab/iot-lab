#!/bin/bash


usage() {
	echo "usage: `basename $0` [-s|--queue-size <queue size>]"\
				  "[-t|--event-timeout <timeout>]"
	echo "
	Feeds user-state.json with 'splash events' as received on stdin.

	Events must come in one per line, as: <node id> [style [style...]]
	Default style is 'splash' when node id is specified alone as input.
	Events land in a queue, are kept for some time, and eventually go away.
	Parameters <queue size> and <timeout> control the aging process.
	"
}

main() {
	queue_size=${queue_size:-5}
	event_timeout=${event_timeout:-0.2}
	parse_args "$@"

	while true; do
		read -t $event_timeout event
		[[ $? > 0 && $? < 128 ]] && break
		queue=`echo -e "$queue\n$event " | tail -$queue_size`
		state=`awk <<< "$queue" '
		$1 == "" { next }
		{	node_id = $1; $1 = ""; style = $0 ? $0 : "splash";
			print node_id ": { style: \"" style "\" },"
		}'`
		echo "{ $state }" > user-state.json
	done
}

parse_args() {
	while [ "$1" ]; do
		case $1 in
		-h|--help) usage && exit 0 ;;
		-s|--queue-size) queue_size=$2 && shift ;;
		-t|--event-timeout) event_timout=$2 && shift ;;
		*) echo "unknown option: $1" >&2 && exit 1 ;;
		esac
		shift
	done
}

main "$@"
