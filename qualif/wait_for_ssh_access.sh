#!/bin/bash -e

exp_id=$1
if [ ! "$exp_id" ]; then
	echo "usage: `basename $0` <experiment_id>"
	exit 1
fi

NODES_LIST=$(experiment-cli get -i $exp_id -p | ./parse_json.py "
	' '.join([str('node-'+node)
	for node in x['deploymentresults']['0']])")

max_retries=15
nodes=$NODES_LIST
while [ "$nodes" ]; do
	for node in $nodes
	do 
		ssh $node -o ConnectTimeout=5 &>/dev/null \
			date || echo $node > /tmp/$$.failed.$node &
		[ $[ i = (i+1) % 10 ] = 0 ] && sleep 1
	done
	wait
	nodes=$(touch /tmp/$$.failed; cat /tmp/$$.failed*; \rm /tmp/$$.failed*)
	if [ $[--max_retries] = 0 ]; then
		echo "$nodes" | sort -t - -n -k3
		exit 2
	fi
done
