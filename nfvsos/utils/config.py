import configparser
import os
import re


CONF_NOVA = '/etc/nova/nova.conf'
CONF_SYSTEMD = '/etc/systemd/system.conf'


def get_nova_vcpus(sosdir):
    vcpus = []
    nova_conf = os.path.join(sosdir, CONF_NOVA[1:])
    if not os.path.exists(nova_conf):
        return vcpus

    config = configparser.ConfigParser()
    config.read(nova_conf)
    try:
        vcpu_str = config.get('DEFAULT', 'vcpu_pin_set')
        negate = []
        for item in vcpu_str.split(','):
            if '-' in item:
                start = int(item.split('-')[0])
                end = int(item.split('-')[1])
                for i in range(start, end + 1):
                    vcpus.append(int(i))
            elif '^' in item or '!' in item:
                negate.append(int(item[1:]))
            else:
                vcpus.append(int(item))
        for item in negate:
            if item in vcpus:
                vcpus.remove(item)
    except configparser.NoOptionError:
        pass
    return vcpus


def get_cpu_affinity(sosdir):
    cpu_aff = []
    systemd_conf = os.path.join(sosdir, CONF_SYSTEMD[1:])
    if not os.path.exists(systemd_conf):
        return cpu_aff

    config = configparser.ConfigParser()
    config.read(systemd_conf)
    try:
        cpu_aff_str = config.get('Manager', 'CPUAffinity')
        cpu_aff = [int(item) for item in cpu_aff_str.split(' ')]
    except configparser.NoOptionError:
        pass
    return cpu_aff
