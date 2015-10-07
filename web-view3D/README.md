web-view3D
==========

Provides control and viewing capabilities from serial-aggregator into your browser -- powered by node.js.

**This work is under development**

This work implement a node.js application, which consume and interprete the serial_aggragator data into a webpage with 3D view of the topology.
For now, the index.html file implements the sonar example, available at (github:openlab/appli/iot-lab/sonar).

Prerequisites
-------------
* install nodejs
* install following nodejs packages: express, socket.io

Run
---
0. You need a running experiment.
1. Run `serial_aggregator` on testbed site ssh frontend as tcp server:
```sh
socat tcp-listen:9000,fork,reuseaddr exec:'ssh <user>@<site>.iot-lab.info "serial_aggregator -i <experiment id>"'
```
2. Run the node.js application:
```sh
nodejs app.js
```
3. Open your browser at (http://localhost:3000)

Usage
-----
1. Select your site in the list and click the *Resources* button.
2. Select one of your nodes (e.g. one from your experiment) and click on one of the *power* buttons, to send a broadcast radio message.

