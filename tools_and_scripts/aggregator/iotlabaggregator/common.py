#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Common functions that may be required """
import os
import itertools
from iotlabcli import experiment
from iotlabcli.helpers import node_url_sort_key
import iotlabcli.parser.common
import iotlabcli.parser.node

HOSTNAME = os.uname()[1]


# http://stackoverflow.com/questions/1092531/event-system-in-python
class Event(list):  # pylint:disable=too-few-public-methods
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

    Example Usage:
    >>> def f(x):
    ...     print 'f(%s)' % x
    >>> def g(x):
    ...     print 'g(%s)' % x

    >>> e = Event()
    >>> e()
    >>> e.append(f)
    >>> e(123)
    f(123)
    >>> e.remove(f)
    >>> e()

    >>> e += (f, g)
    >>> e(10)
    f(10)
    g(10)
    >>> del e[0]
    >>> e(2)
    g(2)


    >>> e   # doctest: +ELLIPSIS
    Event('[<function g at 0x...>]')

    """

    def __call__(self, *args, **kwargs):
        for func in self:
            func(*args, **kwargs)

    def __repr__(self):
        return "Event(%r)" % list.__repr__(self)


def extract_nodes(resources, hostname=HOSTNAME):
    """ Extract the nodes for this server
    >>> resources = {"items": [ \
        {'network_address': 'm3-1.grenoble.iot-lab.info', 'site': 'grenoble'},\
        {'network_address': 'wsn430-1.lille.iot-lab.info', 'site': 'lille'},\
        {'network_address': 'a8-1.strasbourg.iot-lab.info',\
         'site': 'strasbourg'},\
        {'network_address': 'wsn430-4.grenoble.iot-lab.info', 'site':\
         'grenoble'},\
        {'network_address': 'a8-1.grenoble.iot-lab.info', 'site': 'grenoble'},\
        ]}

    >>> extract_nodes(resources, hostname='grenoble')
    ['m3-1', 'wsn430-4', 'a8-1']
    """
    sites_nodes = [n for n in resources['items'] if n['site'] == hostname]
    nodes = [n['network_address'].split('.')[0] for n in sites_nodes]
    return nodes


def get_experiment_nodes(api, exp_id=None, hostname=HOSTNAME):
    """ Add the nodes from given experiment
    Return the experiment nodes list. Returns an empty list if exp_id is None
    Restrict to the nodes from current site

    :raise ValueError: If the experiment is not running,
    """
    # add nodes from experiment

    if exp_id is None:
        return []

    # Check that the experiment is running
    state = experiment.get_experiment(api, exp_id, 'state')["state"]
    if 'Running' != state:
        raise RuntimeError("Experiment %u not running '%s'" % (exp_id, state))

    # Check that the experiment is running
    resources = experiment.get_experiment(api, exp_id, 'resources')
    return extract_nodes(resources, hostname)


def query_nodes(api, exp_id=None, nodes_list_list=(), hostname=HOSTNAME):
    """ Get nodes list from experiment and/or nodes_list_list.
    Or currently running experiment if none provided """
    nodes_list = frozenset(itertools.chain.from_iterable(nodes_list_list))

    nodes = set()
    # no nodes supplied, try to get currently running experiment
    if exp_id is None and not len(nodes_list):
        exp_id = iotlabcli.get_current_experiment(api)

    # add nodes from experiment, empty if exp_id is None
    nodes.update(get_experiment_nodes(api, exp_id, hostname))
    # add nodes from nodes_list, may be empty
    nodes.update([n.split('.')[0] for n in nodes_list if hostname in n])

    # sorted output for tests
    return sorted(list(nodes))


def add_nodes_selection_parser(parser):
    """ Add parser arguments for selecting nodes """

    iotlabcli.parser.common.add_auth_arguments(parser)
    nodes_group = parser.add_argument_group(
        description="By default, select currently running experiment nodes",
        title="Nodes selection")

    nodes_group.add_argument('-i', '--id', dest='experiment_id', type=int,
                             help='experiment id submission')

    nodes_group.add_argument(
        '-l', '--list', type=iotlabcli.parser.node.nodes_list_from_str,
        action='append', default=[],
        dest='nodes_list', help='nodes list in format: "site,archi,1-5+9". '
        'Can be supplied multiple times'
    )


def get_nodes_selection(username, password, experiment_id, nodes_list,
                        *_args, **_kwargs):  # pylint:disable=unused-argument
    """ Return the requested nodes from 'experiment_id', and 'nodes_list """
    username, password = iotlabcli.get_user_credentials(username, password)
    api = iotlabcli.Api(username, password)
    nodes = query_nodes(api, experiment_id, nodes_list)
    return nodes
