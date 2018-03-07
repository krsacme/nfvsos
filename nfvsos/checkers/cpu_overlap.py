# Ensure proper CPU partition with PMD and VPCU

from nfvsos.checkers import Checker
from nfvsos.utils import config
from nfvsos.utils import cpu_layout
from nfvsos.utils import ovs_config
from nfvsos.utils import tuned


CONDITIONS = [
    {
        'name': 'No Overlap (PMD and VCPU)',
        'description': 'No overlap of cpus between OVS-DPDK PMD and Nova '
        'vcpu_pin_set configs',
        'validator': '_validate_overlap_pmd_vcpu'
    }
]


class CpuOverlapChecker(Checker):
    checker_name = 'cpu_overlap'
    checker_profiles = ('dpdk')

    def __init__(self, commons):
        super(CpuOverlapChecker, self).__init__(commons)
        self.conditions = CONDITIONS

    def _validate_overlap_pmd_vcpu(self, data):
        status = True
        error = None
        vcpu = config.get_nova_vcpus(self.sosdir)
        pmd = ovs_config.get_ovs_config_cores(self.sosdir, 'pmd-cpu-mask')
        overlap = [i for i in pmd if i in vcpu]
        if overlap:
            status = False
            error = ("CPUs ({0}) of PMD overlap with Nova VCPUs".format(
                ','.join([str(i) for i in overlap])))
        return status, error
