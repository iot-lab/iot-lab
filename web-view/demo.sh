#!/bin/bash

./httpd.py &
firefox localhost:8000 &
speed() { while read i; do echo $i; sleep $1; done; }

(
	seq 36 69 | tac | speed .1;
	seq 24 35 | tac | speed .2;
	seq  1 23 | tac | speed .1;
	seq 70 3 94  | speed .2 ;
	seq 95 5 178 | speed .4;
	seq 179 2 205 | speed .1;
	seq 207 2 289 | speed .3;
	seq 204 2 288 | tac | speed .2;
	seq 290 358 | speed .1
) | while read i; do
	j=$((RANDOM*290/65535+70));
	echo "{ $i: { style: 'splash' },
		$j: { style: 'circle green' }
	}" > user-state.json
done
