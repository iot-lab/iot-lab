#!/bin/bash

nodes=$*

./aggr.sh $nodes | awk -F '[-;]' '/Peak/ { print $3 }' | ./splash.sh
