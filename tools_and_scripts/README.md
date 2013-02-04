Aggregate log
=============

Take an experiment description as input.
Gather all nodes output to stdout, prefixed by the node number.

        node42;Hello world
        node66;The cake is a lie!
        node1;Come the dark side, we have cookies.



Usage
-----

On each server your experiment is run on:

        experiment-cli get -r | ./aggregate_log.py

It outputs the nodes messages line by line, prefixed by the node number.

No message can be sent to the nodes, it's only a logging feature.



Warning
-------

If a node sends only characters without newlines, the output is never printed.
To give a 'correct' looking output, only lines are printed.


### Multi sites experiments ###

The script will try to connect to all the nodes of the experiment.

So if you have nodes booked on another site, you will see error messages like:

        node71.grenoble.senslab.info;Connection error




