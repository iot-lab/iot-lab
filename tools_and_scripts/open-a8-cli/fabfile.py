""" Fabric methods to help running commands on A8 nodes """
import os
import functools
import logging

from fabric.api import env, run, execute
from fabric.api import task, parallel, roles, runs_once
from fabric.utils import abort, puts
from fabric import operations

import iotlabcli
import iotlabcli.helpers
import iotlabcli.experiment
import iotlabcli.parser.common

_VERSION = (int(n) for n in env.version.split('.'))
assert (1, 5, 0) >= _VERSION, \
    ("Fabric should support ssh 'gateway'. Should be at least version '1.5'" +
     ": %r" % env.version)

# Debug paramiko
logging.basicConfig(level=logging.CRITICAL)
# logging.basicConfig(level=logging.DEBUG)

env.use_ssh_config = True
env.ssh_config_path = './ssh_config'

env.reject_unknown_hosts = False
env.disable_known_hosts = True
env.abort_on_prompts = True

env.skip_bad_hosts = True

env.colorize_errors = True
env.pool_size = 10


def _get_exp_a8_nodes(api, exp_id=None):
    """ Get the list of a8 nodes from given experiment """
    experiment = iotlabcli.experiment.get_experiment(api, exp_id)
    _ok_nodes = experiment["deploymentresults"]["0"]

    # select valid a8 nodes from 'site'
    nodes = [str('root@node-' + n) for n in _ok_nodes if n.startswith('a8')]
    if not nodes:
        abort("No successfully deployed A8 nodes found for exp:%u" % exp_id)
    return nodes


@runs_once
@task
def exp(exp_id=None):
    """ Extract nodes from `exp_id` experiment and set them as commands targets
    Following roles are set:
     * nodes: all the a8 nodes of the experiment
     * frontends: each sites where there are a8 nodes

    """
    username, password = iotlabcli.get_user_credentials()
    api = iotlabcli.Api(username, password)
    exp_id = iotlabcli.get_current_experiment(api, exp_id)

    env.user = username

    nodes = _get_exp_a8_nodes(api, exp_id)
    env.roledefs['nodes'] = nodes

    sites = list(set([url.split('.', 1)[1] for url in nodes]))
    env.roledefs['frontends'] = sites


def exp_task(func):
    """ Declare a task that will only be called after calling 'exp' task.
    If exp task was already called, a new call won't be done."""
    @runs_once
    @task
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """ wrapper that calls 'exp' before actual task """
        execute(exp, exp_id=None)
        ret = func(*args, **kwargs)
        print_result(ret)

    return wrapper

def host_sort_key(value):
    """Hosts sort key. Sort nodes by archi/numbers, or return host."""
    try:
        return iotlabcli.helpers.node_url_sort_key(value)
    except ValueError:
        return value

def inv_dict(in_d):
    """ Invert dict and store values in a list """
    out_d = {}
    for key, val in in_d.iteritems():
        out_d.setdefault(str(val), []).append(key)

    # sort values
    for vals in out_d.itervalues():
        vals.sort(key=host_sort_key)
    return out_d


def print_result(execute_res):
    """ Print task results classed by return value/error code """
    import json
    result_dict = inv_dict(execute_res)
    puts(json.dumps(result_dict, indent=4))


# # # # # # # # # # # # # # # # # # # #
# Redirect the open node serial port
# # # # # # # # # # # # # # # # # # # #


@exp_task
def redirect(command='start'):
    """ Start Open A8 node m3 serial port redirection """
    assert command in ('start', 'stop')
    if command == 'start':
        return execute(restart_redirect)
    elif command == 'stop':
        return execute(stop_redirect)


@parallel
@roles('nodes')
def restart_redirect():
    """ Redirect the serial port to port 20000 """
    return run("/etc/init.d/serial_redirection restart", pty=False).return_code

@parallel
@roles('nodes')
def stop_redirect():
    """ Stop Redirect the serial port to port 20000 """
    return run("/etc/init.d/serial_redirection stop", pty=False).return_code


# # # #
# Upload file to A8 directory
# # # #
@exp_task
def upload_a8(filepath, mode=None):
    return execute(_upload_to_a8, filepath, mode=mode)


@roles('frontends')
def _upload_to_a8(filepath, mode=None):
    """ Upload the file at filepath to the frontends A8 shared directory """
    remote = '~/A8/' + os.path.basename(filepath)
    operations.put(filepath, '~/A8')
    if mode:
        run('chmod %s %s' % (mode, remote))
    return 0


# # # # # # # # # # # # # # # # # # # # # # # # # #
# Update firmware on the Open A8-M3
#
#  * Upload firmware to frontends ~/A8 directory
#  * Run the flash command on each node
#
# # # # # # # # # # # # # # # # # # # # # # # # # #


@exp_task
def update(firmware):
    """ Update the firmware on all experiment nodes """
    execute(_upload_to_a8, firmware)
    return execute(flash_firmware, firmware)

@parallel
@roles('nodes')
def flash_firmware(firmware):
    """ Flash the nodes """
    remote_firmware = '~/A8/' + os.path.basename(firmware)
    return run("flash_a8_m3 %s 2>/dev/null" % remote_firmware).return_code


# Execute with screen

@exp_task
def screen(script):
    """ Update the firmware on all experiment nodes """
    execute(_upload_to_a8, script, mode='0755')
    return execute(exec_screen, script)

@parallel
@roles('nodes')
def exec_screen(script):
    """Execute under screen."""
    remote = '~/A8/' + os.path.basename(script)
    #run('killall screen || sleep 1')
    run("screen -ls | grep Detached | cut -d. -f1 | awk '{print $1}'"
        " | xargs kill  > /dev/null 2>/dev/null"
        " && echo 'Killed' || echo 'Not killed'")
    return run('screen -d -m %s; sleep 5' % remote, pty=False).return_code


# # # # # # # # # # #
# Reset Open A8-M3
# # # # # # # # # # #


@exp_task
def reset():
    """ Reset Open A8 node m3 """
    return execute(reset_node)


@parallel
@roles('nodes')
def reset_node():
    """ Reset the node """
    return run("reset_a8_m3 2>/dev/null").return_code
