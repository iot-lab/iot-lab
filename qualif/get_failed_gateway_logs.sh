#! /bin/bash -e

exp_id=$1
if [ ! $exp_id ]
then
    echo "usage: $0 <exp_id>"
    echo "
        Gets first error found in gateway logs
        for nodes belonging to specified exepriment.
        Requires root ssh access to gateways.
    "
    exit 1
fi

cd "$(dirname "$0")"
NODES_LIST=$(./get_failed_nodes.sh $exp_id)

max_retries=20
nodes=$NODES_LIST
while [ "$nodes" ]; do
for node in $nodes
do
    ssh $node 2>/dev/null '
	source /etc/profile;
	cat /var/log/gateway-server/gateway-server.log \
	| grep -e ERROR -B 2 -A 3 | head -n 6 \
	| egrep -e "Flash firmware failed on (gwt|m3)" -e "Open A8 tty not visible"
	ftdi-devices-list -t 4232 | grep -q ControlNode || echo FTDI: No Control Node
	ftdi-devices-list -t 2232 | grep -q Description || echo FTDI: No Open Node
    ' > /tmp/$$.$node || echo $node > /tmp/$$.failed.$node &
    [ $[ i = (i+1) % 10 ] = 0 ] && sleep 1
done
wait
nodes=$(touch /tmp/$$.failed; cat /tmp/$$.failed*; \rm /tmp/$$.failed*)
[ $[--max_retries] = 0 ] && sed 's/$/: failed to fetch gw logs/' <<< "$nodes" && break
done

for node in $NODES_LIST
do
	echo -n "$node: "
	cat /tmp/$$.$node | tr '\n' ' '
	\rm /tmp/$$.$node
	echo
done
