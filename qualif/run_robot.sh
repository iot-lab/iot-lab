#!/bin/bash
set -e

nb_runs=${nb_runs:-100}
site=${site:-devgrenoble}

main() {
	echo "nb_runs=$nb_runs, duration=$duration, site=$site"
	echo "==== starting  @ $(date +'%F %T') ===="
	for i in $(seq $nb_runs); do
		run_test
	done
	echo "==== completed @ $(date +'%F %T') ===="
}

run_test() {
	printf "experiment: "
	exp_id=$(submit | get_exp_id) # submit defined in sourced exp_*.sh
	[ ! $exp_id ] && echo "failed to start" && return 0
	printf "$exp_id, "
	./wait_for_exp_state.sh $exp_id "Running" || return 0
	#./get_experiment_status.sh $exp_id
	echo "started"
	printf "+ running specific setup...\r"
	setup # defined in sourced exp_*.sh
	printf "+ waiting for experiment $i to end...\r"
	./wait_for_exp_state.sh $exp_id "Terminated" || return 0
	printf "+ waiting for robot to dock...\r"
	#mock_docking &
	./wait_for_robot_state.sh $exp_id "IN_DOCK"
	./wait_for_robot_state.sh $exp_id "DOCKED" "IN_DOCK"
	rest_time=$((duration * 2))
	for t in `seq $rest_time | tac`; do
		printf "+ time left till battery recharged: %2d min\r" $t
		sleep 1m
	done
	printf "%*c\r" 50
}

mock_docking() {
	sleep 5
	ssh turtlebot@m3-381.devgrenoble.iot-lab.info "
		echo \"Robot_state: 'DOCKED'\" \
			>> /var/log/iotlab-ros/turtlebot_debug.log
	"
}

get_exp_id() {
	./parse_json.py 'x["id"]'
}

init() {
	true
}

case $1 in
	""|-h|--help)
		options=`egrep '# help$' $0 | sed 's/).*//'`
		echo "usage: $(basename "$0") $options"
		;;
	c1|c2|c3) # help
		source "exp_robot_$1".sh
		init
		main
		;;
	*)
		echo "unsupported option: $1" && exit 1
		;;
esac
