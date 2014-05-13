#!/bin/bash

[ ! "$*" ] && echo "usage: $0 <node_name> [<node_name> ...]" && exit 1

ssh fit-gre '
	cd poe_switch
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
