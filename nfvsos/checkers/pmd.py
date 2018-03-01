from nfvsos.checkers import Checker
from nfvsos.utils import cpu_layout
from nfvsos.utils import ovs_config

class PMDCoreListChecker(Checker):
    checker_name = 'pmd'
    checker_profiles = ('dpdk')

    def analyze(self, base_path):
        numa_layout = cpu_layout.get_cpu_layout(base_path)
        pmd_cpus = ovs_config.get_ovs_config_cores(base_path, 'pmd-cpu-mask')
        print(pmd_cpus)

    def passed(self):
        pass

    def failed(self):
        pass
