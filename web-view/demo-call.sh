#!/bin/bash

#./httpd.py &> /dev/null &
#firefox localhost:8000 &

seq 0 5 720 | while read r;
do
	echo '
	{
		"381" : {
			text: "Robot '$r'!",
			call: "set_orientation(\"m3-381\", '$r')",
		},
	}' > user-state.json
	sleep .1
done
