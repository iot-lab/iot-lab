#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Get all nodes UID """

UID_SCRIPT = 'get_iotlab_uid.py'

import sys
import os.path
import time
import argparse
import fabric.network
import fabric.operations
import fabric.tasks
import fabric.context_managers
import fabric.api
import fabric.utils
import traceback

import json

from iotlabcli import experiment, get_user_credentials
import iotlabcli.parser.common
from fabric.api import env

STATES = ('Alive', 'Busy')  # , 'Absent')
ARCHIS = ('m3:at86rf231', 'a8:at86rf231', 'wsn430:cc1101', 'wsn430:cc2420')

PARSER = argparse.ArgumentParser()
iotlabcli.parser.common.add_auth_arguments(PARSER)

PARSER.add_argument('--name', default='uid_experiment')
PARSER.add_argument('--duration', default=10, type=int)

PARSER.add_argument('--all-bookable', help="Run on %r nodes.\n"
                    "Default: Alive" % list(STATES),
                    action='store_true', default=False)
PARSER.add_argument('--site', action='append',
                    help="Run on SITE. Default: all")
PARSER.add_argument('--archi', choices=ARCHIS, action='append',
                    help="Run on ARCHI. Default: all")

PARSER.add_argument('--firmware-m3', dest='firmware_m3:at86rf231')
PARSER.add_argument('--firmware-a8', dest='firmware_a8:at86rf231')
PARSER.add_argument('--firmware-cc1101', dest='firmware_wsn430:cc1101')
PARSER.add_argument('--firmware-cc2420', dest='firmware_wsn430:cc2420')

PARSER.add_argument('--outfile', default='/dev/null')

env.use_ssh_config = True
env.ssh_config_path = './ssh_config'

env.reject_unknown_hosts = False
env.disable_known_hosts = True
env.abort_on_prompts = True
env.skip_bad_hosts = True


class RunExperiment(object):
    """ Run an automated experiment """

    def __init__(self, api, firmware, site, archi, all_bookable):
        env.host_string = '%s.iot-lab.info' % site

        self.api = api
        self.site = site
        self.archi = archi

        self.exp_id = None

        self.firmware = firmware
        self.states = STATES if all_bookable else ('Alive',)

        # get nodes after setting all attributes
        self.nodes = None

    def run(self, name, duration, script):
        """ Run a whole experiment """
        ret = None
        fabric.utils.puts("run_exp: %s %d %s %s %s %r" % (
            name, duration, self.site, self.archi, self.firmware,
            list(self.states)))

        try:
            self.submit_exp(name, duration)
            self.wait_exp()
            if 'a8:at86rf231' == self.archi:
                self.setup_a8_nodes()
            ret = self.run_exp(script)
        except:
            traceback.print_exc()
        finally:
            self.teardown_exp()

        return ret

    def submit_exp(self, name, duration):
        """ Submit experiment with name and duration """
        fabric.utils.puts("submit_exp")
        self.nodes = self._get_nodes_list(self.site, self.archi)
        if not self.nodes:
            raise ValueError("Empty nodes list")
        firmware = None if self.archi == 'a8:at86rf231' else self.firmware

        resources = [experiment.exp_resources(self.nodes, firmware)]
        self.exp_id = experiment.submit_experiment(self.api, name, duration,
                                                   resources)["id"]

        fabric.utils.puts("Exp-id:%d" % self.exp_id)

    def wait_exp(self):
        """ Wait experiment started """
        fabric.utils.puts("wait_exp: %i" % self.exp_id)
        time.sleep(10)  # wait 10s so that 'start date' is set
        timestamp = experiment.get_experiment(
            self.api, self.exp_id, 'start')['start_time']
        start_date = time.ctime(timestamp) if timestamp else 'Unknown'

        fabric.utils.puts("Start-date: %s" % start_date)
        experiment.wait_experiment(self.api, self.exp_id)

        if self.archi == 'a8:at86rf231':
            self.wait_a8_started()

        fabric.utils.puts("Exp-started: %s" % start_date)

    def wait_a8_started(self):
        """ Wait for A8 nodes to be booted """
        fabric.utils.puts("wait_a8_started TODO %i" % self.exp_id)
        fabric.utils.puts("sleep 500")

        # # TODO wait for A8 nodes to be started
        time.sleep(500)
        with fabric.context_managers.cd('~/.iot-lab/%s/log' % self.exp_id):
            fabric.operations.run(
                'grep "Boot A8 succeeded" --color=auto a8-*')
            fabric.operations.run(
                'grep "Boot A8 failed" a8-* --color=auto; echo ''')

    def setup_a8_nodes(self):
        """ Setup firmware and serial redirection on A8 """
        # TODO Flash the A8 node and start redirection

        fw_path = '~/A8/%s' % os.path.basename(self.firmware)
        fabric.operations.put(self.firmware, fw_path)

        fabric.tasks.execute(
            self.configure_node, fw_path,
            hosts=['node-%s' % node for node in self.nodes])

    @staticmethod
    @fabric.api.parallel(pool_size=10)
    def configure_node(fw_path):
        fabric.operations.run('flash_a8_m3 %s 2>/dev/null' % fw_path)
        fabric.operations.run("/etc/init.d/serial_redirection restart",
                              pty=False)

    def run_exp(self, script):
        """ Actually run the experiment script """
        fabric.utils.puts("run_exp %i" % self.exp_id)

        script_name = os.path.basename(script)

        fabric.operations.run('mkdir -p %d' % self.exp_id)
        with fabric.context_managers.cd('%d' % self.exp_id):
            fabric.operations.put(script, script_name, mode=0755)
            ret = fabric.operations.run(
                './%s -i %s 2>/dev/null' % (script_name, self.exp_id))
        return ret

    def teardown_exp(self):
        """ Stop experiment an cleanup stuff maybe """
        fabric.utils.puts("teardown_exp %r" % self.exp_id)
        if self.exp_id is not None:
            experiment.stop_experiment(self.api, self.exp_id)

    @staticmethod
    def targets_list(sites_dict, sites, archis):
        """ Filter sites_dict to return a list of (site, archi) tuples """
        targets = []
        for site, archi_list in sites_dict.iteritems():
            if sites is not None and site not in sites:  # filter sites
                continue
            for archi in archi_list:
                if archis is not None and archi not in archis:  # filter archis
                    continue
                targets.append((site, archi))
        return targets

    @staticmethod
    def site_archi_dict(api):
        """ Returns a dict {'site': ['archi', 'archi2']} """
        _sites_dict = {}
        res_list = experiment.info_experiment(api, False)['items']

        site_archi = ((res['network_address'].split('.')[1], res['archi'])
                      for res in res_list)
        for site, archi in set(site_archi):
            archis = _sites_dict.setdefault(site, [])
            archis.append(archi)
            archis.sort()
        return _sites_dict

    def _get_nodes_list(self, site, archi):
        """ Return a list of nodes for site, archi, state.
        If `state` defined restrict to this state,
        either choose bookable nodes """
        nodes = []

        res_list = experiment.info_experiment(self.api, False, site)['items']
        for res in res_list:
            if res['archi'] != archi:  # filter archis
                continue
            if res['state'] not in self.states:  # filter state
                continue
            nodes.append(res['network_address'])
        return nodes


@fabric.api.parallel(pool_size=4)
def run_exp(api, config, all_bookable):
    cfg = config[env.host_string]
    exps = RunExperiment(api, all_bookable=all_bookable, **cfg)
    ret = exps.run('test_uid', 10, UID_SCRIPT)
    return ret


def main():
    """ Start experiments on all sites/nodes and get the nodes uids """
    opts = PARSER.parse_args()
    try:
        user, passwd = get_user_credentials(opts.username, opts.password)
        api = iotlabcli.Api(user, passwd)
        env.user = user

        sites_dict = RunExperiment.site_archi_dict(api)
        targets = RunExperiment.targets_list(sites_dict, opts.site, opts.archi)

        # Generate config for all targets
        config = {}
        for site, archi in targets:
            firmware = vars(opts)['firmware_%s' % archi]
            if firmware is None:
                fabric.utils.puts("No firmware for %s %s" % (site, archi))
            else:
                # replace ':' in host to prevent it being interpreted as port
                config['%s-%s' % (archi.replace(':', '+'), site)] = {
                    'site': site, 'archi': archi, 'firmware': firmware
                }

        if len(config) == 0:
            raise ValueError("No valid hosts")


        result_dict = fabric.tasks.execute(
            run_exp, api, config, opts.all_bookable,
            hosts=sorted(config.keys()))

        result = {}
        for ret in result_dict.itervalues():
            if ret is not None:
                result.update(json.loads(ret))

        result_str = json.dumps(result, indent=4, sort_keys=True)


        print result_str
        with open(opts.outfile, 'w') as outfile:
            outfile.write(result_str)

#            exps = RunExperiment(api, firmware, site, archi, opts.all_bookable)
#            ret = exps.run('test_uid', 10, UID_SCRIPT)
#            if ret is not None:
#                result.update(json.loads(ret))
#
#        print json.dumps(result, indent=4, sort_keys=True)
#        with open(opts.outfile, 'w') as outfile:
#            outfile.write(json.dumps(result, indent=4, sort_keys=True))

    except:
        traceback.print_exc()
        print >> sys.stderr, sys.exc_info()

    finally:
        fabric.network.disconnect_all()


if __name__ == '__main__':
    main()
