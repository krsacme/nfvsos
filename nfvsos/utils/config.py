import configparser
import os
import re

CONF_NOVA = '/etc/nova/nova.conf'
CONF_SYSTEMD = '/etc/systemd/system.conf'


def get_container_name(conf_file):
    if 'nova.conf' in conf_file:
        return 'nova_libvirt'
    raise Exception(
        'Unknown conf file (%s) to get the container name' % conf_file)


def get_conf_path(sosdir, conf_file):
    config_data = os.path.join(sosdir, 'var/lib/config-data')
    if os.path.exists(config_data):
        # Container based deployment
        container = get_container_name(conf_file)
        return os.path.join(sosdir, 'var/lib/config-data/puppet-generated',
                            container, conf_file)
    else:
        # Baremetal service based deployment
        return os.path.join(sosdir, conf_file)


def get_nova_vcpus(sosdir):
    vcpus = []
    nova_conf = get_conf_path(sosdir, CONF_NOVA[1:])
    if not os.path.exists(nova_conf):
        raise Exception('Conf file (%s) is not found!' % nova_conf)

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
