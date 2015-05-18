#!/usr/bin/python
# -*- coding: utf-8 -*-

""" plot_distance.py

./plot_distance.py
Plot distance between a mobile node and a fixe one

export PYTHONPATH=$PYTHONPATH:..:../../qualif/geo

see https://github.com/iot-lab/iot-lab/wiki/Distance-mobile-fixed-nodes
"""

import  plot_oml_traj
import grenoble
import numpy as np
import matplotlib.pyplot as plt

# OML trajectory file of the mobile node
LOGROBOT = "m3-382-Jhall_w.oml"
# M3 Node ID fixed node 
ID_NODE = 30
# Sample time extraction
S_BEG = 0
S_END = -1
# Cartesian offset between trajectory coordinates
# and fixed nodes for Grenoble site
OFX_GRE = - 3.11
OFY_GRE = + 7.80

# Fields of Robot logfile oml
FIELDS = {'t_s': 3, 't_us': 4, 'x': 5, 'y': 6, 'th': 7}

# Load robot trajectory
mobnode = plot_oml_traj.oml_load(LOGROBOT)[S_BEG:S_END, :]
# Load 3D coordinates of node ID_NODE
geonodes = grenoble.list_nodes_offset("m3", OFX_GRE, OFY_GRE, 0.0)
fixnode = geonodes[ID_NODE]
print "fixnode ", geonodes[ID_NODE]
# Compute the distance between the mobile node and 
dist = (mobnode[:, FIELDS['x']]-fixnode[0])**2 +\
    (mobnode[:, FIELDS['y']]-fixnode[1])**2 +\
    (fixnode[2])**2
dist = np.sqrt(dist)
timestamps = mobnode[:, FIELDS['t_s']] + mobnode[:, FIELDS['t_us']] / 1e6

# Plot this distance along the time
plt.figure()
plt.grid()
plt.title("Distance m3-" + str(ID_NODE) + "/mobile node")
plt.plot(timestamps, dist)
plt.xlabel('time (sec)')
plt.ylabel('distance (m)')
plt.show()
