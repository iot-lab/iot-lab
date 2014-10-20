""" Fabric methods to help running commands on A8 nodes """
import iotlabcli
import iotlabcli.experiment
import iotlabcli.parser.common
from fabric.api import env, run, execute
from fabric.api import task, parallel
from fabric.utils import abort, puts
version = (int(n) for n in env.version.split('.'))
assert (1, 5, 0) >= version, \
    ("Fabric should support ssh 'gateway'. Should be at least version '1.5'" +
     ": %r" % env.version)
# Debug paramiko
# import logging
# logging.basicConfig(level=logging.DEBUG)
# Debug paramiko


env.user = 'harter'


env.use_ssh_config = True
env.ssh_config_path = './ssh_config'

env.reject_unknown_hosts = False
env.disable_known_hosts = True

env.pool_size = 10

def get_exp_a8_nodes(api, exp_id=None):
    """ Get the list of a8 nodes from given experiment """
    experiment = iotlabcli.experiment.get_experiment(api, exp_id)
    _working_nodes = experiment["deploymentresults"]["0"]

    # select valid a8 nodes from 'site'
    nodes = [str('node-' + n) for n in _working_nodes if n.startswith('a8')]
    if not nodes:
        abort("No successfully deployed A8 nodes found for exp:%u" % exp_id)
    return nodes


@task
def exp(exp_id=None):
    """ Extract nodes from experiment and set ennv.hosts """
    username, password = iotlabcli.get_user_credentials()
    api = iotlabcli.Api(username, password)
    exp_id = iotlabcli.get_current_experiment(api, exp_id)

    nodes = get_exp_a8_nodes(api, exp_id)
    env.hosts = nodes

@task
@parallel
def socat():
    run("killall -q socat; sleep 1")
    run("nohup socat -d TCP4-LISTEN:20000,reuseaddr,fork " +
        " open:/dev/ttyA8_M3,b500000,echo=0,raw </dev/null >/tmp/socat_log &",
        pty=False)

@task
@parallel
def hello():
    """ Simple hello world example """
    run('printf "Hello world!"')

