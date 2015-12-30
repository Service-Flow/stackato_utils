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

        def isDea(self):
                return "dea" == self.role

        def getIp(self):
                return self.ip

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
        
        def getId(self):
                return self.id

        def __repr__(self):
                return 'Container id: {}, name: {}'.format(self.id, self.name)
                #return 'Container: id %s' % (self.id)

#if __name__ == "__main__":
kato_nodes = subprocess.check_output(["kato", "node", "list"])
#print(kato_nodes)
for node in map(Node, kato_nodes.splitlines()):
        if (node.isDea()):
                print("Node:" + str(node))
                docker_instances = subprocess.check_output(["ssh", node.getIp(), "docker ps"])
                for instance in map(DockerInstance, docker_instances.splitlines()[1:]):
                        print(instance)
                        #print(subprocess.check_output(["ssh", node.getIp(), "docker inspect", instance.getId()]))
                        import sys
                        sys.exit()
