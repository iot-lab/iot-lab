OpenA8 fabric deployement script
================================

This fabfile has been written to simply configure all Open A8 of an experiment.


Requirement
-----------

Dependencies:

 * python-fabric >= 1.5.0  # support for fabric 'gateway'
 * iotlabcli >= 1.4.0      # new library api

It also requires that you run once `auth-cli --user`.


Usage
=====

    $ fab -l
    Fabric methods to help running commands on A8 nodes

    Available commands:

        exp       Extract nodes from `exp_id` experiment and set them as commands targets
        redirect  Start Open A8 node m3 serial port redirection
        reset     Reset Open A8 node m3
        update    Update the firmware on all experiment nodes

By default, the script will run the tasks on the currently running experiment nodes.

Updates current experiment open-A8-m3 nodes firmwares and start serial port
redirection to port 20000 (like open m3).

    $ fab update:../path_to/a_firmware/open_a8_fw.elf redirect


Specifying the experiment
-------------------------

You can also specify on which experiment nodes to run the tasks by calling
`exp:<exp_id>` before the tasks names.

    $ fab exp:<exp_id> redirect reset

