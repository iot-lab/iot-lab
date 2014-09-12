# sourced by run_all.sh

duration=${duration:-10}

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
