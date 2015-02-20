#!/usr/bin/python
# -*- coding: utf-8 -*-

""" plot_oml_traj.py

plot oml robot trajectory [-behmt] -i <filename> or --input=<filename>

for time verification --time or -t
for begin sample --begin=<sample_beg> or -b <sample_beg>
for end sample --end=<sample_end> or -e <sample_end>
for label title plot --label=<title> or -l <title>
for plot maps and elements --maps=<filename> or -c <filename>
for help use --help or -h
"""

# disabling pylint errors 'E1101' no-member, false positive from pylint
#                         'R0912' too-many branches
# pylint:disable=I0011,E1101,R0912

import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import Image

FIELDS = {'t_s': 3, 't_us': 4, 'x': 5, 'y': 6, 'th': 7}
DECO = {'marker': 0, 'color': 1, 'size': 2, 'x': 3, 'y': 4}
MAPS = {'marker': 0, 'file': 1, 'ratio': 2, 'sizex': 3, 'sizey': 4}


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


def maps_load(filename):
    """ Load iot-lab om file

    Parameters:
    ------------
    filename: string
              filename

    Returns:
    -------
    data_deco : numpy array
    [[mark color size x y] [mark1 color1 size1 x1 y1]...]

    data_map : numpy array
    ['f' 'filename' ratio sizex sizey]

    """
    data = None
    try:
        data = np.genfromtxt(filename, skip_header=1,
                             dtype=None, invalid_raise=False)
    except IOError as err:
        sys.stderr.write("Error opening maps file:\n{0}\n".format(err))
        sys.exit(2)
    except (ValueError, StopIteration) as err:
        sys.stderr.write("Error reading maps file:\n{0}\n".format(err))
        sys.exit(3)

    # Search if there is a map and split with other
    # elements (data_deco) and the map (data_map)
    findmap = False
    index = 0
    data_map = None
    if data.size == 1:
        data = np.atleast_1d(data)

    while index < data.size and not findmap:
        if data[index][DECO['marker']] == 'f':
            findmap = True
            data_map = data[index]
            data_deco = np.delete(data, index, 0)
        else:
            index = index + 1
    # If the map exists rescale x,y elements
    if findmap is False:
        data_deco = data
    else:
        ratio = data_map[MAPS['ratio']]
        sizey = data_map[MAPS['sizey']]
        for ditem in data_deco:
            ditem[DECO['x']] = ditem[DECO['x']] / ratio
            ditem[DECO['y']] = sizey - ditem[DECO['y']] / ratio

    return data_deco, data_map


def oml_plot(data, title, deco, maps):
    """ Plot iot-lab oml data

    Parameters:
    ------------
    data: numpy array
      [oml_timestamp 1 count timestamp_s timestamp_us power voltage current]
    title: string
       title of the plot
    deco: array
       [marker, color, size,  x, y]
       for marker see http://matplotlib.org/api/markers_api.html
       for color  see http://matplotlib.org/api/colors_api.html
    maps: array (size 1)
       [marker, filename_img, ratio, sizex, sizey]
       plot point item for trajectory with filename_img in background
    """
    timestamps = data[:, FIELDS['t_s']] + data[:, FIELDS['t_us']] / 1e6
    # Figure trajectory initialization
    plt.figure()
    plt.title(title + ' trajectory')
    plt.grid()
    # Plot map image in background
    if maps is not "":
        fname = maps[MAPS['file']]
        try:
            image = Image.open(fname).convert("L")
        except IOError as err:
            sys.stderr.write(
                "Error opening image map file:\n{0}\n".format(err)
                )
            sys.exit(2)
        arr = np.asarray(image)
        plt.imshow(arr, cmap=cm.Greys_r)
        ratio = maps[MAPS['ratio']]
        sizey = maps[MAPS['sizey']]
    else:
        ratio = 0
        sizey = 0
    # Plot elements for decoration
    for ditem in deco:
        plt.scatter(ditem[DECO['x']], ditem[DECO['y']],
                    marker=ditem[DECO['marker']],
                    color=ditem[DECO['color']], s=ditem[DECO['size']])
    # Plot robot trajectory
    if ratio == 0:
        plt.plot(data[:, FIELDS['x']], data[:, FIELDS['y']])
        plt.xlabel('X (m)')
        plt.ylabel('Y (m)')
    else:
        plt.plot(data[:, FIELDS['x']]/ratio,
                 sizey - data[:, FIELDS['y']]/ratio)
        plt.xlabel('X (pixels)')
        plt.ylabel('Y (pixels)')

    # Figure angle initialization
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
        opts, _ = getopt.getopt(argv, "i:htm:b:e:l:",
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
        elif opt in ("-m", "--maps"):
            options.append("-m")
            filename_maps = arg

    if len(filename) == 0:
        usage()
        sys.exit(2)

    # Load file
    data = oml_load(filename)[s_beg:s_end, :]
    if "-m" in options:
        deco, img_map = maps_load(filename_maps)
    else:
        deco = ""
        img_map = ""
    oml_plot(data, title, deco, img_map)
    # Clock verification
    if "-t" in options:
        oml_clock(data)

    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
