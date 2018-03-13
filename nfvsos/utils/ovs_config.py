import logging
import os
import re

LOG = logging.getLogger(__name__)

def get_ovs_config_socmem(sosdir):
    other_config_str = _get_ovsdb_other_config(sosdir)
    if not other_config_str:
        return []
    #value = other_config_str.split('dpdk-socket-mem=')[1]
    #value = value.strip('""')
    # print(value)
    parts = re.split('^.* (dpdk-socket-mem=.*), .*', other_config_str)
    mem_str = parts[1].strip('dpdk-socket-mem=').strip('"')
    mem_val = map(int, mem_str.split(","))
    return mem_val


def get_ovs_config_cores(sosdir, match_str):
    core_list = []
    other_config_str = _get_ovsdb_other_config(sosdir)
    if not other_config_str:
        return core_list
    value = other_config_str.split(match_str + '=')[1].split(',')[0]
    value = value.strip('""')
    bin_str = '{0:b}'.format(int(value, 16))
    for idx, val in enumerate(reversed(bin_str)):
        if int(val):
            core_list.append(idx)
    return core_list


def get_ovs_dpdk_enable_state(sosdir):
    other_config_str = _get_ovsdb_other_config(sosdir)
    if 'dpdk-init' not in other_config_str:
        LOG.error("dpdk-init is not in other_config(%s)" %
                  other_config_str)
    if other_config_str:
        value = other_config_str.split('dpdk-init=')[1].split(',')[0]
        if 'true' in value:
            return True
    return False


###############################################################################


def _get_ovsdb_other_config(sosdir):
    dname = os.path.join(sosdir, 'sos_commands/openvswitch')
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


def _read(fname):
    if not os.path.exists(fname):
        raise Exception("File (%s) is not found in the sosreport" % fname)
    with open(fname) as f:
        return f.read().strip()
