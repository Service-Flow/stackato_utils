#!/usr/bin/python
import subprocess
import re


class Node:
    def __init__(self, node_string):
        node_info = node_string.split()
        self.ip = node_info[0]
        self.role = node_info[2]

    def is_dea(self):
        return "dea" == self.role

    def __repr__(self):
        return '{} {}'.format(self.ip, self.role)


class DockerInstance:
    def __init__(self, ps_string):
        # The beginning of the line is the alphanumeric Container Id
        id_search = re.search("^\w+", ps_string, re.UNICODE)
        if id_search:
            self.id = id_search.group().strip()
        else:
            raise ValueError("Unable to parse Container Id from\n{}".format(ps_string))

        # The end of the line is the Container name
        name_search = re.search("([\w-])+\s*$", ps_string, re.UNICODE)
        if name_search:
            self.name = name_search.group().strip()
        else:
            raise ValueError("Unable to parse Container name from\n{}".format(ps_string))

    def __free_mem(self):
        return self.mem_limit - self.mem_usage

    def __mem_limit_mb(self):
        return round(self.mem_limit / 1024**2, 1)

    def __free_mem_mb(self):
        return round(self.__free_mem() / 1024**2, 1)

    def __free_mem_percentage(self):
        overhead = self.__free_mem() / self.mem_limit
        return round(overhead * 100, 1)

    def __repr__(self):
        return "{}\t{}\t{}MB\t{}MB\t{}%".format(self.id, self.name, self.__mem_limit_mb(), self.__free_mem_mb(), self.__free_mem_percentage())


# if __name__ == "__main__":
kato_nodes = subprocess.check_output(["kato", "node", "list"])
print("Node\tContainer Id\tContainer name\tMem limit\tFree mem\tFree mem %")
for node in map(Node, kato_nodes.splitlines()):
    if node.is_dea():
        docker_instances = subprocess.check_output(["ssh", node.ip, "docker ps"])
        for instance in map(DockerInstance, docker_instances.splitlines()[1:]):
            instance.mem_usage = float(subprocess.check_output(
                ["ssh", node.ip, "cat /sys/fs/cgroup/memory/docker/{}*/memory.usage_in_bytes".format(instance.id)]))
            instance.mem_limit = float(subprocess.check_output(
                ["ssh", node.ip, "cat /sys/fs/cgroup/memory/docker/{}*/memory.limit_in_bytes".format(instance.id)]))
            print("{}\t{}".format(node.ip, instance))
