import json
import logging
import os
import re
import sys

import utils
import condition

LOG = logging.getLogger(__name__)

NUMBER_OF_PMD_PHYSICAL_CORES = 1


class DpdkConfig(object):

    def __init__(self):
        self.pmd = []
        self.host = []
        self.isol = []
        self.vcpu = []
        self.socmem = []

    def dump(self):
        LOG.info(" PMD Cores: %s" % ','.join(map(str, self.pmd)))
        LOG.info("OVSL Cores: %s" % ','.join(map(str, self.host)))
        LOG.info("Isol Cores: %s" % ','.join(map(str, self.isol)))
        LOG.info("Vcpu Cores: %s" % ','.join(map(str, self.vcpu)))
        LOG.info("Sock Memor: %s" % ','.join(map(str, self.socmem)))


class DpdkTripleOAnalyzer(object):

    def __init__(self, sosdir):
        self.sosdir = sosdir
        self.utils = utils.SosAnalyzerUtils(sosdir)
        self.conditions = condition.DpdkConditions()
        self.hostname = None
        self.dpdk_enabled = False
        self.dpdk_actual = DpdkConfig()
        self.dpdk_recomm = DpdkConfig()

    def analyze(self):
        self._read_hostname()
        self.dpdk_enabled = self._is_dpdk_enabled()
        if self.dpdk_enabled:
            LOG.info("DPDK is enabled in OVS")
            self._validate_config()
        else:
            LOG.error("DPDK is not enabled in OpenvSwitch (dpdk-init)")

    def _validate_config(self):
        self._validate_core_lists()

    def _recommended_config(self):
        cpu_layout = self.utils.cpu_layout
        for numa in cpu_layout:
            cpu_list = sorted(numa)
            self.dpdk_recomm.host.extend(cpu_list[0])
            for i in range(1, NUMBER_OF_PMD_PHYSICAL_CORES + 1):
                # TODO: Identify which numa has DPDK nic associated
                self.dpdk_recomm.pmd.extend(cpu_list[i])

    def _validate_core_lists(self):
        # self.dpdk_actual
        cpu_layout = self.utils.cpu_layout
        self.dpdk_actual.host = self._get_ovs_config_cores('dpdk-lcore-mask')
        self.dpdk_actual.pmd = self._get_ovs_config_cores('pmd-cpu-mask')
        self.dpdk_actual.isol = self.utils.isol_cpus
        self.dpdk_actual.vcpu = self.utils.vcpu_list
        self.dpdk_actual.socmem = self._get_ovs_config_socmem()
        self.dpdk_actual.dump()

        self.conditions.c1_pmd_in_both_numa(self.dpdk_actual.pmd, cpu_layout)

    def _get_ovs_config_socmem(self):
        other_config_str = self._get_ovsdb_other_config()
        #value = other_config_str.split('dpdk-socket-mem=')[1]
        #value = value.strip('""')
        # print(value)
        parts = re.split('^.* (dpdk-socket-mem=.*), .*', other_config_str)
        mem_str = parts[1].strip('dpdk-socket-mem=').strip('"')
        mem_val = map(int, mem_str.split(","))
        return mem_val

    def _get_ovs_config_cores(self, match_str):
        other_config_str = self._get_ovsdb_other_config()
        value = other_config_str.split(match_str + '=')[1].split(',')[0]
        value = value.strip('""')
        bin_str = '{0:b}'.format(int(value, 16))
        core_list = []
        for idx, val in enumerate(reversed(bin_str)):
            if int(val):
                core_list.append(idx)
        return core_list

    def _read_hostname(self):
        fname = os.path.join(self.sosdir, 'hostname')
        self.hostname = self._read(fname)
        print("Hostname: %s" % self.hostname)

    def _is_dpdk_enabled(self):
        other_config_str = self._get_ovsdb_other_config()
        if 'dpdk-init' not in other_config_str:
            LOG.error("dpdk-init is not in other_config(%s)" %
                      other_config_str)
        value = other_config_str.split('dpdk-init=')[1].split(',')[0]
        if 'true' in value:
            return True

    def _get_ovsdb_other_config(self):
        dname = os.path.join(self.sosdir, 'sos_commands/openvswitch')
        fname = None
        for i in os.listdir(dname):
            name = os.path.join(dname, i)
            if (os.path.isfile(name) and i.startswith('ovsdb-client')):
                fname = name
                break
        if not fname:
            return None
        lines = []

        # Gets the conent of 'Open_vSwitch table' section in ovsdb-client dump
        with open(fname) as f:
            matching = False
            for line in f:
                if matching:
                    line = line.strip()
                    if not line:
                        break
                    lines.append(line)
                elif line.startswith('Open_vSwitch table'):
                    matching = True

        # Gets the 'other-config' value in 'Open_vSwitch table'
        configs = []
        for line in lines:
            if 'other_config' in line:
                return line.split(':')[1].strip("'{} ")

    def _read(self, fname):
        if not os.path.exists(fname):
            raise Exception("File (%s) is not found in the sosreport" % fname)
        with open(fname) as f:
            return f.read().strip()
