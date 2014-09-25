#!/bin/bash -e

exp_id=$1
if [ ! "$exp_id" ]; then
	echo "usage: `basename $0` <experiment_id>"
	exit 1
fi

NODES_LIST=$(experiment-cli get -i $exp_id -p | ./parse_json.py "
	' '.join([str('node-'+node)
	for node in x['deploymentresults']['0']])")

tmpfiles=/tmp/$$.failed
trap "rm -f $tmpfiles.*" EXIT

max_time=$(date -d "now + 10 min" +%s)
nodes=$NODES_LIST
while [ "$nodes" ]; do
	for node in $nodes
	do 
		ssh $node -o ConnectTimeout=5 &>/dev/null \
			date || echo $node > $tmpfiles.$node &
		[ $[ i = (i+1) % 10 ] = 0 ] && sleep 1
	done
	wait
	nodes=$(touch $tmpfiles; cat $tmpfiles*; \rm $tmpfiles*)
	if [[ $(date +%s) > $max_time ]]; then
		echo "$nodes" | sort -t - -n -k3
		exit 2
	fi
done
