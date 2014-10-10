#!/bin/bash

usage() { echo "usage: $0 <site> <node_name> [<node_name> ...]" ; }

case $1 in
	gre)    host=fit-gre; dir=poe_switch ;;
	devgre) host=fit-gre; dir=poe_switch_dev ;;
	roc)    host=dev-roc; dir=poe_switch_roc_new ;;
	""|-h|--help)
		usage
		echo -e "\tsites: " `egrep "host=.*;;$" $0 | sed 's/).*//'`
		exit 0 ;;
	*)
		echo "invalid site: $1" ; exit 1 ;;
esac
shift && [ ! "$1" ] && usage && exit 1

ssh -n $host '
	cd '$dir'
	for node in '$*'; do
		res=`host $node` || { unknown="$unknown $node"; continue; }
		parts=($res)
		ip_list=$ip_list${parts[3]},
		targets="$targets $node"
	done
	[ "$unknown" ] && echo "unknown:$unknown"
	[ "$targets" ] && echo "rebooting:$targets" || exit 0
	./reboot_gateways.py $ip_list > /dev/null
'
