#!/bin/bash

./httpd.py &
firefox localhost:8000 &
delay() { while read i; do echo $i; sleep $1; done; }

(
	seq 36 69 | tac | delay .1;
	seq 24 35 | tac | delay .2;
	seq  1 23 | tac | delay .1;
	seq 70 3 94  | delay .2 ;
	seq 95 5 178 | delay .4;
	seq 179 2 205 | delay .1;
	seq 207 2 289 | delay .3;
	seq 204 2 288 | tac | delay .2;
	seq 290 358 | delay .1
) | while read i; do
	j=$((RANDOM*290/65535+70));
	echo "{ $i: { style: 'splash' },
		$j: { style: 'circle green' }
	}" > user-state.json
done
