# -*- coding: utf-8 -*-
""" Robot Experiment """

import argparse
import sys
from iotlabcli import auth
from iotlabcli import rest
from iotlabcli import experiment


class RobotExpe(object):
    """
    A simple REST client to launch experimentations on a robot

    """

    def __init__(self, nodename, profile, timeexpe):
        user, passwd = auth.get_user_credentials()
        self.api = rest.Api(user, passwd)
        self.idexpe = 0
        self.nodename = nodename
        self.profile = profile
        self.time = timeexpe

    def submit(self):
        """"
        Submit an experiment
        using class attribute for parametrization :
         self.nodename
         self.profile
         self.time
        """
        qexp = experiment.submit_experiment(
            self.api, 'test', self.time, [{'firmware': None,
                                           'profile': self.profile,
                                           'type': 'physical',
                                           'nodes': [self.nodename]}])

        self.idexpe = qexp['id']

    def wait_run(self):
        """ Wait the experimentation is Running """
        experiment.wait_experiment(self.api, self.idexpe, states='Running')

    def wait_stop(self):
        """ Wait the experimentation is Terminated """
        experiment.wait_experiment(self.api, self.idexpe, states='Terminated')

    def setparam(self, nodename, profile, timeexpe):
        """
        Change class attributes for experimentation parameters
        will be take in account in the next submit
        """
        self.nodename = nodename
        self.profile = profile
        self.idexpe = timeexpe

    def experiment(self):
        """  Launch one experimentation and wait its termination """
        self.submit()
        print "Submit robot expe", self.idexpe
        if self.idexpe > 0:
            print "Robot wait expe start..."
            self.wait_run()
            print "Robot expe stop..."
            self.wait_stop()
        else:
            print "Robot robot submit failed"

    def loop(self, nb_expe):
        """ Loop for nb_expe experiments """
        for index in range(0, nb_expe):
            print "--- Robot expe number ", index
            self.experiment()


TIMEEXPE_DEF = 5
PROFILEEXPE_DEF = 'robot_c2'
COUNT_DEF = 3


def launch():
    """ Launch the process taking into account arguments
    """
    # create parser
    parser = argparse.ArgumentParser(description="Robot Experimentations")
    # add arguments
    parser.add_argument('node_name', metavar='node_name', type=str, nargs=1,
                        help="complete node name, ex: m3-381.grenoble.iot-lab.info")
    parser.add_argument('-c', '--count', type=int,
                        help="number of experimentations to launch")
    parser.add_argument('-t', '--time', type=int,
                        help="duration in minutes of a experimentation")
    parser.add_argument('-p', '--profile', type=str,
                        help="profile name for experimentation")
    args = parser.parse_args()

    # Arguments verification
    if len(args.node_name) != 1:
        parser.print_help()
        sys.exit()
    else:
        node_name = str(args.node_name[0])

    if args.time < 0 or args.time is None:
        args.time = TIMEEXPE_DEF
    if args.count < 0 or args.count is None:
        args.count = COUNT_DEF
    if args.profile is None:
        args.profile = PROFILEEXPE_DEF

    robot = RobotExpe(node_name, args.profile, args.time)
    robot.loop(args.count)

if __name__ == '__main__':
    launch()
