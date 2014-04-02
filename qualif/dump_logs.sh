#!/bin/bash

logsdir=${1:-faillogs}
cat "$logsdir"/* | cut -f1 -d: | sort | uniq \
| while read node; do
	grep "$node" "$logsdir"/* \
	| sed "s|$logsdir/faillog.||;s/:/ /" \
	| sort -k 1 -n \
	| head -1 
done \
| sort -k 1 -n
