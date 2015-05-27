#!/usr/bin/python
# -*- coding: utf-8 -*-

""" plot_distance.py

./plot_distance.py <oml_trajectory_file> <m3_fixed_node_num>

Plot distance between a mobile node and a fixe one

see https://github.com/iot-lab/iot-lab/wiki/Distance-mobile-fixed-nodes
"""

import sys
import plot_oml_traj
import geo.grenoble
import numpy as np
import matplotlib.pyplot as plt

# numpy is not correctly introspected
# pylint: disable=no-member

# Sample time extraction
S_BEG = 0
S_END = -1
# Cartesian offset between trajectory coordinates
# and fixed nodes for Grenoble site
OFX_GRE = - 3.11
OFY_GRE = + 7.80

# Fields of Robot logfile oml
FIELDS = {'t_s': 3, 't_us': 4, 'x': 5, 'y': 6, 'th': 7}


def plot_m3_node_distance(robot_traj_file, node_id):
    """ Plot distance between node num 'node_id' and 'robot_traj_file' """

    # Load robot trajectory
    mobnode = plot_oml_traj.oml_load(robot_traj_file)[S_BEG:S_END, :]
    # Load 3D coordinates of node node_id
    #   Maybe use 'cli-tools' here to get the nodes
    geonodes = geo.grenoble.list_nodes_offset("m3", OFX_GRE, OFY_GRE, 0.0)
    fixnode = geonodes[node_id]
    print "fixnode ", geonodes[node_id]
    # Compute the distance between the mobile node and node num 'node_id'
    dist = (mobnode[:, FIELDS['x']]-fixnode[0])**2 +\
        (mobnode[:, FIELDS['y']]-fixnode[1])**2 +\
        (fixnode[2])**2
    dist = np.sqrt(dist)
    timestamps = mobnode[:, FIELDS['t_s']] + mobnode[:, FIELDS['t_us']] / 1e6

    # Plot this distance along the time
    plt.figure()
    plt.grid()
    plt.title("Distance m3-" + str(node_id) + "/mobile node")
    plt.plot(timestamps, dist)
    plt.xlabel('time (sec)')
    plt.ylabel('distance (m)')
    plt.show()


def main():
    """ Plot distance between node and robot """
    try:
        # OML trajectory file of the mobile node
        trajectory = sys.argv[1]
        # M3 Node ID fixed node
        node_num = int(sys.argv[2])
    except IndexError:
        sys.stderr.write(
            "Usage: %s <oml_trajectory_file> <m3_fixed_node_num>\n" %
            sys.argv[0])
        exit(1)

    plot_m3_node_distance(trajectory, node_num)

if __name__ == '__main__':
    main()
