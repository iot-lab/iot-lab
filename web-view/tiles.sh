#!/bin/bash

node_set_name=$1
nodes=$(grep "\"$node_set_name\"" nodes-sets.json | sed 's/.*: "//; s/".*//')
[ ! "$nodes" ] && echo "usage: $0 <node set name>" && exit 1

./aggr.sh $nodes | awk -F '[-;]' '
/AccPeak/ { print $3, "splash"; fflush() }
/MagPeak/ { print $3, "circle"; fflush() }
' \
| tee /dev/stderr | ./splash.sh --queue-size 10
