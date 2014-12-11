Web-View
========

Provides control and customizable viewing capabilities for IoT-LAB.


Prerequisites
-------------

- you need cli-tools installed and working
- you need sudo apt-get install python-simplejson


Running Experiments
-------------------

- start the server: ``./httpd.py &``
- browse to: http://localhost:8000/ 
- wait a few seconds for the display to update
- select some available nodes, you can use click'n'drag
- click "grab", provide experiment duration (in minutes)
- wait for the nodes to finish flashing
- edit file firmwares.json, set path(s) to firmware(s)
- click "update", select firmware
- wait for the nodes to finish flashing
- you're done !

In case an error happens during operation, the nodes in error
flash quicker for 2 seconds and are shown as "failed".


Showing What's Going On
-----------------------

- web-view polls file user-state.json every 100ms
- generate user-state.json by script or whatever
- create your own styles as needed
- update the polling frequency in script.js as needed

Run ``./demo.sh`` to see what it looks like, and check the script
for inspiration.


Starting / Stopping / Resetting nodes
-------------------------------------

- select some nodes that you own
- click start, stop or reset

The selection is adjusted to contain only nodes that you own.
If the selection is empty, the buttons do nothing.


Saving / Loading Nodes Sets
---------------------------

- select some nodes
- click "save", provide a name
- click "load", select a node set

Node sets are saved in file ``nodes-sets.json``, which may be
edited manually or by script.


Internals Overview
------------------

The following files are "user data" and read by the system:
- user-styles.css
- user-state.json
- nodes-sets.json
- firmwares.json

The following files are "core" and may be customized:
- script.js
- sensors.js
- httpd.py

File lib-drag-drop.js is a re-packed single-file version of a
region-selection library courtesy of http://threedubmedia.com/

File nodes-sets.json is updated when button "save" is used,
providing for easy export of selected nodes.

File user-state.json is polled by the web gui every 100ms; the intended
use is that an externel process writes this file to display system state.

[![web-view archi](https://github.com/iot-lab/iot-lab/wiki/Images/web-view_archi.png)](web-view archi.odg)
