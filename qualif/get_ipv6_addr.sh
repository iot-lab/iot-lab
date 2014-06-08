#!/bin/bash -e

if [ "`hostname -a`" != "srvssh" ]; then
	echo "please run me on a ssh-frontend"
	exit 1
fi

cd "$(dirname "$0")"

site=`hostname`
all_m3=$(site=$site ./get_valid_nodes.sh m3)
firmware="firmware/print-ipv6-addr.iotlab-m3"

exp=$(experiment-cli submit -d 1 -l $site,m3,$all_m3,$firmware \
	| grep '"id"' | sed 's/.*: //')

./wait_for_exp_state.sh $exp Running

nodes=$(./get_deployed_nodes.sh $exp)

for node in $nodes; do 
	nc $node 20000 | grep -m 1 :: > /tmp/$$.$node &
done
wait
echo -n > $site.ipv6.txt
for node in $nodes; do
	echo $node `cat /tmp/$$.$node` >> $site.ipv6.txt
	/bin/rm /tmp/$$.$node
done
cat $site.ipv6.txt
