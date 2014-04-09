#!/bin/bash
set -e

nb_runs=${nb_runs:-100}
site=${site:-devgrenoble}
faillog_pfx=faillogs/faillog.

run_all_m3() {
	duration=${duration:-1}
	run_all submit_exp_m3
}

run_all_a8() {
	duration=${duration:-5}
	run_all submit_exp_a8
}

main() {
	echo "nb_runs=$nb_runs, duration=$duration, site=$site"
	echo "failure logs go in $faillog_pfx<exp_id>"
	echo "==== starting  @ $(date +'%F %T') ===="
	for i in $(seq $nb_runs); do
		run_test $1
	done
	echo "==== completed @ $(date +'%F %T') ===="
}

submit_exp_m3() {
	node_list=$(get_valid_nodes $node_type)
	#firmware=./firmware/serial_echo.elf
	firmware=./firmware/serial_flood.elf
	#profile=profile_test_ftdi2
	experiment-cli submit -d $duration   \
	-l $site,$node_type,$node_list,$firmware,$profile
}

submit_exp_a8() {
	node_list=$(get_valid_nodes $node_type)
	experiment-cli submit -d $duration   \
	-l $site,$node_type,$node_list
}

run_test() {
	printf "experiment: "
	exp_id=$($1 | get_json "id")
	[ ! $exp_id ] && echo "failed to start" && return 0
	printf "$exp_id, "
	wait_for_exp_state $exp_id "Running" || return 0
	./get_experiment_status.sh $exp_id
	printf "+ dumping gateway logs...\r"
	./get_failed_gateway_logs.sh $exp_id > $dir_$faillog_pfx$exp_id
	printf "+ running node-specific setup...\r"
	${node_type}_setup
	printf "+ waiting for experiment $i to end...\r"
	wait_for_exp_state $exp_id "Terminated" || return 0
	printf "%*c\r" 50
}

wait_for_exp_state() {
	while [ "$(get_exp_state $1)" != '"'$2'"' ]; do
		if [ "$(get_exp_state $1)" = '"Error"' ]; then
			echo "! error while waiting for experiment $1 / $2"
			return 1
		fi
		sleep 1
	done
}

m3_setup() {
	true
}

a8_setup() {
	printf "+ waiting for ssh access...\r"
	./wait_for_ssh_access.sh $exp_id
	printf "+ performing a8 open nodes init...\r"
	./setup_a8_nodes.sh $exp_id >> $dir_$faillog_pfx$exp_id
}

check_create_logs_dir() {
	logs_dir=$(dirname "$dir_$faillog_pfx")
	if [ ! -d "$logs_dir" ]; then
		echo creating $logs_dir
		mkdir -p "$logs_dir"
	fi
}

get_valid_nodes() {
	site=$site ./get_valid_nodes.sh $1
}

get_exp_state() {
	experiment-cli get -i $1 -s | get_json "state" || true
}

get_json() {
	grep '"'$1'":' | awk '{print $2}'
}

setup() {
	dir_="$(pwd)/"
	cd "$(dirname "$0")"
	check_create_logs_dir
}

run_all() {
	setup
	main $1
}

case $1 in
	""|-h|--help)
		echo "usage: $(basename "$0") m3|a8"
		;;
	m3|a8)
		node_type=$1
		run_all_$1
		;;
	*)
		echo "unsupported option: $1" && exit 1
		;;
esac
