import os
import re


def get_cpu_layout(sosdir):
    cpu_layout = []
    numa_node_path = os.path.join(sosdir, 'sys/devices/system/node/')
    numa_node_count = 0
    for numa_node_dir in os.listdir(numa_node_path):
        numa_node_dir_path = os.path.join(numa_node_path, numa_node_dir)
        if (os.path.isdir(numa_node_dir_path)
                and numa_node_dir.startswith("node")):
            cpu_layout.append([])
            numa_node_count += 1
    cpu_path = os.path.join(sosdir, 'sys/devices/system/cpu/')
    for cpu in os.listdir(cpu_path):
        numa_node = None
        path = os.path.join(cpu_path, cpu)
        if (not os.path.isdir(path)
                or not cpu.startswith("cpu")):
            continue
        val = cpu.split('cpu')[1]
        if not val.isdigit():
            continue
        for item in os.listdir(path):
            if not item.startswith('node'):
                continue
            if not item.strip('node').isdigit():
                continue
            numa_node = int(item.strip('node'))
        sib_path = os.path.join(path, 'topology/thread_siblings_list')
        sibs_content = _read(sib_path)
        sibs_content = sibs_content.split(',')
        for idx, val in enumerate(sibs_content):
            sibs_content[idx] = int(val)

        if sibs_content not in cpu_layout[numa_node]:
            cpu_layout[numa_node].append(sibs_content)

    return cpu_layout


def get_numa_node(cpu_layout, cpu):
    for idx, numa_list in enumerate(cpu_layout):
        for sibs in numa_list:
            if cpu in sibs:
                return idx, sibs
    return None, None


def _isol_cpus(sosdir):
    tuned_conf = os.path.join(
        sosdir, 'etc/tuned/cpu-partitioning-variables.conf')
    content = _read(tuned_conf)
    parts = re.findall(r"(^isolated_cores=([0-9,-]+)$)",
                       content, re.MULTILINE)
    isol_str = None
    isol = []
    if not parts:
        return isol
    try:
        isol_str = parts[0][1]
    except KeyError:
        LOG.info("Failed to get isolcpus list, tune config is:")
        LOG.info(content)
        LOG.info("-------------------------------------------------------")
    for item in isol_str.split(','):
        if '-' in item:
            start = int(item.split('-')[0])
            end = int(item.split('-')[1])
            for i in range(start, end):
                isol.append(int(i))
        else:
            isol.append(int(item))
    return isol


def _vcpu(sosdir):
    nova_conf = os.path.join(sosdir, 'etc/nova/nova.conf')
    content = _read(nova_conf)
    parts = re.findall(r"(^vcpu_pin_set=([0-9,-]+)$)",
                       content, re.MULTILINE)
    vcpus_str = None
    vcpus = []
    if not parts:
        return vcpus
    try:
        vcpus_str = parts[0][1]
    except KeyError:
        LOG.info("Failed to get vpcu list, tune config is:")
        LOG.info(content)
        LOG.info("-------------------------------------------------------")

    for item in vcpus_str.split(','):
        if '-' in item:
            start = int(item.split('-')[0])
            end = int(item.split('-')[1])
            for i in range(start, end + 1):
                vcpus.append(int(i))
        else:
            vcpus.append(int(item))
    return vcpus


def _read(fname):
    if not os.path.exists(fname):
        raise Exception("File (%s) is not found in the sosreport" % fname)

    with open(fname) as f:
        return f.read().strip()
