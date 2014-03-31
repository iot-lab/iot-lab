#!/bin/bash

cat faillogs/* | cut -f1 -d: | sort | uniq \
| while read node; do
	grep "$node" faillogs/* \
	| sed 's/[^.]*\.//;s/:/ /' \
	| sort -k 1 -n \
	| head -1 
done \
| sort -k 1 -n
