from nfvsos.checkers import Checker
from nfvsos.utils import config
from nfvsos.utils import cpu_layout
from nfvsos.utils import tuned
from nfvsos.utils import utilities


CONDITIONS = [
    {
        'name': 'Siblings',
        'description': 'Sibling threads should be associated together',
        'validator': '_validate_vcpu_siblings'
    },
    {
        'name': 'Tuned Isolation',
        'description': 'Nova Vcpus should be isolated using tuned',
        'validator': '_validate_vcpu_isolate'
    }
]


class VpcuListChecker(Checker):
    checker_name = 'vcpu'
    checker_profiles = ('dpdk')

    def __init__(self, commons):
        super(VpcuListChecker, self).__init__(commons)
        self.conditions = CONDITIONS

    def analyze(self):
        print("KRS: HERE")
        numa_layout = cpu_layout.get_cpu_layout(self.sosdir)
        vpcus = config.get_nova_vcpus(self.sosdir)
        data = {
            'numa_layout': numa_layout,
            'vpcus': vpcus
        }
        super(VpcuListChecker, self).analyze(data)

    def _validate_vcpu_siblings(self, data):
        status = True
        error = None
        missing_siblings = {}
        vpcus = data['vpcus']
        if not vpcus:
            error = "No CPUs configured as vcpu_pin_set"
            return False, error

        numa_layout = data['numa_layout']
        cpus_in_numa = []
        for item in enumerate(numa_layout):
            cpus_in_numa.append(0)
        for item in vpcus:
            node, sibs = cpu_layout.get_numa_node(numa_layout, item)
            cpus_in_numa[node] += 1
            sibs.remove(item)
            for i in sibs:
                if i not in vpcus:
                    missing_siblings.update({item: i})
        if missing_siblings:
            status = False
            error = ["CPUs({0})'s sibling ({1}) is not added in PMD list".format(
                k, v) for k, v in missing_siblings.items()]
        return status, error

    def _validate_vcpu_isolate(self, data):
        status = True
        error = None
        vpcus = data['vpcus']
        if not vpcus:
            error = "No CPUs configured as vcpu_pin_set"
            return False, error

        tuned_isol = tuned.get_tuned_isolated_cores(self.sosdir)
        missing = []
        for item in vpcus:
            if item not in tuned_isol:
                missing.append(item)
        if missing:
            status = False
            missing_str = utilities.convert_to_range(missing)
            error=("CPUs (%s) should be added to tuned isolation "
                     "config (%s) " % (missing_str,
                                       tuned.TUNED_CPU_CONFIG))
        return status, error
