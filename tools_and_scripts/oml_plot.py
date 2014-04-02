#!/usr/bin/python
# -*- coding: utf-8 -*-

""" oml_plot.py

plot oml filename [-tpvcah] -i <filename> or --input=<filename>

for time verification --time or -t
for begin sample --begin=<sample_beg> or -b <sample_beg>
for end sample --end=<sample_end> or -e <sample_end>
for label title plot --label=<title> or -l <title>
for plot consumption --power or -p
for plot voltage --voltage or -v
for plot current --current or -c
for all plot --all or -a
for help use --help or -h
"""

import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt

FIELDS = {'t_s': 3, 't_us': 4, 'power': 5, 'voltage': 6, 'current': 7}


def oml_load(filename):
    """ Load iot-lab om file

    Parameters:
    ------------
    filename: string
              oml filename

    Returns:
    -------
    data : numpy array
    [oml_timestamp 1 count timestamp_s timestamp_us power voltage current]
    """
    try:
        data = np.loadtxt(filename, skiprows=10)
    except IOError as err:
        print "Error opening oml file:\n{}".format(err)
        usage()
        sys.exit(2)

    return data


def oml_all_plot(data, title):
    """ Plot iot-lab oml all data

    Parameters:
    ------------
    data: numpy array
      [oml_timestamp 1 count timestamp_s timestamp_us power voltage current]
    title: string
       title of the plot
    """

    timestamps = data[:, FIELDS['t_s']] + data[:, FIELDS['t_us']] / 1e6

    plt.figure()
    plt.subplot(311)
    plt.grid()
    plt.title(title)
    plt.plot(timestamps, data[:, FIELDS['power']])
    plt.ylabel('Power (W)')
    plt.subplot(312)
    plt.grid()
    plt.title("node2")
    plt.plot(timestamps, data[:, FIELDS['voltage']])
    plt.ylabel('Voltage (V)')
    plt.subplot(313)
    plt.grid()
    plt.plot(timestamps, data[:, FIELDS['current']])
    plt.ylabel('Current (A)')
    plt.xlabel('Sample Time (sec)')
    return


def oml_plot(data, title, labely, channel):
    """ Plot iot-lab oml data

    Parameters:
    ------------
    data: numpy array
      [oml_timestamp 1 count timestamp_s timestamp_us power voltage current]
    title: string
       title of the plot
    channel: number
       channel to plot 5 = power, 6 = voltage, 7 = current
    """
    timestamps = data[:, FIELDS['t_s']] + data[:, FIELDS['t_us']] / 1e6
    print data[0, :]

    plt.figure()
    plt.title(title)
    plt.grid()
    plt.plot(timestamps, data[:, FIELDS[channel]])
    plt.xlabel('Sample Time (sec)')
    plt.ylabel(labely)

    return


def oml_clock(data):
    """ Clock time plot and verification

    Parameters:
    ------------
    data: numpy array
      [oml_timestamp 1 count timestamp_s timestamp_us power voltage current]
    echd : int
       sample count begin
    echf : int
       sample count end
    """
    plt.figure()
    plt.title("Clock time verification")
    plt.grid()
    time = data[:, FIELDS['t_s']] + data[:, FIELDS['t_us']] / 1e6
    clock = np.diff(time) * 1000
    plt.plot(clock)

    print 'NB Points      =', len(time)
    print 'Duration    (s)=', time[-1] - time[0]
    print 'Steptime    (ms)=', 1000 * (time[-1] - time[0]) / len(time)
    print 'Time to', time[0], 'From', time[-1]
    print 'Clock mean (ms)=', np.mean(clock)
    print 'Clock std  (ms)=', np.std(clock)
    print 'Clock max  (ms)=', np.max(clock)
    print 'Clock min  (ms)=', np.min(clock)
    return


def usage():
    """Usage command print
    """
    print "Usage"
    print __doc__


def main(argv):
    """ Main command
    """
    options = []
    filename = ""
    try:
        opts, _ = getopt.getopt(argv, "i:htpcvab:e:l:",
                                ["input=", "help", "time", "power", "current",
                                 "voltage", "all", "begin=", "end=", "label="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    s_beg = 0
    s_end = -1
    title = "Node"
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-i", "--input"):
            filename = arg
        elif opt in ("-l", "--label"):
            title = arg
        elif opt in ("-b", "--begin"):
            s_beg = int(arg)
        elif opt in ("-e", "--end"):
            s_end = int(arg)
        elif opt in ("-t", "--time"):
            options.append("-t")
        elif opt in ("-p", "--power"):
            options.append("-p")
        elif opt in ("-c", "--current"):
            options.append("-c")
        elif opt in ("-v", "--voltage"):
            options.append('-v')
        elif opt in ("-a", "--all"):
            options.append("-a")

    if len(filename) == 0:
        usage()
        sys.exit(2)

    # Load file
    data = oml_load(filename)[s_beg:s_end, :]
    # Plot power consumption
    if "-p" in options:
        oml_plot(data, title +
                 " power consumption", "Power (W)", 'power')
    # Plot voltage
    if "-v" in options:
        oml_plot(data, title + " voltage", "Voltage (V)", 'voltage')
    # Plot voltage
    if "-c" in options:
        oml_plot(data, title + " current", "Current (A)", 'current')
    # All Plot
    if "-a" in options:
        oml_all_plot(data, title)
    # All Plot
    if "-t" in options:
        oml_clock(data)

    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
