# sourced by run_all.sh

duration=${duration:-1}

submit() {
	node_type=m3
	node_list=$(site=$site ./get_valid_nodes.sh $node_type)
	#firmware=./firmware/serial_echo.elf
	firmware=./firmware/serial_flood.elf
	#profile=profile_test_ftdi2
	experiment-cli submit -d $duration   \
	-l $site,$node_type,$node_list,$firmware,$profile
}
