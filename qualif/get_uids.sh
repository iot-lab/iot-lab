#!/bin/bash -e

res=$(experiment-cli submit \
	-d 3 \
	-l 180,archi=m3:at86rf231+site=devgrenoble,firmware/test_uids.elf
)
exp_id=$(echo "$res" | grep '"id"' | sed 's/.*: //')

./wait_for_exp_state.sh $exp_id "Running"

NODES_LIST=$(./get_deployed_nodes.sh $exp_id | sed 's/\..*//')

max_retries=10
nodes=$NODES_LIST
while [ "$nodes" ]; do
for node in $nodes; do
	ssh $node 2>/dev/null "nc localhost 20000 & sleep 30; kill %%" \
	| grep iotlab_uid -A 1 | tail -n +2 \
	> /tmp/$$.$node || echo $node > /tmp/$$.failed.$node &
	[ $[ i = (i+1) % 10 ] = 0 ] && sleep 1
done
wait
nodes=$(touch /tmp/$$.failed; cat /tmp/$$.failed*; \rm /tmp/$$.failed*)
[ $[--max_retries] = 0 ] && echo "failed to get logs for:" && echo "$nodes" && false
done

for node in $NODES_LIST
do
	echo -n "$node: "
	cat /tmp/$$.$node | tr '\n' ' '
	\rm /tmp/$$.$node
	echo
done
