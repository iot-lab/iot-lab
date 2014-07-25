#!/bin/bash

nodes=$*

./aggr.sh $nodes \
| awk -F '[-;]' '
	/Peak/ {
		node_id = $3
		print node_id, ": { style: \"splash\" }"
		fflush()
	}
' \
| while true; do
	while read -t 2 line; do
		state="$state,$line"
	done
	[[ $? > 0 && $? < 128 ]] && exit 1
	echo "{ ${state/,/} }" > user-state.json
	state=
done 
