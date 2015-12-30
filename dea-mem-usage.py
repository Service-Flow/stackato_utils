#!/usr/bin/python
import subprocess
import re


class Node:
    def __init__(self, node_string):
        node_info = node_string.split()
        self.ip = node_info[0]
        self.role = node_info[2]

    def __repr__(self):
        return '{} {}'.format(self.ip, self.role)

    def isdea(self):
        return "dea" == self.role


class DockerInstance:
    def __init__(self, ps_string):
        # The beginning of the line is the alphanumeric Container Id
        id_search = re.search("^\w+", ps_string, re.UNICODE)
        if id_search:
            self.id = id_search.group()
        else:
            raise ValueError("Unable to parse Container Id from\n{}".format(ps_string))

        # The end of the line is the Container name
        name_search = re.search("([\w-])+\s*$", ps_string, re.UNICODE)
        if name_search:
            self.name = name_search.group()
        else:
            raise ValueError("Unable to parse Container name from\n{}".format(ps_string))

    def get_overhead(self):
        free_mem = self.mem_limit - self.mem_usage
        overhead = free_mem / self.mem_limit
        return round(overhead * 100, 1)

    def __repr__(self):
        return "Container id: '{}', name: '{}'".format(self.id, self.name)


# if __name__ == "__main__":
kato_nodes = subprocess.check_output(["kato", "node", "list"])
# print(kato_nodes)
for node in map(Node, kato_nodes.splitlines()):
    if node.isdea():
        print("Node:" + str(node))
        docker_instances = subprocess.check_output(["ssh", node.ip, "docker ps"])
        for instance in map(DockerInstance, docker_instances.splitlines()[1:]):
            instance.mem_usage = float(subprocess.check_output(
                ["ssh", node.ip, "cat /sys/fs/cgroup/memory/docker/{}*/memory.usage_in_bytes".format(instance.id)]))
            instance.mem_limit = float(subprocess.check_output(
                ["ssh", node.ip, "cat /sys/fs/cgroup/memory/docker/{}*/memory.limit_in_bytes".format(instance.id)]))
            print("{} free memory {}%".format(instance, instance.get_overhead()))
            import sys

            sys.exit()
