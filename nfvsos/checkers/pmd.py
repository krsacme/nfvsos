from nfvsos.checkers import Checker
from nfvsos.utils import cpu_layout
from nfvsos.utils import ovs_config
from nfvsos.utils import tuned


CONDITIONS = [
    {
        'name': 'PMD on each NUMA',
        'description': 'PMD Cores should be allocated on each of the NUMA node',
        'validator': '_validate_pmd_on_each_numa'
    },
    {
        'name': 'Siblings',
        'description': 'Sibling threads to be associated together',
        'validator': '_validate_pmd_siblings'
    },
    {
        'name': 'Tuned Isolation',
        'description': 'PMD Cores should be isolated using tuned',
        'validator': '_validate_pmd_isolate'
    }
]


class PMDCoreListChecker(Checker):
    checker_name = 'pmd'
    checker_profiles = ('dpdk')

    def __init__(self, commons):
        super(PMDCoreListChecker, self).__init__(commons)
        self.conditions = CONDITIONS

    def analyze(self):
        numa_layout = cpu_layout.get_cpu_layout(self.sosdir)
        pmd_cpus = ovs_config.get_ovs_config_cores(self.sosdir, 'pmd-cpu-mask')
        data = {
            'numa_layout': numa_layout,
            'pmd_cpus': pmd_cpus
        }
        super(PMDCoreListChecker, self).analyze(data)

    def _validate_pmd_on_each_numa(self, data):
        status = True
        error = None
        pmd_cpus = data['pmd_cpus']
        numa_layout = data['numa_layout']

        if not pmd_cpus:
            error = "No CPUs configured as OVS-DPDK PMD cores"
            return False, error

        cpus_in_numa = []
        for item in enumerate(numa_layout):
            cpus_in_numa.append(0)
        for item in pmd_cpus:
            node, sibs = cpu_layout.get_numa_node(numa_layout, item)
            cpus_in_numa[node] += 1

        if 0 in cpus_in_numa:
            status = False
            err_numas = ', '.join(
                [str(k) for k, v in enumerate(cpus_in_numa) if v == 0])
            error = ("Numa (%s) does not have any PMD CPUs allocated" %
                     err_numas)
        return status, error

    def _validate_pmd_siblings(self, data):
        status = True
        error = None
        missing_siblings = {}
        pmd_cpus = data['pmd_cpus']
        numa_layout = data['numa_layout']
        if not pmd_cpus:
            error = "No CPUs configured as OVS-DPDK PMD cores"
            return False, error

        cpus_in_numa = []
        for item in enumerate(numa_layout):
            cpus_in_numa.append(0)
        for item in pmd_cpus:
            node, sibs = cpu_layout.get_numa_node(numa_layout, item)
            cpus_in_numa[node] += 1
            sibs.remove(item)
            for i in sibs:
                if i not in pmd_cpus:
                    missing_siblings.update({item: i})
        if missing_siblings:
            status = False
            error = ["CPUs({0})'s sibling ({1}) is not added in PMD list".format(
                k, v) for k, v in missing_siblings.items()]
        return status, error

    def _validate_pmd_isolate(self, data):
        status = True
        error = None
        pmd_cpus = data['pmd_cpus']
        if not pmd_cpus:
            error = "No CPUs configured as OVS-DPDK PMD cores"
            return False, error

        tuned_isol = tuned.get_tuned_isolated_cores(self.sosdir)
        missing = []
        for item in pmd_cpus:
            if item not in tuned_isol:
                missing.append(item)
        if missing:
            status = False
            error = ("CPUs (%s) should be added to tuned isolation "
                     "config (%s) " % (', '.join([str(i) for i in missing]),
                                       tuned.TUNED_CPU_CONFIG))
        return status, error
