#!/bin/bash


usage() {
	echo "usage: `basename $0` [-s|--queue-size <queue size>]"\
				  "[-t|--event-timeout <timeout>]"
	echo "
	Feeds user-state.json with 'splash events' based on the node IDs
	that are coming on stdin.  Events are kept in a queue, aged, and
	in time get discarded from the queue.  Parameters <queue size>
	and <timeout> control the process.
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
		$1 != "" { print $1 ": { style: \"splash\" }," }'`
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
