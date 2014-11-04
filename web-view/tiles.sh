#!/bin/bash

node_set_name=$1
nodes=$(grep "\"$node_set_name\"" nodes-sets.json | sed 's/.*: "//; s/".*//')
[ ! "$nodes" ] && echo "usage: $0 <node set name>" && exit 1

./aggr.sh $nodes | awk -F '[-;]' '
{ node_id = $3 }
/AccPeak/		{ print node_id, "splash" }
/MagPeak/		{ print node_id, "splash red" }
/Radio .* data=Robot!/ 	{ print node_id, "circle" }
/ping!/		 	{ print node_id, "splash red" }
{ fflush() }
' \
| tee /dev/stderr | ./splash.py --queue-size 100 --max-age 2
