#!/bin/bash

./httpd.py &> /dev/null &
firefox localhost:8000 &

delay() { while read i; do echo $i; sleep $1; done; }
alter() { awk 'NR % 2 { print; next } { print $1 " circle green" }'; }

(
	seq 36 69 | tac | delay .1;
	seq 24 35 | tac | alter | delay .1;
	seq  1 23 | tac | delay .2;
	seq 70 3 94  | alter | delay .03;
	seq 95 5 178 | delay .4;
	seq 179 2 205 | delay .1;
	seq 207 2 289 | delay .3;
	seq 204 2 288 | tac | delay .2;
	seq 290 358 | alter | delay .1;
	sleep 1.5;
) | ./splash.sh
