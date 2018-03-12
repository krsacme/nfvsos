from nfvsos.checkers import Checker
from nfvsos.utils import config
from nfvsos.utils import cpu_layout
from nfvsos.utils import system
from nfvsos.utils import tuned

TUNED_PROFILE_NAME = 'cpu-partitioning'

CONDITIONS = [
    {
        'name': 'IOMMU in cmdline',
        'description': 'IOMMU should be enabled in cmdline',
        'validator': '_validate_cmdline',
        'matchers': ['iommu=on']
    },
    {
        'name': 'Hugepages in cmdline',
        'description': 'Hugepages should be enabled in cmdline',
        'validator': '_validate_cmdline',
        'matchers': ['default_hugepagesz=1GB', 'hugepagesz=1G', 'hugepages=']
    }
]


class ProcChecker(Checker):
    checker_name = 'cmdline'
    checker_profiles = ('dpdk')

    def __init__(self, commons):
        super(ProcChecker, self).__init__(commons)
        self.conditions = CONDITIONS

    def _validate_cmdline(self, data):
        status = True
        error = None
        cmdline = system.get_cmdline(self.sosdir)
        missing = []
        for matcher in data.get('matchers'):
            found = False
            for cmd in cmdline:
                if matcher in cmd:
                    found = True
            if not found:
                missing.append(matcher)

        if missing:
            status = False
            error = ("Cmdline does not contain parameter(s) - %s" %
                     (','.join(missing)))

        return status, error
