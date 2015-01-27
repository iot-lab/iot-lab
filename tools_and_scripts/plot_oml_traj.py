#!/usr/bin/python
# -*- coding: utf-8 -*-

""" plot_oml_traj.py

plot oml robot trajectory [-bdeht] -i <filename> or --input=<filename>

for time verification --time or -t
for begin sample --begin=<sample_beg> or -b <sample_beg>
for end sample --end=<sample_end> or -e <sample_end>
for label title plot --label=<title> or -l <title>
for plot decoration --decor=<filename> or -c <filename>
for help use --help or -h
"""

# disabling pylint errors 'E1101' no-member, false positive from pylint
#                         'R0912' too-many branches
# pylint:disable=I0011,E1101,R0912

import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt

FIELDS = {'t_s': 3, 't_us': 4, 'x': 5, 'y': 6, 'th': 8}
DECO = {'marker': 0, 'color': 1, 'size': 2, 'x': 3, 'y': 4}


def oml_load(filename):
    """ Load iot-lab om file

    Parameters:
    ------------
    filename: string
              oml filename

    Returns:
    -------
    data : numpy array
    [oml_timestamp 1 count timestamp_s timestamp_us x y theta]

    >>> from StringIO import StringIO
    >>> oml_load(StringIO('\\n' * 10 + '1 2 3\\n'))
    array([ 1.,  2.,  3.])

    >>> sys.stderr = sys.stdout  # hide stderr output

    >>> oml_load('/invalid/file/path')
    Traceback (most recent call last):
    SystemExit: 2

    >>> oml_load(StringIO('\\n' * 10 + 'invalid_content'))
    array(nan)

    # Invalid file content.
    # Raises IOError on python2.6 and StopIteration in python2.7
    >>> oml_load(StringIO('1 2 3'))  # doctest:+ELLIPSIS
    Traceback (most recent call last):
    SystemExit: ...


    >>> sys.stderr = sys.__stderr__
    """
    try:
        data = np.genfromtxt(filename, skip_header=10, invalid_raise=False)
    except IOError as err:
        sys.stderr.write("Error opening oml file:\n{0}\n".format(err))
        sys.exit(2)
    except (ValueError, StopIteration) as err:
        sys.stderr.write("Error reading oml file:\n{0}\n".format(err))
        sys.exit(3)

    return data


def decor_load(filename):
    """ Load iot-lab om file

    Parameters:
    ------------
    filename: string
              filename

    Returns:
    -------
    data : array
    [mark color x y]

    >>> from StringIO import StringIO
    >>> decor_load(StringIO('\\n' * 10 + '1 2 3\\n'))
    array([ 1.,  2.,  3.])

    >>> sys.stderr = sys.stdout  # hide stderr output

    >>> oml_load('/invalid/file/path')
    Traceback (most recent call last):
    SystemExit: 2

    >>> oml_load(StringIO('\\n' * 10 + 'invalid_content'))
    array(nan)

    # Invalid file content.
    # Raises IOError on python2.6 and StopIteration in python2.7
    >>> decor_load(StringIO('1 2 3'))  # doctest:+ELLIPSIS
    Traceback (most recent call last):
    SystemExit: ...


    >>> sys.stderr = sys.__stderr__
    """
    try:
        data = np.genfromtxt(filename, skip_header=1,
                             dtype=None, invalid_raise=False)
    except IOError as err:
        sys.stderr.write("Error opening decor file:\n{0}\n".format(err))
        sys.exit(2)
    except (ValueError, StopIteration) as err:
        sys.stderr.write("Error reading decor file:\n{0}\n".format(err))
        sys.exit(3)

    return data


def oml_plot(data, title, decor):
    """ Plot iot-lab oml data

    Parameters:
    ------------
    data: numpy array
      [oml_timestamp 1 count timestamp_s timestamp_us power voltage current]
    title: string
       title of the plot
    decor: array
       [marker, color, size,  x, y]
       for marker see http://matplotlib.org/api/markers_api.html
       for color  see http://matplotlib.org/api/colors_api.html
       plot point item for trajectory
    """
    timestamps = data[:, FIELDS['t_s']] + data[:, FIELDS['t_us']] / 1e6

    plt.figure()
    plt.title(title + ' trajectory')
    plt.grid()
    plt.plot(data[:, FIELDS['x']], data[:, FIELDS['y']])
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')

    if decor is not "":
        for ditem in decor:
            plt.scatter(ditem[DECO['x']], ditem[DECO['y']],
                        marker=ditem[DECO['marker']],
                        color=ditem[DECO['color']], s=ditem[DECO['size']])
    plt.figure()
    plt.title(title + ' angle')
    plt.grid()
    plt.plot(timestamps, data[:, FIELDS['th']])
    plt.xlabel('Sample Time (sec)')
    plt.ylabel('yaw angle (rad)')
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
    clock = np.diff(time) * 1000  # pylint:disable=I0011,E1101
    plt.plot(clock)

    print 'NB Points      =', len(time)
    print 'Duration    (s)=', time[-1] - time[0]
    print 'Steptime    (ms)=', 1000 * (time[-1] - time[0]) / len(time)
    print 'Time to', time[0], 'From', time[-1]
    print 'Clock mean (ms)=', np.mean(clock)  # pylint:disable=I0011,E1101
    print 'Clock std  (ms)=', np.std(clock)  # pylint:disable=I0011,E1101
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
        opts, _ = getopt.getopt(argv, "i:htd:b:e:l:",
                                ["input=", "help", "time",
                                 "begin=", "end=", "label="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    s_beg = 0
    s_end = -1
    title = "Robot"
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
        elif opt in ("-d", "--decor"):
            options.append("-d")
            filename_decor = arg

    if len(filename) == 0:
        usage()
        sys.exit(2)

    # Load file
    data = oml_load(filename)[s_beg:s_end, :]
    # decor = [['o', 'blue', 2, 4], ['o', 'red', 1, 6]]
    decor = ""
    if "-d" in options:
        decor = decor_load(filename_decor)
        print "DECOR", decor
    oml_plot(data, title, decor)
    # Clock verification
    if "-t" in options:
        oml_clock(data)

    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
