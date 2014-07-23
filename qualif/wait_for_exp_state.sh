#!/bin/bash -e

exp_id=$1
target_state=$2

usage() {
	echo "usage: `basename "$0"` <exp_id> <target_state> (or -h)"
	echo
	echo "state: `egrep '# help$' $0 | sed 's/).*//'`"
}

main() {
	while true; do
		state=`get_exp_state` || {
			error "get_exp_state failed"
			return 3
		}
		case $state in
		$target_state)
			return 0
			;;
		Error|Terminated)
			error "unexpected state ($state vs. $target_state)"
			return 2
			;;
		esac
		sleep 1
	done
}

get_exp_state() {
	experiment-cli get -i $exp_id -s \
	| ./parse_json.py "x['state']" 2> /dev/null
}

error() {
	echo "! wait_for_exp_state: $1" >&2
}

shopt -s extglob
init() {
	case $exp_id in
	""|-h|--help)
		usage && exit 0
		;;
	+([0-9]))
		;;
	*)
		error "invalid exp_id: $exp_id" && return 1
		;;
	esac
	case $target_state in
	"")
		usage && return 1
		;;
	Running|Terminated|Launching|Waiting|Error) # help
		;;
	*)
		error "invalid target_state: $target_state" && return 1
		;;
	esac
	cd "`dirname "$0"`" # for parse_json.py
	./parse_json.py > /dev/null <<< "{}"
	experiment-cli -h > /dev/null
}

init
main
