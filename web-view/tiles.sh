#!/bin/bash

nodes=$*

./aggr.sh $nodes | awk -F '[-;]' '/Peak/ { print $3; fflush() }' \
| tee /dev/stderr | ./splash.sh --queue-size 10
