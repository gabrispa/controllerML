from ryu import cfg
from ryu.base import app_manager
from ryu.base.app_manager import lookup_service_brick
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub
from ryu.topology.switches import Switches
from ryu.topology.switches import LLDPPacket

# TESTING
#  from ryu.lib.packet import ethernet, ether_types, packet

import ast, csv, json, time
import setting

#import topology_discover_a
import monitor

CONF = cfg.CONF


class Delay(app_manager.RyuApp):
    """
        A Ryu app for calculating link delay by using echo replay
        messages from the Control Plane to the datapaths in the Data Plane.
        It is part of the Statistics module of the Control Plane
    """
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Delay, self).__init__(*args, **kwargs)
        self.name = "delay"
        self.sending_echo_request_interval = 0.1
        self.sw_module = lookup_service_brick('switches')
        self.awareness = lookup_service_brick('awareness')
        self.paths_calculator = lookup_service_brick('paths_calculator')
        self.count = 0
        self.datapaths = {}
        self.echo_latency = {}
        self.link_delay = {}
        self.end_to_end_delay = {}  # {(src_ip, dst_ip): delay, }
        self.delay_dict = {}
        self.measure_thread = hub.spawn_after(25, self._detector)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('Register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('Unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _detector(self):
        """
            Delay detecting functon.
            Send echo request and calculate link delay periodically
        """
        self.logger.info("[INFO] Starting delay detecting function")
        while True:
            hub.sleep(setting.DELAY_DETECTING_PERIOD)
            self.count += 1
            self._send_echo_request()
            self.create_link_delay()
            # self.paths_calculator = lookup_service_brick('paths_calculator')
            if not self.paths_calculator:
                self.paths_calculator = lookup_service_brick('paths_calculator')
                self.paths_calculator.write_paths()

            
            try:
                self.awareness.shortest_paths = {}
            except:
                self.awareness = lookup_service_brick('awareness')
            # if self.awareness is not None:
                # self.show_delay_statis()

    def _send_echo_request(self):
        """
            Seng echo request msg to datapath.
        """
        for datapath in list(self.datapaths.values()):
            parser = datapath.ofproto_parser
            echo_req = parser.OFPEchoRequest(datapath,
                                             data=b"%.12f" % time.time())
            datapath.send_msg(echo_req)
            # Important! Don't send echo request together, it will
            # generate a lot of echo reply almost in the same time.
            # which will generate a lot of delay of waiting in queue
            # when processing echo reply in echo_reply_handler.

            hub.sleep(self.sending_echo_request_interval)

    @set_ev_cls(ofp_event.EventOFPEchoReply, MAIN_DISPATCHER)
    def echo_reply_handler(self, ev):
        """
            Handle the echo reply msg, and get the latency of link.
        """
        now_timestamp = time.time()
        try:
            self.logger.debug('OFPEchoReply received: data=%s',
                            ev.msg.data)
            latency = now_timestamp - eval(ev.msg.data)
            self.echo_latency[ev.msg.datapath.id] = latency
        except:
            return

    def get_delay(self, src, dst):
        """
            Get link delay.
                        Controller
                        |        |
        src echo latency|        |dst echo latency
                        |        |
                   SwitchA-------SwitchB

                    fwd_delay--->
                        <----reply_delay
            delay = (forward delay + reply delay - src datapath's echo latency
        """
        try:
            fwd_delay = self.awareness.graph[src][dst]['lldpdelay']
            re_delay = self.awareness.graph[dst][src]['lldpdelay']
            src_latency = self.echo_latency[src]
            dst_latency = self.echo_latency[dst]
            delay = (fwd_delay + re_delay - src_latency - dst_latency) / 2
            return max(delay, 0)
        except:
            return float('inf')

    def _save_lldp_delay(self, src=0, dst=0, lldpdelay=0):
        try:
            self.awareness.graph[src][dst]['lldpdelay'] = lldpdelay
        except:
            if self.awareness is None:
                self.awareness = lookup_service_brick('awareness')
            return

    def create_link_delay(self):
        """
            Create link delay data, and save it into graph object.
        """
        try:
            for src in self.awareness.graph:
                for dst in self.awareness.graph[src]:
                    if src == dst:
                        self.awareness.graph[src][dst]['delay'] = 0
                        continue
                    delay = self.get_delay(src, dst)
                    self.awareness.graph[src][dst]['delay'] = delay
            if self.awareness is not None:
                for dp in self.awareness.graph:
                    self.delay_dict.setdefault(dp, {})
                self.get_link_delay()
        except:
            if self.awareness is None:
                self.awareness = lookup_service_brick('awareness')
            return


    # def create_end_to_end_delay(self):
    #     if self.awareness.paths:
    #

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
            Explore LLDP packet and get the delay of link (fwd and reply).
        """
        msg = ev.msg

        try:
            src_dpid, src_port_no = LLDPPacket.lldp_parse(msg.data)
            dpid = msg.datapath.id
            if self.sw_module is None:
                self.sw_module = lookup_service_brick('switches')

            for port in list(self.sw_module.ports.keys()):
                if src_dpid == port.dpid and src_port_no == port.port_no:
                    port_data = self.sw_module.ports[port]
                    timestamp = port_data.timestamp
                    if timestamp:
                        delay = time.time() - timestamp
                        self._save_lldp_delay(src=src_dpid, dst=dpid,
                                            lldpdelay=delay)
        except LLDPPacket.LLDPUnknownFormat as e:
            # print("Unkown format")
            return

    def get_link_delay(self):
        '''
        Calculates total link dealy and save it in self.link_delay[(node1,node2)]: link_delay
        '''
        for src in self.awareness.graph:
            for dst in self.awareness.graph[src]:
                if src != dst:
                    delay1 = self.awareness.graph[src][dst]['delay']
                    delay2 = self.awareness.graph[dst][src]['delay']
                    link_delay = ((delay1 + delay2)*1000.0) / 2 #saves in ms
                    link = (src, dst)
                    self.link_delay[link] = link_delay
                    self.delay_dict[src][dst] = link_delay
        # print(self.awareness.graph[1][2]['delay'])
        # print(self.awareness.graph[2][1]['delay'])
        # if self.awareness.link_to_port:
        #     self.write_dijkstra_paths()
            # self.calc_stretch()

    def show_delay_statis(self):
        if self.awareness is None:
            print("Not doing nothing, awareness none")
        else:
            print("Latency ok")
        if setting.TOSHOW and self.awareness is not None:
            self.logger.info("\nsrc\t\tdst\t\tdelay")
            self.logger.info("---------------------------")
            for src in self.awareness.graph:
                for dst in self.awareness.graph[src]:
                    if src == dst: continue
                    delay = self.awareness.graph[src][dst]['delay']
                    self.logger.info("%s\t\t%s\t\t%.3f" % (src, dst, delay*1000))
