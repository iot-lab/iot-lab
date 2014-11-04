#!/bin/bash


usage() {
	echo "usage: $0 check|reboot|wait <site> <arch> <nodes>"
	echo
	echo "       <site> : grenoble|lille|rocquencourt|strasbourg|..."
	echo "       <arch> : m3|a8|node-a8"
	echo "       <nodes>: list of node IDs e.g. 1 2 3 5, or 'all'"
}

check_node() {
	case $ARCH in
		m3) check_m3_node ;;
		a8) check_a8_node ;;
		node-a8) check_open_a8 ;;
	esac
}

check_m3_node() {
	ssh -n $fqdn '
	set -ex
	#uname -r | grep -q 3.17.0-rc1592653-hkb || exit 5
	uname -r | grep -q 3.9.6 || exit 5
	grep -m 1 U-Boot /dev/mtd1 | grep -q "Oct 05 2014" || exit 4
	ftdi-devices-list -t 4232 | grep -q ControlNode || exit 3
	ftdi-devices-list | grep -q "Description: M3" || exit 2
	'
}

check_a8_node() {
	ssh -n $fqdn '
	set -ex
	# ftdi-devices-list does not show A8 if no experiment is on
	#uname -r | grep -q 3.17.0-rc1592653-hkb || exit 5
	uname -r | grep -q 3.9.6 || exit 5
	grep -m 1 U-Boot /dev/mtd1 | grep -q "Oct 05 2014" || exit 4
	ftdi-devices-list -t 4232 | grep -q ControlNode || exit 3
	'
}

check_open_a8() {
	ssh -n $fqdn '
	set -ex
	#uname -r | grep -q 3.17.0-rc1592653-hkb || exit 5
	grep -m 1 U-Boot /dev/mtd1 | grep -q "Oct 05 2014" || exit 4
	ftdi-devices-list | grep -q "Description: A8-M3" || exit 2
	'
}

reboot_node() {
	ssh -n $fqdn /sbin/reboot
}

wait_node() {
	max_time=$(date -d "now + ${timeout:-3} min" +%s)
	cmd="ssh -n $fqdn -o ConnectTimeout=5 date &>/dev/null"
	set +x
	while ! $cmd; do
		sleep 1
		[[ $(date +%s) > $max_time ]] && return 2
	done
}

case $1 in
	""|-h|--help)
		usage
		exit 0
		;;
	check|reboot|wait) ;;
	*)
		echo "unknown function: $1"
		exit 1
		;;
esac
case $2 in
	grenoble|devgrenoble) ;;
	lille|devlille) ;;
	rocquencourt) ;;
	strasbourg|devstras) ;;
	*)
		echo "invalid site: $2"
		exit 1
		;;
esac
case $3 in
	m3|a8|node-a8) ;;
	*)
		echo "invalid arch: $3"
		exit 1
		;;
esac
func=$1"_node"
SITE=$2
ARCH=$3
shift 3
NODES=$*

if [ "$NODES" = "all" ]; then
	case $ARCH in
		node-a8) arch=a8 ;;
		a8|m3)   arch=$ARCH ;;
	esac
	NODES=`experiment-cli info -l --site $SITE | grep "$arch-" \
		| sed "s/.*: \"$arch-//; s/\..*//"`
fi
if [[ ! "$NODES" =~ ^[0-9\ ]+$g ]]; then
	echo "invalid nodes list: $NODES"
	exit 1
fi

for n in $NODES; do
	node=$ARCH-$n"."$SITE"."iot-lab.info
	( set -ex; fqdn=$node; $func || ERROR=$? ) &> /tmp/$$.$node &
	[ $[ i = (i+1) % 10 ] = 0 ] && sleep 1
done
wait

if grep -q ERROR /tmp/$$.*; then
	if [[ $ARCH =~ "node-" ]]; then key=3; else key=2; fi
	grep ERROR /tmp/$$.* | sed "s|.*/$$\.||" | sort -k $key -t '-' -n
	grep ERROR -h -B 52 `ls /tmp/$$.* | sort -k $key -t '-' -n` > errors.log
	echo error logs dumped to errors.log >&2
fi
\rm /tmp/$$.*
