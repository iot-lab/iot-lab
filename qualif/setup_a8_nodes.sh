#! /bin/bash

if [[ $# != 1 ]]
then
    echo "Usage: $0 <experiment_id>"
    echo "       Return the status for open nodes A8 belonging to specified experiment"
    exit 1
fi

cd "$(dirname "$0")"
NODES_LIST=$(experiment-cli get -i $exp_id -p | ./parse_json.py "
	' '.join([str('node-'+node)
	for node in x['deploymentresults']['0']])")
NODES_ARRAY=($NODES_LIST)
scp ./firmware/serial_flood.a8.elf ${NODES_ARRAY[0]}: > /dev/null
for node in $NODES_LIST
do 
    ssh $node 2>/dev/null '
        source /etc/profile;
        ftdi-devices-list -t 2232 | grep -q Description || echo FTDI: No Open Node;
        flash_a8.sh /home/root/serial_flood.a8.elf > /dev/null || echo Flash Firmware failed on m3
	serial_flooder() {
		while true; do cat /dev/mtd2 > /dev/null ; sleep 5; done
	}
	serial_flooder &
    ' > /tmp/$$.$node || echo $node >> /tmp/$$.failed &
    [ $[ i = (i+1) % 10 ] = 0 ] && sleep 1
done
wait

for node in $NODES_LIST
do
	out=$(wc -l /tmp/$$.$node)
	size=${out% *}
        if [[ $size -ne 0 ]]; then
           echo -n "$node: "
           cat /tmp/$$.$node | tr '\n' ' '
           \rm /tmp/$$.$node
           echo
        fi
done
