from nfvsos.checkers import Checker
from nfvsos.utils import config
from nfvsos.utils import cpu_layout
from nfvsos.utils import system
from nfvsos.utils import tuned

TUNED_PROFILE_NAME = 'cpu-partitioning'

CONDITIONS = [
    {
        'name': 'First core on all numa as CPUAffinity',
        'description': 'CPUAffinity should contain first cores from all numa',
        'validator': '_validate_cpu_affinity'
    },
    {
        'name': 'Tuned Active Profile',
        'description': 'Tuned Profile should be active with right profile',
        'validator': '_validate_active_profile'
    },
    {
        'name': 'Tuned Config in cmdline',
        'description': 'Tuned config should be applied on /proc/cmdline',
        'validator': '_validate_cmdline_config',
        'matchers': ['tuned.non_isolcpus', 'nohz_full', 'rcu_nocbs']
    },

]


class TunedChecker(Checker):
    checker_name = 'tuned'
    checker_profiles = ('dpdk')

    def __init__(self, commons):
        super(TunedChecker, self).__init__(commons)
        self.conditions = CONDITIONS

    def analyze(self):
        numa_layout = cpu_layout.get_cpu_layout(self.sosdir)
        data = {
            'numa_layout': numa_layout,
        }
        super(TunedChecker, self).analyze(data)

    def _validate_cpu_affinity(self, data):
        status = True
        error = None
        numa_layout = data['numa_layout']
        first_cores = []
        cpus_in_numa = []
        for item in numa_layout:
            first_cores.extend(sorted(item)[0])

        cpu_aff = config.get_cpu_affinity(self.sosdir)
        missing = [i for i in first_cores if i not in cpu_aff]
        if missing:
            status = False
            error = ("First cores of NUMA ({0}) should be added to CPUAffinity"
                     "({1}) via Tuned Config".format(
                         ','.join([str(i) for i in first_cores]),
                         ','.join([str(i) for i in cpu_aff])))
        return status, error

    def _validate_active_profile(self, data):
        status = True
        error = None
        tuned_profile = tuned.get_tuned_profile(self.sosdir)
        if tuned_profile != TUNED_PROFILE_NAME:
            status = False
            error = ("Tuned Profile '%s' is active. Expected Tuned profile "
                     "is '%s'" % (tuned_profile, TUNED_PROFILE_NAME))
        return status, error

    def _validate_cmdline_config(self, data):
        status = True
        error = None
        cmdline = ' '.join(system.get_cmdline(self.sosdir))
        missing_matchers = []
        for matcher in data.get('matchers'):
            if matcher not in cmdline:
                status = False
                missing_matchers.append(matcher)

        if not status:
            error = ("Tuned matchers (%s) is not found in the command line "
                     "of the node, available cmdline args are (%s)" %
                     (', '.join(missing_matchers), cmdline))
        return status, error
