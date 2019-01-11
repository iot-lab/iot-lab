#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Get all nodes UID """


import sys
import os.path
import time
import tempfile
import json
import multiprocessing
import traceback

import argparse
from fabric.api import env
import fabric.network
import fabric.operations
import fabric.tasks
import fabric.context_managers
import fabric.api
import fabric.utils
import fabric.decorators

from iotlabcli import experiment, get_user_credentials
import iotlabcli.parser.common

# Issue with pylint context_managers
# pylint:disable=not-context-manager


SCRIPT_DIR = os.path.relpath(os.path.dirname(__file__))
UTILS_DIR = os.path.join(SCRIPT_DIR, 'utils')

ANSI_RESET = '\x1b[0m'

FW_DIR = os.path.join(SCRIPT_DIR, 'firmwares/')
if not os.path.isdir(FW_DIR):
    fabric.utils.puts('Cannot find firmwares folder, run:')
    fabric.utils.puts('    make -C ../.. setup-iot-lab.wiki')
    exit(1)

FW_DICT = {
    'm3:at86rf231': os.path.join(FW_DIR, 'm3_print_uids.elf'),
    'a8:at86rf231': os.path.join(FW_DIR, 'a8_print_uids.elf'),
    'wsn430:cc1101': os.path.join(FW_DIR, 'wsn430_print_uids.hex'),
    'wsn430:cc2420': os.path.join(FW_DIR, 'wsn430_print_uids.hex'),
    'samr21:at86rf233': os.path.join(FW_DIR, 'samr21_print_uids.elf'),
    'arduino-zero:xbee': os.path.join(FW_DIR, 'arduino-zero_print_uids.elf'),
    'st-lrwan1:sx1276': os.path.join(FW_DIR, 'st-lrwan1_print_uids.elf'),
    'st-iotnode:multi': os.path.join(FW_DIR, 'st-iotnode_print_uids.elf'),
    'nrf52dk:ble': os.path.join(FW_DIR, 'nrf52dk_print_uids.elf'),
    'nrf52840dk:multi': os.path.join(FW_DIR, 'nrf52840dk_print_uids.elf'),
    'nrf51dk:ble': os.path.join(FW_DIR, 'nrf51dk_print_uids.elf'),
    'frdm-kw41z:multi': os.path.join(FW_DIR, 'frdm-kw41z_print_uids.elf'),
    'samr30:at86rf212b': os.path.join(FW_DIR, 'samr30_print_uids.elf'),
    'microbit:ble': os.path.join(FW_DIR, 'microbit_print_uids.elf'),
    'phynode:kw2xrf': os.path.join(FW_DIR, 'phynode_print_uids.elf'),
    'nrf52840mdk:multi': os.path.join(FW_DIR, 'nrf52840mdk_print_uids.elf'),
    'firefly:multi': os.path.join(FW_DIR, 'firefly_print_uids.elf'),
}


STATES = ('Alive', 'Busy')  # , 'Absent')
ARCHIS = ('m3:at86rf231', 'a8:at86rf231', 'wsn430:cc1101', 'wsn430:cc2420')

PARSER = argparse.ArgumentParser()
iotlabcli.parser.common.add_auth_arguments(PARSER)

PARSER.add_argument('--name', default='uid_experiment')
PARSER.add_argument('--duration', default=60, type=int)

PARSER.add_argument('-o', '--outfile', default='/dev/null')

# Restrict nodes to sites/state
SELECT_PARSER = PARSER.add_argument_group('Nodes selection on site/state')
SELECT_PARSER.add_argument('--all-bookable', help="Run on %r nodes.\n"
                           "Default: Alive" % list(STATES),
                           action='store_true', default=False)
SELECT_PARSER.add_argument('--site', action='append',
                           help="Run on SITE. Default: all")

# Restrict nodes to archis
NODE_PARSER = PARSER.add_argument_group('Nodes architectures to run on')
NODE_PARSER.add_argument('--m3:at86rf231', '--m3', action='store_true')
NODE_PARSER.add_argument('--a8:at86rf231', '--a8', action='store_true')
NODE_PARSER.add_argument('--wsn430:cc1101', '--cc1101', action='store_true')
NODE_PARSER.add_argument('--wsn430:cc2420', '--cc2420', action='store_true')
NODE_PARSER.add_argument('--samr21:at86rf233', '--samr21', action='store_true')
NODE_PARSER.add_argument('--arduino-zero:xbee', '--arduino-zero',
                         action='store_true')
NODE_PARSER.add_argument('--st-lrwan1:sx1276', '--st-lrwan1',
                         action='store_true')
NODE_PARSER.add_argument('--st-iotnode:multi', '--st-iotnode',
                         action='store_true')
NODE_PARSER.add_argument('--nrf52dk:ble', '--nrf52dk', action='store_true')
NODE_PARSER.add_argument('--nrf52840dk:multi', '--nrf52840dk',
                         action='store_true')
NODE_PARSER.add_argument('--nrf51dk:ble', '--nrf51dk', action='store_true')
NODE_PARSER.add_argument('--frdm-kw41z:multi', '--frdm-kw41z',
                         action='store_true')
NODE_PARSER.add_argument('--samr30:at86rf212b', '--samr30',
                         action='store_true')
NODE_PARSER.add_argument('--microbit:ble', '--microbit', action='store_true')
NODE_PARSER.add_argument('--phynode:kw2xrf', '--phynode', action='store_true')
NODE_PARSER.add_argument('--nrf52840mdk:multi', '--nrf52840mdk',
                         action='store_true')
NODE_PARSER.add_argument('--firefly:multi', '--firefly', action='store_true')

UID_SCRIPT = os.path.join(UTILS_DIR, 'get_iotlab_uid.py')

env.reject_unknown_hosts = False
env.disable_known_hosts = True
# env.abort_on_prompts = True
env.skip_bad_hosts = True


def use_custom_ssh_config(username):
    """Use generated ssh config for fabric."""
    utils_ssh_file = os.path.join(UTILS_DIR, 'ssh_config')
    env.ssh_config_path = ssh_config(username, utils_ssh_file)
    env.use_ssh_config = True


def ssh_config(username, filepath=None):
    """Generate ssh config for username and return it's path.
    If `filepath` is given, it is used instead of creating a temporary file.

    :return: config file path
    """
    try:
        cfg_file = open(filepath, 'w+')
    except TypeError:
        # delete=False as the reference will be lost but file should remain
        cfg_file = tempfile.NamedTemporaryFile('w+', delete=False)
        filepath = cfg_file.name

    sites = iotlabcli.parser.common.sites_list()

    cfg_file.write('Host node-a8-*\n')
    cfg_file.write('  User root\n')
    cfg_file.write('  StrictHostKeyChecking no\n')
    cfg_file.write('\n')

    for site in sites:
        cfg_file.write('# Use ssh frontend as proxy\n')
        cfg_file.write('Host *.%s*\n' % site)
        cfg_file.write('  ProxyCommand ssh %s.iot-lab.info -W %%h:%%p\n' %
                       site)
        cfg_file.write('\n')

    cfg_file.write('# Iot-Lab username for frontends\n')
    cfg_file.write('Host *\n')
    cfg_file.write('  User %s\n' % username)
    cfg_file.write('\n')

    return filepath


class RunExperiment(object):
    """ Run an automated experiment """

    def __init__(self,  # pylint:disable=too-many-arguments
                 api, firmware, site, archi, all_bookable):
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
        full_name = '%s_%s_%s' % (name, self.site, self.archi.split(':')[0])
        ret = None
        fabric.utils.puts("run_exp: %s %d %s %s %s %r" % (
            full_name, duration, self.site, self.archi, self.firmware,
            list(self.states)))

        try:
            self.submit_exp(full_name, duration)
            self.wait_exp()
            if self.archi == 'a8:at86rf231':
                setup_ret = self.setup_a8_nodes()
                if 0 not in setup_ret.values():
                    raise StandardError("Setup A8 failed for all")
            ret = self.run_exp(script)
        except:  # pylint:disable=bare-except
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
    @fabric.decorators.with_settings(warn_only=True)
    def _num_a8_booted_nodes(log_path):
        """ Return a tuple with the number of experiment started a8 nodes
        with num of booted nodes """
        with fabric.api.hide('warnings'):
            with fabric.context_managers.cd(log_path):
                # use cat to get count in one line
                ok_nodes = fabric.operations.run(
                    'cat a8_* | grep -c "Start experiment succeeded"')
                booted = fabric.operations.run(
                    'cat a8_* | grep -c "Boot A8 succeeded"')
        return int(ok_nodes), int(booted)

    @staticmethod
    @fabric.decorators.with_settings(warn_only=True)
    def _print_a8_booted_nodes(log_path):
        """ Print booted and boot failed nodes """
        with fabric.api.hide('warnings'):
            with fabric.context_managers.cd(log_path):
                fabric.operations.run(
                    'grep "Boot A8 succeeded" --color=auto a8_*')
                fabric.operations.run(
                    'grep "Boot A8 failed" --color=auto a8_* ''')

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

            if num_ok == num_booted:
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
    def targets_list(sites_dict, sites):
        """ Filter sites_dict to return a list of (site, archi) tuples """
        targets = []
        for site, archi_list in sites_dict.iteritems():
            if sites is not None and site not in sites:  # filter sites
                continue
            for archi in archi_list:
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

    user, passwd = get_user_credentials(opts.username, opts.password)
    api = iotlabcli.Api(user, passwd)
    use_custom_ssh_config(user)

    fabric.utils.puts("Get platform nodes...")
    sites_dict = RunExperiment.site_archi_dict(api)
    targets = RunExperiment.targets_list(sites_dict, opts.site)

    # Generate config for all targets
    config = {}
    for site, archi in targets:
        # replace ':' in host to prevent it being interpreted as port
        host = '%s-%s' % (archi.replace(':', '+'), site)
        if vars(opts).get(archi.replace('-', '_'), False):
            config[host] = {
                'site': site, 'archi': archi, 'firmware': FW_DICT[archi],
            }
        else:
            fabric.utils.puts("Ignore %s %s" % (site, archi))

    if len(config) == 0:
        fabric.utils.abort("No valid hosts")

    try:
        result_dict = fabric.tasks.execute(
            run_exp, api, opts.name, opts.duration, config, opts.all_bookable,
            hosts=sorted(config.keys()))

        result = {}
        for ret in result_dict.values():
            if ret is not None:
                if ret.endswith(ANSI_RESET):
                    # Remove ANSI_RESET if at the end, got it on devlille
                    ret = ret.replace(ANSI_RESET, '')
                try:
                    result.update(json.loads(ret))
                except ValueError:
                    print >> sys.stderr, 'Error loading ret as json %r' % ret

        result_str = json.dumps(result, indent=4, sort_keys=True)

        print result_str
        with open(opts.outfile, 'w') as outfile:
            outfile.write(result_str)

    except:  # pylint:disable=bare-except
        traceback.print_exc()
        print >> sys.stderr, sys.exc_info()
    finally:
        fabric.network.disconnect_all()


if __name__ == '__main__':
    main()
