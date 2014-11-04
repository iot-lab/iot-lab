""" Fabric methods to help running commands on A8 nodes """
import os
import iotlabcli
import iotlabcli.experiment
import iotlabcli.parser.common
from fabric.api import env, run, execute
from fabric.api import task, parallel, roles, runs_once
from fabric.utils import abort
from fabric import operations

_VERSION = (int(n) for n in env.version.split('.'))
assert (1, 5, 0) >= _VERSION, \
    ("Fabric should support ssh 'gateway'. Should be at least version '1.5'" +
     ": %r" % env.version)
# Debug paramiko
# import logging
# logging.basicConfig(level=logging.DEBUG)
# Debug paramiko


env.use_ssh_config = True
env.ssh_config_path = './ssh_config'

env.reject_unknown_hosts = False
env.disable_known_hosts = True
env.abort_on_prompts = True

env.colorize_errors = True
env.pool_size = 10


def _get_exp_a8_nodes(api, exp_id=None):
    """ Get the list of a8 nodes from given experiment """
    experiment = iotlabcli.experiment.get_experiment(api, exp_id)
    _working_nodes = experiment["deploymentresults"]["0"]

    # select valid a8 nodes from 'site'
    nodes = [str('node-' + n) for n in _working_nodes if n.startswith('a8')]
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
    @task(name=func.__name__)
    def wrapper(*args, **kwargs):
        """ wrapper that calls 'exp' before actual task """
        execute(exp, exp_id=None)
        func(*args, **kwargs)
    wrapper.__doc__ = func.__doc__

    return wrapper


# # # # # # # # # # # # # # # # # # # #
# Redirect the open node serial port
# # # # # # # # # # # # # # # # # # # #


@exp_task
def redirect():
    """ Start Open A8 node m3 serial port redirection """
    execute(restart_redirect)


@parallel
@roles('nodes')
def restart_redirect():
    """ Redirect the serial port to port 20000 """
    run("/etc/init.d/serial_redirection restart", pty=False)


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
    execute(upload_firmware, firmware)
    execute(flash_firmware, firmware)


@parallel
@roles('frontends')
def upload_firmware(firmware):
    """ Upload the firmware to the frontends A8 shared directory """
    operations.put(firmware, '~/A8')


@parallel
@roles('nodes')
def flash_firmware(firmware):
    """ Flash the nodes """
    remote_firmware = '~/A8/' + os.path.basename(firmware)
    run("flash_a8_m3 %s 2>/dev/null" % remote_firmware)


# # # # # # # # # # #
# Reset Open A8-M3
# # # # # # # # # # #


@exp_task
def reset():
    """ Reset Open A8 node m3 """
    execute(reset_node)


@parallel
@roles('nodes')
def reset_node():
    """ Reset the node """
    run("reset_a8_m3 2>/dev/null")
