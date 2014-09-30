#!/bin/bash
set -e

nb_runs=${nb_runs:-100}
site=${site:-devgrenoble}
faillog_pfx=faillogs.$site/faillog.

source source.me

main() {
	echo "nb_runs=$nb_runs, duration=$duration, site=$site"
	echo "failure logs go in $faillog_pfx<exp_id>"
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
	./get_experiment_status.sh $exp_id
	printf "+ dumping gateway logs...\r"
	./get_failed_gateway_logs.sh $exp_id > $dir_$faillog_pfx$exp_id || true
	printf "+ running specific setup...\r"
	setup
	printf "+ waiting for experiment $i to end...\r"
	./wait_for_exp_state.sh $exp_id "Terminated" || return 0
	printf "+ performing cleanup ...\r"
	cleanup
	printf "%*c\r" 50
}

check_create_logs_dir() {
	logs_dir=$(dirname "$dir_$faillog_pfx")
	if [ ! -d "$logs_dir" ]; then
		echo creating $logs_dir
		mkdir -p "$logs_dir"
	fi
}

get_exp_id() {
	./parse_json.py 'x["id"]'
}

init() {
	dir_="$(pwd)/"
	cd "$(dirname "$0")"
	check_create_logs_dir
}

# the following functions are overriden in sourced exp_*.sh

submit() { :; }
setup() { :; }
cleanup() { :; }

case $1 in
	""|-h|--help)
		options=`egrep '# help$' $0 | sed 's/).*//'`
		echo "usage: $(basename "$0") $options"
		;;
	m3|a8) # help
		source "exp_$1".sh
		init
		main
		;;
	*)
		echo "unsupported option: $1" && exit 1
		;;
esac
