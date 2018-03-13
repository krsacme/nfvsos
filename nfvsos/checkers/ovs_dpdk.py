from nfvsos.checkers import Checker
from nfvsos.utils import ovs_config
from nfvsos.utils import tuned


CONDITIONS = [
    {
        'name': 'Enable DPDK',
        'description': 'DPDK should be enabled by setting dpdk-init in ovsdb',
        'validator': '_validate_enable_dpdk'
    },
    {
        'name': 'Socket Memory',
        'description': 'Socket Memory should be set according to MTU and NUMA',
        'validator': '_validate_socket_mem'
    },
    {
        'name': 'OvS lcore',
        'description': 'OvS lcore should not be isolated',
        'validator': '_validate_lcore_no_isolation'
    }
]


class DpdkConfigChecker(Checker):
    checker_name = 'ovs_dpdk'
    checker_profiles = ('dpdk')

    def __init__(self, commons):
        super(DpdkConfigChecker, self).__init__(commons)
        self.conditions = CONDITIONS

    def _validate_enable_dpdk(self, data):
        status = True
        error = None

        if not ovs_config.get_ovs_dpdk_enable_state(self.sosdir):
            status = False
            error = "DPDK is not enabled in ovsdb config (other_config:dpdk-init)"
        return status, error

    def _validate_socket_mem(self, data):
        return False, None

    def _validate_lcore_no_isolation(self, data):
        lcores = ovs_config.get_ovs_config_cores(
            self.sosdir, 'dpdk-lcore-mask')
        if not lcores:
            error = "No CPUs configured as OVS-DPDK lcores"
            return False, error

        isol_cores = tuned.get_tuned_isolated_cores(self.sosdir)
        overlap = [core for core in lcores if core in isol_cores]
        if not isol_cores:
            status = False
            error = "Tuned isolated cores is not configured"
        elif overlap:
            status = False
            error = ("Lcores (%s) is added to tuned isolated cores list, but "
                     "Lcores should not be isolated" %
                     (','.join([int(i) for i in overlap])))

        return status, error
