# sourced by run_all.sh

duration=${duration:-7}

submit() {
	node_type=a8
	node_list=$(site=$site ./get_valid_nodes.sh $node_type)
	experiment-cli submit -d $duration   \
	-l $site,$node_type,$node_list
}

setup() {
	log_file=$dir_$faillog_pfx$exp_id
	failed_ssh=/tmp/failed.ssh.$exp_id
	printf "+ waiting for ssh access...       \r"
	./wait_for_ssh_access.sh $exp_id > $failed_ssh || (
		echo "! failed ssh to ok nodes: $(cat $failed_ssh | wc -l)"
		cat $failed_ssh | sed 's/$/: ssh access failed/' >> $log_file
	)
	printf "+ performing a8 open nodes init...\r"
	./setup_a8_nodes.sh $exp_id $failed_ssh $log_file
	\rm -f $failed_ssh
}

cleanup() {
	log_file=$dir_$faillog_pfx$exp_id
	cat $log_file \
	| grep "ssh access failed" | cut -d : -f 1 | sed 's/^node-//' | \
	while read node_fqdn; do
		printf "+ removing failed ssh node $node_fqdn ..."
		ssh fit-master ssh srvoar \
		oarnodesetting -s Dead -h $node_fqdn \
			</dev/null &>/dev/null \
		&& printf "\r" || echo "ERR"
	done
	printf "%*c\r" 70
}
