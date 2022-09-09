from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

import json

class DigitalTwin( Topo ):

    def build(self):
        with open('./digital_twin_topology.json', 'r') as json_dt:
            f = json.load(json_dt)

        nodes = f['nodes']
        print(nodes)
        links = f['links']
        dict = {}

        for node in nodes:
            n = "s" + str(node)
            print(n)
            globals()[n] = self.addSwitch(n, cls=OVSKernelSwitch)
            dict[node] = globals()[n]

        self.addLink(s1, s7)
        for link in links:
            self.addLink(dict[link[0]], dict[link[1]])


topos = { 'digital_twin': ( lambda: DigitalTwin() )}

