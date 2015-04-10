#!/bin/bash
set -e

nb_runs=${nb_runs:-10}
site=${site:-devgrenoble}
robot_id=${robot_id:-382}
circuit=
duration=${duration:-5}

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
	exp_id=$(submit | get_exp_id)
	[ ! $exp_id ] && echo "failed to start" && return 0
	printf "$exp_id, "
	./wait_for_exp_state.sh $exp_id "Running" || return 0
	#./get_experiment_status.sh $exp_id
	echo "started"
	printf "+ waiting for experiment $i to end...\r"
	./wait_for_exp_state.sh $exp_id "Terminated" || return 0
	printf "+ waiting for robot to dock...\r"
	./wait_for_robot_state.sh $exp_id "IN_DOCK"
	./wait_for_robot_state.sh $exp_id "DOCKED" "IN_DOCK"
	rest_time=$((duration * 2))
	for t in `seq $rest_time | tac`; do
		printf "+ time left till battery recharged: %2d min\r" $t
		sleep 1m
	done
	printf "%*c\r" 50
}

get_exp_id() {
	./parse_json.py 'x["id"]'
}

submit() {
	node_type=m3
	node_list=$robot_id
	firmware=
	profile=Robot_gre_$circuit
	experiment-cli submit -d $duration   \
	-l $site,$node_type,$node_list,$firmware,$profile
}

case $1 in
	""|-h|--help)
		options=`egrep '# help$' $0 | sed 's/).*//'`
		echo "usage: $(basename "$0") $options"
		;;
	c1|c2|c3) # help
		circuit=$1
		main
		;;
	*)
		echo "unsupported option: $1" && exit 1
		;;
esac
