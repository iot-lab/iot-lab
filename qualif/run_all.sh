#!/bin/bash
set -e

nb_runs=${nb_runs:-100}
duration=${duration:-1}
site=${site:-devgrenoble}
faillog_pfx=faillogs/faillog.

main() {
	echo "nb_runs=$nb_runs, duration=$duration, site=$site"
	echo "failure logs go in $faillog_pfx<exp_id>"
	echo "==== starting  @ $(date +'%F %T') ===="
	for i in $(seq $nb_runs); do
		run_test submit_exp
	done
	echo "==== completed @ $(date +'%F %T') ===="
}

submit_exp() {
	node_type=m3
	node_list=$(get_valid_nodes $node_type)
	firmware=./firmware/serial_echo.elf
	firmware=./firmware/serial_flood.elf
	#profile=profile_test_ftdi2
	experiment-cli submit -d $duration   \
	-l $site,$node_type,$node_list,$firmware,$profile
}

run_test() {
	printf "experiment: "
	exp_id=$($1 | get_json "id")
	[ ! $exp_id ] && echo "failed to start" && return 0
	printf "$exp_id, "
	wait_for_exp_state $exp_id "Running" || return 0
	./get_experiment_status.sh $exp_id
	printf "+ dumping logs...\r"
	./get_failed_logs.sh $exp_id > $dir_$faillog_pfx$exp_id
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

dir_="$(pwd)/"
cd "$(dirname "$0")"
check_create_logs_dir
main
