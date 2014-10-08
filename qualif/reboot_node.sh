#!/bin/bash

[ ! "$*" ] && echo "usage: $0 <node_name> [<node_name> ...]" && exit 1

# use: ssh fit-gre / cd poe_switch_dev         for dev-gre (dev)
# use: ssh fit-gre / cd poe_switch             for fit-gre (prod)
# use: ssh dev-roc / cd poe_switch_roc_new     for dev-roc (dev)

ssh fit-gre '
	cd poe_switch_dev
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
