#!/bin/bash -e

exp_id=$1
target_state=$2
previous_state=$3

usage() {
	echo "usage: `basename "$0"` <exp_id> <target_state> [<previous state>] (or -h)"
	echo
	echo "state: `egrep '# help$' $0 | sed 's/).*//'`"
}

main() {
	robot_fqdn=`get_robot_fqdn $exp_id`
	while true; do
		state=`get_robot_state` || {
			error "get_robot_state failed"
			return 3
		}
		case $state in
		$target_state)
			return 0
			;;
		$previous_state|'')
			;;
		*)
			error "unexpected state ($state vs. $target_state)"
			return 2
			;;
		esac
		sleep 1
	done
}

get_robot_fqdn() {
	experiment-cli get -r -i $exp_id \
	| ./parse_json.py 'x["items"][0]["network_address"]'
}

get_robot_state() {
	ssh turtlebot@$robot_fqdn -p 2222 '
		tail /var/log/iotlab-ros/turtlebot_debug.log \
		| grep Robot_state: | tail -1 
	' | sed "s/.*: '\|'$//g"
}

error() {
	echo "! $0: $1" >&2
}

check_utils() {
	cd "`dirname "$0"`" # for parse_json.py
	./parse_json.py > /dev/null <<< "{}"
	experiment-cli -h > /dev/null
}

check_state() {
	case $1 in
	DOCKED|IN_DOCK|OUT_DOCK|IN_MOTION|STOP) # help
		;;
	*)
		return 1
		;;
	esac
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
	if ! check_state $target_state; then
		error "invalid target_state: $target_state" && exit 1
	fi
	if [ "$previous_state" ] && ! check_state $previous_state; then
		error "invalid previous_state: $previous_state" && exit 1
	fi
}

init
check_utils
main
