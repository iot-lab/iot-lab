""" Fabric methods to help running commands on A8 nodes """
import iotlabcli
import iotlabcli.experiment
import iotlabcli.parser.common
from fabric.api import env, run, execute
from fabric.api import task, parallel
from fabric.utils import abort, puts

version = env.version.split('.')
assert int(version[0]) <= 1 and int(version[1]) < 5, \
    "Fabric should support ssh 'gateway', should be at least version '1.5'"


# env.use_ssh_config = True
# env.ssh_config_path = './ssh_config'

#env.user = 'root'
# env.gateway = 'harter@grenoble.iot-lab.info'

def get_exp_a8_nodes(api, exp_id=None, site=''):
    """ Get the list of a8 nodes from given experiment """
    experiment = iotlabcli.experiment.get_experiment(api, exp_id)

    # select valid a8 nodes from 'site'
    nodes = [str('node-' + n) for n in experiment["deploymentresults"]["0"] if
             'a8' in n and site in n]
    if len(nodes) == 0:
        abort("No successfully deployed nodes found for" +
              " expid:site {0}:{1}".format(exp_id, site))

    sites = list(set((n.split('.', 1)[1] for n in nodes)))
    if len(sites) > 1:
        abort("Restrict nodes to one site with 'site' parameter:" +
              " {0}".format(sites))
    site = sites[0]
    return nodes, site


@task
def get_nodes_ip_addr(nodes_list):
    nodes = run("dig +short %s" % " ".join(nodes_list))
    nodes_ip_addrs = nodes.splitlines()
    hosts = ['root@' + n for n in nodes_ip_addrs]
    env.hosts = hosts


@task
def exp(exp_id=None, site=''):
    sites = iotlabcli.parser.common.sites_list()
    if site:
        if site not in sites:
            abort("Invalid site: {0}, should be in {1}".format(site, sites))
        puts("Running on nodes from site: {0}".format(site))


    username, password = iotlabcli.get_user_credentials()
    api = iotlabcli.Api(username, password)
    exp_id = iotlabcli.get_current_experiment(api, exp_id)

    nodes, gateway = get_exp_a8_nodes(api, exp_id, site)
    gateway = 'harter@' + gateway
    ip_addrs = execute(get_nodes_ip_addr, nodes, hosts=[gateway])

    puts('1')
    puts('2')

    env.user = 'root'
    env.gateway = gateway
    puts(gateway)
    puts(env.hosts)
    puts(env.user)


@task
def socat():
    run("setsid socat -d TCP4-LISTEN:20000,reuseaddr,fork " +
        " open:/dev/ttyA8_M3,b500000,echo=0,raw &")

# @parallel
@task
def hello():
    run('echo "Hello world!"')
    run('hostname')

