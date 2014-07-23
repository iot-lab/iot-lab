# sourced by run_robot.sh

duration=${duration:-5}

submit() {
	node_type=m3
	node_list=381
	firmware=
	profile=Robot_gre_c1
	experiment-cli submit -d $duration   \
	-l $site,$node_type,$node_list,$firmware,$profile
}

setup() {
	# call start_robot API when available
	true
}
