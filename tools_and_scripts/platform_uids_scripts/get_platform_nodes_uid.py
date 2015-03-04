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
import multiprocessing

from iotlabcli import experiment, get_user_credentials
import iotlabcli.parser.common
from fabric.api import env

STATES = ('Alive', 'Busy')  # , 'Absent')
ARCHIS = ('m3:at86rf231', 'a8:at86rf231', 'wsn430:cc1101', 'wsn430:cc2420')

PARSER = argparse.ArgumentParser()
iotlabcli.parser.common.add_auth_arguments(PARSER)

PARSER.add_argument('--name', default='uid_experiment')
PARSER.add_argument('--duration', default=60, type=int)

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
                setup_ret = self.setup_a8_nodes()
                if 0 not in setup_ret.values():
                    raise StandardError("Setup A8 failed for all")
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

    @staticmethod
    def _num_a8_booted_nodes(log_path):
        """ Return a tuple with the number of experiment started a8 nodes
        with num of booted nodes """
        with fabric.api.settings(warn_only=True):
            with fabric.context_managers.cd(log_path):
                # use cat to get count in one line
                ok_nodes = fabric.operations.run(
                    'cat a8-* | grep -c "Start experiment succeeded"')
                booted = fabric.operations.run(
                    'cat a8-* | grep -c "Boot A8 succeeded"')
        return int(ok_nodes), int(booted)

    @staticmethod
    def _print_a8_booted_nodes(log_path):
        """ Print booted and boot failed nodes """
        with fabric.api.settings(warn_only=True):
            with fabric.context_managers.cd(log_path):
                fabric.operations.run(
                    'grep "Boot A8 succeeded" --color=auto a8-*')
                fabric.operations.run(
                    'grep "Boot A8 failed" --color=auto a8-* ''')

    def wait_a8_started(self, num_loop_max=20, step=30):
        """ Wait for A8 nodes to be booted

        We wait either for minimum of:
         * max time == num_loop_max * step
         * All nodes booted
         * More than half A8 booted and no more nodes booted since last loop

        :param step: duration between each check in seconds
        :param num_loop_max: number of loop to wait at max
        """

        fabric.utils.puts("wait_a8_started %i" % self.exp_id)
        log_path = '~/.iot-lab/%s/log' % self.exp_id

        old_num_booted = 0
        for i in range(num_loop_max, 0, -1):
            fabric.utils.puts("Remaining sleep %i" % (i * step))
            time.sleep(step)
            num_ok, num_booted = self._num_a8_booted_nodes(log_path)

            if (num_ok == num_booted):
                break  # all booted
            if ((num_ok / 2) < num_booted) and (old_num_booted == num_booted):
                # no new nodes booted since last time and more than half did
                break

            # keep waiting
            old_num_booted = num_booted

        self._print_a8_booted_nodes(log_path)

    def setup_a8_nodes(self):
        """ Setup firmware and serial redirection on A8 """

        fw_path = '~/A8/%s' % os.path.basename(self.firmware)
        fabric.operations.put(self.firmware, fw_path)

        return fabric.tasks.execute(
            self.configure_a8_node, fw_path,
            hosts=['node-%s' % node for node in self.nodes])

    @staticmethod
    @fabric.api.parallel(pool_size=multiprocessing.cpu_count())
    def configure_a8_node(fw_path):
        """ Configure a8 node """
        fabric.operations.run('flash_a8_m3 %s 2>/dev/null' % fw_path)
        fabric.operations.run('/etc/init.d/serial_redirection restart',
                              pty=False)
        return 0

    def run_exp(self, script):
        """ Actually run the experiment script """
        fabric.utils.puts("run_exp %i" % self.exp_id)

        script_name = os.path.basename(script)

        fabric.operations.run('mkdir -p %d' % self.exp_id)
        with fabric.context_managers.cd('%d' % self.exp_id):
            fabric.operations.put(script, script_name, mode=0755)
            ret = fabric.operations.run(
                './%s -i %s 2>log' % (script_name, self.exp_id))
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


# give 2 * a8_ssh connections == 2 * cpu_count
@fabric.api.parallel(pool_size=2)
def run_exp(api, name, duration, config, all_bookable):
    """ Run an experiment """
    cfg = config[env.host_string]
    exps = RunExperiment(api, all_bookable=all_bookable, **cfg)
    ret = exps.run(name, duration, UID_SCRIPT)
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
            run_exp, api, opts.name, opts.duration, config, opts.all_bookable,
            hosts=sorted(config.keys()))

        result = {}
        for ret in result_dict.values():
            if ret is not None:
                result.update(json.loads(ret))
        result_str = json.dumps(result, indent=4, sort_keys=True)

        print result_str
        with open(opts.outfile, 'w') as outfile:
            outfile.write(result_str)

    except:
        traceback.print_exc()
        print >> sys.stderr, sys.exc_info()

    finally:
        fabric.network.disconnect_all()


if __name__ == '__main__':
    main()
