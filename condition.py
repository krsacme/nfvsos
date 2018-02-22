import utils


class DpdkConditions(object):

    def c1_pmd_in_both_numa(self, pmd_list, cpu_layout):
        siblings_present = True
        both_numa_has_cpus = True
        cpus_in_numa = []
        for item in enumerate(cpu_layout):
            cpus_in_numa.append(0)
        for item in pmd_list:
            node, sibs = self._get_numa_node(cpu_layout, item)
            cpus_in_numa[node] += 1
            sibs.remove(item)
            for i in sibs:
                if i not in pmd_list:
                    siblings_present = False
                    print("CPUs(%s)'s sibling (%s) is not added in PMD list" %
                          (item, i))
        if 0 in cpus_in_numa:
            both_numa_has_cpus = False
            print("CPUs found in numa (%s), not all numa node has PMD CPUs" %
                  cpus_in_numa)
        if siblings_present and both_numa_has_cpus:
            print("PMD CPUs in both NUMA including siblings condition passed")

    def c2_host_in_both_numa_including_first_core(self, host_list, cpu_layout):
        pass

    def c3_isol_cpus_with_pmd_and_vpcus(self, pmd_list, vcpu_list, cpu_layout):
        pass

    def _get_numa_node(self, cpu_layout, cpu):
        for idx, numa_list in enumerate(cpu_layout):
            for sibs in numa_list:
                if cpu in sibs:
                    return idx, sibs
        return None, None
