import os
import re

TUNED_CPU_CONFIG = 'etc/tuned/cpu-partitioning-variables.conf'

def get_tuned_isolated_cores(sosdir):
    isol = []
    tuned_config = os.path.join(
        sosdir, 'etc/tuned/cpu-partitioning-variables.conf')
    if not os.path.exists(tuned_config):
        print("no tuned config")
        return isol
    with open(tuned_config) as f:
        data = f.read().strip().split('\n')
        for line in data:
            match = re.search('^(isolated_cores=)(.*)$', line)
            if not match:
                continue
            if match.group(2):
                for item in match.group(2).split(','):
                    if '-' in item:
                        start = int(item.split('-')[0])
                        end = int(item.split('-')[1])
                        for i in range(start, end + 1):
                            isol.append(int(i))
                    else:
                        isol.append(int(item))

        return isol
