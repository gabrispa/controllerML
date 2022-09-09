from matplotlib._api import select_matching_signature
import networkx as nx
import matplotlib.pyplot as plt
import time

from ryu import cfg, utils
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.base.app_manager import lookup_service_brick
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import arp
from ryu.lib import hub
from ryu.topology import event
from ryu.topology.api import get_switch, get_link

import json
import setting


class TopologyDiscover(app_manager.RyuApp):
    """
        A Ryu app for discovering topology information.
        Provides many data services for other Apps, such as
        link_to_port, access_table, switch_port_table, access_ports,
        interior_ports, and topology graph.
        This represent the Topology discovery module of the Control Plane
    """
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # List the event list should be listened.
    events = [
        event.EventSwitchEnter,
        event.EventSwitchLeave, event.EventPortAdd,
        event.EventPortDelete, event.EventPortModify,
        event.EventLinkAdd, event.EventLinkDelete
    ]

    def __init__(self, *args, **kwargs):
        super(TopologyDiscover, self).__init__(*args, **kwargs)
        self.topology_api_app = self
        self.name = "awareness"
        self.link_to_port = {}                # {(src_dpid,dst_dpid):(src_port,dst_port),}
        self.access_table = {}                # {(sw,port):(ip, mac),}
        self.switch_port_table = {}           # {dpid:set(port_num,),}
        self.access_ports = {}                # {dpid:set(port_num,),}
        self.interior_ports = {}              # {dpid:set(port_num,),}
        self.switches = []                    # self.switches = [dpid,]
        self.shortest_paths = {}              # {dpid:{dpid:[[path],],},}
        self.pre_link_to_port = {}
        self.pre_access_table = {}
        self.length = 0
        self.graph = nx.DiGraph()
        self.initiation_delay = self.get_initiation_delay(4)
        self.start_time = time.time()
        self.discover_thread = hub.spawn_after(self.initiation_delay, self._discover)

    def _discover(self):
        while True:
            self.logger.info("[INFO] Started discovering routine")
            # self.get_topology(None)
            self.get_topology_dt()
            self.save_topology()
            # self.show_topology()
            hub.sleep(setting.DISCOVERY_PERIOD)

    def save_topology(self):
        present_time = time.time()
        if present_time - self.start_time < self.initiation_delay: #Set to 30s
            return

        with open('./digital_twin_topology.json', 'w') as dt_json:
            nodes = self.graph_dt.nodes()
            links = self.graph_dt.edges()
            json.dump({"nodes": list(nodes),  "links": list(links)}, dt_json, indent=2)

    def add_flow(self, dp, priority, match, actions, idle_timeout=0, hard_timeout=0):
        ofproto = dp.ofproto
        parser = dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=dp, priority=priority,
                                idle_timeout=idle_timeout,
                                hard_timeout=hard_timeout,
                                match=match, instructions=inst)
        dp.send_msg(mod)

    def get_topology_dt(self):
        self.logger.info("[INFO] Getting topology information (DT)")
        present_time = time.time()
        if present_time - self.start_time < self.initiation_delay: #Set to 30s
            return

        self.graph_dt = nx.DiGraph()
        switch_list = get_switch(self.topology_api_app, None)
        links = get_link(self.topology_api_app, None)
        self.create_port_map(switch_list)
        time.sleep(0.5)
        self.create_interior_links(links)
        self.create_access_ports()
        self.graph_dt.add_nodes_from([sw.dp.id for sw in switch_list])
        self.graph_dt.add_edges_from([(link.src.dpid, link.dst.dpid) for link in links])

    def get_host_location(self, host_ip):
        """
            Get host location info ((datapath, port)) according to the host ip.
            self.access_table = {(sw,port):(ip, mac),}
        """
        # print(self.access_table)
        for key in list(self.access_table.keys()):
            if self.access_table[key][0] == host_ip:
                return key
        self.logger.info("%s location is not found." % host_ip)
        return None

    def get_graph(self, link_list):
        """
            Get Adjacency matrix from link_to_port.
        """
        _graph = nx.DiGraph()
        _graph.add_nodes_from(self.switches)
       # print(self.switches)

        for src in self.switches:
            for dst in self.switches:
                if src == dst:
                    _graph.add_edge(src, dst, weight=0)
                elif (src, dst) in link_list:
                # elif link_list.has_edge(src, dst):
                    _graph.add_edge(src, dst, weight=1)
                else:
                    pass
        return _graph

    def get_initiation_delay(self, fanout):
        """
            Get initiation delay.
        """
        if fanout == 4:
            delay = 10
        elif fanout == 8:
            delay = 20
        else:
            delay = 20
        return delay

    def create_port_map(self, switch_list):
        """
            Create interior_port table and access_port table.
        """
        for sw in switch_list:
            dpid = sw.dp.id
            self.switch_port_table.setdefault(dpid, set())
            # switch_port_table is equal to interior_ports plus access_ports.
            self.interior_ports.setdefault(dpid, set())
            self.access_ports.setdefault(dpid, set())
            for port in sw.ports:
                # switch_port_table = {dpid:set(port_num,),}
                self.switch_port_table[dpid].add(port.port_no)

    def create_interior_links(self, link_list):
        """
            Get links' srouce port to dst port  from link_list.
            link_to_port = {(src_dpid,dst_dpid):(src_port,dst_port),}
        """
        for link in link_list:
            src = link.src
            dst = link.dst

            self.link_to_port[(src.dpid, dst.dpid)] = (src.port_no, dst.port_no)
            # Find the access ports and interior ports.
            if link.src.dpid in self.switches:
                self.interior_ports[link.src.dpid].add(link.src.port_no)
            if link.dst.dpid in self.switches:
                self.interior_ports[link.dst.dpid].add(link.dst.port_no)

    def create_access_ports(self):
        """
            Get ports without link into access_ports.
        """
        for sw in self.switch_port_table:
            all_port_table = self.switch_port_table[sw]
            interior_port = self.interior_ports[sw]
            # That comes the access port of the switch.
            self.access_ports[sw] = all_port_table - interior_port

    def register_access_info(self, dpid, in_port, ip, mac):
        """
            Register access host info into access table.
        """
        print("register for " + str(in_port) + " " + str(ip))
        if in_port in self.access_ports[dpid]:
            if (dpid, in_port) in self.access_table:
                if self.access_table[(dpid, in_port)] == (ip, mac):
                    return
                else:
                    self.access_table[(dpid, in_port)] = (ip, mac)
                    return
            else:
                self.access_table.setdefault((dpid, in_port), None)
                self.access_table[(dpid, in_port)] = (ip, mac)
                return
