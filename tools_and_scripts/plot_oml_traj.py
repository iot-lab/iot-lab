#!/usr/bin/python
# -*- coding: utf-8 -*-

""" plot_oml_traj.py

./plot_oml_traj.py --input=<oml_filename> --maps=<map_filename.txt>
        --circuit=<circuit_filename.json> --time --angle --label=<MyExperiment>

for help use --help or -h
for time verification --time or -t
for plot angle --angle or -a
for begin sample --begin=<sample_beg> or -b <sample_beg>
for end sample --end=<sample_end> or -e <sample_end>
for label title plot --label=<title> or -l <title>
for plot maps and elements --maps=<filename> or -m <filename>
for plot circuit --circuit=<filename> or -c <filename>
"""

# disabling pylint errors 'E1101' no-member, false positive from pylint
#                         'R0912' too-many branches
# pylint:disable=I0011,E1101,R0912

import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# http://stackoverflow.com/a/26605247/395687
# pip install --no-index -f http://dist.plone.org/thirdparty/ -U PIL
# or 'apt-get install python-imaging'
from PIL import Image
import csv

import json
import matplotlib.patches as patches

FIELDS = {'t_s': 3, 't_us': 4, 'x': 5, 'y': 6, 'th': 7}
DECO = {'marker': 0, 'color': 1, 'size': 2, 'x': 3, 'y': 4}
MAPS = {'marker': 0, 'file': 1, 'ratio': 2, 'sizex': 3, 'sizey': 4,
        'offsetx': 5, 'offsety': 6}


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
    ['f' 'filename' ratio sizex sizey ofx ofy]

    """
    try:
        datafile = open(filename, 'r')
        datareader = csv.reader(datafile, delimiter=' ')
    except IOError as err:
        sys.stderr.write("Error opening maps file:\n{0}\n".format(err))
        sys.exit(2)
    except (ValueError, StopIteration) as err:
        sys.stderr.write("Error reading maps file:\n{0}\n".format(err))
        sys.exit(3)

    # Search if there is a map and split with other
    # elements (data_deco) and the map (data_map)
    findmap = False
    data_map = []
    data_deco = []
    for row in datareader:
        if len(row) > 0:
            if row[0] == 'f':
                findmap = True
                # float conversion
                for index in range(2, len(row)):
                    row[index] = float(row[index])
                data_map = row
            else:
                if row[0] != '#':
                    # float conversion
                    for index in range(2, len(row)):
                        row[index] = float(row[index])
                    data_deco.append(row)

    # If the map exists rescale x,y elements
    if findmap is True:
        ratio = data_map[MAPS['ratio']]
        sizey = data_map[MAPS['sizey']]
        ofx = data_map[MAPS['offsetx']]
        ofy = data_map[MAPS['offsety']]
        for ditem in data_deco:
            ditem[DECO['x']] = (ditem[DECO['x']] - ofx) / ratio
            ditem[DECO['y']] = sizey - (ditem[DECO['y']] - ofy) / ratio

    return data_deco, data_map


def circuit_load(filename):
    """ Load robot circuit file

    Parameters:
    ------------
    filename: string
              filename

    Returns:
    -------
    circuit: json object
    {
       "coordinates": [
       {
         "name": "0",
         "x": 9.5036359876481,
         "y": -0.8644077467101,
         "z": 0,
         "w": -2.4504422620417
       },
       {
         "name": "1",
         "x": 0.88773354001121,
         "y": 9.750401138047,
         "z": 0,
         "w": 0.46435151843117
       }
      ],
      "points":[
                "0",
                "1"
      ]
    }
    """

    json_data = open(filename, "rb")
    circuit = json.load(json_data)
    json_data.close()
    return circuit


def oml_plot(data, title, deco, maps, options, circuit=None):
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
    circuit:
       TODO
    """
    # Figure trajectory initialization
    circuit_fig = plt.figure()
    plt.title(title + ' trajectory')
    plt.grid()
    # Plot map image in background
    if len(maps) > 0:
        fname = maps[MAPS['file']]
        try:
            image = Image.open(fname).convert("L")
        except IOError as err:
            sys.stderr.write(
                "Error opening image map file:\n{0}\n".format(err))
            sys.exit(2)
        arr = np.asarray(image)
        plt.imshow(arr, cmap=cm.Greys_r)
        ratio = maps[MAPS['ratio']]
        sizey = maps[MAPS['sizey']]
        ofx = maps[MAPS['offsetx']]
        ofy = maps[MAPS['offsety']]
    else:
        ratio = 0
        sizey = 0
        ofx = 0
        ofy = 0
    # Plot elements for decoration
    for ditem in deco:
        plt.scatter(ditem[DECO['x']], ditem[DECO['y']],
                    marker=ditem[DECO['marker']],
                    color=ditem[DECO['color']], s=ditem[DECO['size']])
    # Plot robot trajectory
    if "-i" in options:
        timestamps = data[:, FIELDS['t_s']] + data[:, FIELDS['t_us']] / 1e6
        if ratio == 0:
            plt.plot(data[:, FIELDS['x']], data[:, FIELDS['y']])
            plt.xlabel('X (m)')
            plt.ylabel('Y (m)')
        else:
            plt.plot((data[:, FIELDS['x']] - ofx)/ratio,
                     sizey - (data[:, FIELDS['y']] - ofy)/ratio)
            plt.xlabel('X (pixels)')
            plt.ylabel('Y (pixels)')

    # Plot circuit
    # if circuit is not None:
    if "-c" in options:
        c_x = []
        c_y = []
        checkpoint_path = []

        for checkpoint in circuit['coordinates']:
            if ratio == 0:
                coord_x = checkpoint['x']
                coord_y = checkpoint['y']
            else:
                coord_x = (checkpoint['x'] - ofx)/ratio
                coord_y = sizey - (checkpoint['y'] - ofy)/ratio
            c_x.append(coord_x)
            c_y.append(coord_y)
            checkpoint_path.append([coord_x, coord_y])

        checkpoint_lines = patches.Polygon(checkpoint_path, linestyle='dashed',
                                           linewidth=2, edgecolor='red',
                                           fill=False)
        a_x = circuit_fig.add_subplot(111)
        a_x.add_patch(checkpoint_lines)
        plt.plot(c_x, c_y, 'ro')

    # Figure angle initialization
    if "-a" in options:
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
    """ Main command """
    options = []
    filename = ""
    try:
        opts, _ = getopt.getopt(argv, "i:hta:m:b:e:l:c:",
                                ["input=", "help", "time", "angle", "maps=",
                                 "begin=", "end=", "label=", "circuit="])
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
            options.append("-i")
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
        elif opt in ("-c", "--circuit"):
            options.append("-c")
            filename_circuit = arg
        elif opt in ("-a", "--angle"):
            options.append("-a")

    # Load file
    if "-i" in options:
        if len(filename) == 0:
            usage()
            sys.exit(2)
        data = oml_load(filename)[s_beg:s_end, :]
    else:
        data = None
    if "-m" in options:
        deco, img_map = maps_load(filename_maps)
    else:
        deco = ""
        img_map = ""
    if "-c" in options:
        circuit = circuit_load(filename_circuit)
    else:
        circuit = None
    oml_plot(data, title, deco, img_map, options, circuit)
    # Clock verification
    if "-t" in options:
        oml_clock(data)

    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
