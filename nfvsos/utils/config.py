import configparser
import os
import re


NOVA_CONF = 'etc/nova/nova.conf'


def get_nova_vcpus(sosdir):
    vcpus = []
    nova_conf = os.path.join(sosdir, NOVA_CONF)
    if not os.path.exists(nova_conf):
        print(nova_conf)
        return vcpus

    config = configparser.ConfigParser()
    config.read(nova_conf)
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
    return vcpus
