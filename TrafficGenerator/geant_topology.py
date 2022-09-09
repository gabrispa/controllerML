#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import time

import json

def myNetwork():
    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      protocol='tcp',
                      port=6633)
                      
    info( '*** Add switches\n')
    s14 = net.addSwitch('s14', cls=OVSKernelSwitch)
    s7 = net.addSwitch('s7', cls=OVSKernelSwitch)
    s11 = net.addSwitch('s11', cls=OVSKernelSwitch)
    s21 = net.addSwitch('s21', cls=OVSKernelSwitch)
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)
    s23 = net.addSwitch('s23', cls=OVSKernelSwitch)
    s18 = net.addSwitch('s18', cls=OVSKernelSwitch)
    s15 = net.addSwitch('s15', cls=OVSKernelSwitch)
    s8 = net.addSwitch('s8', cls=OVSKernelSwitch)
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s12 = net.addSwitch('s12', cls=OVSKernelSwitch)
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)
    s22 = net.addSwitch('s22', cls=OVSKernelSwitch)
    s19 = net.addSwitch('s19', cls=OVSKernelSwitch)
    s9 = net.addSwitch('s9', cls=OVSKernelSwitch)
    s16 = net.addSwitch('s16', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s13 = net.addSwitch('s13', cls=OVSKernelSwitch)
    s6 = net.addSwitch('s6', cls=OVSKernelSwitch)
    s10 = net.addSwitch('s10', cls=OVSKernelSwitch)
    s20 = net.addSwitch('s20', cls=OVSKernelSwitch)
    s17 = net.addSwitch('s17', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.6', defaultRoute=None)
    h7 = net.addHost('h7', cls=Host, ip='10.0.0.7', defaultRoute=None)
    h8 = net.addHost('h8', cls=Host, ip='10.0.0.8', defaultRoute=None)
    h9 = net.addHost('h9', cls=Host, ip='10.0.0.9', defaultRoute=None)
    h10 = net.addHost('h10', cls=Host, ip='10.0.0.10', defaultRoute=None)
    h11 = net.addHost('h11', cls=Host, ip='10.0.0.11', defaultRoute=None)
    h12 = net.addHost('h12', cls=Host, ip='10.0.0.12', defaultRoute=None)
    h13 = net.addHost('h13', cls=Host, ip='10.0.0.13', defaultRoute=None)
    h14 = net.addHost('h14', cls=Host, ip='10.0.0.14', defaultRoute=None)
    h15 = net.addHost('h15', cls=Host, ip='10.0.0.15', defaultRoute=None)
    h16 = net.addHost('h16', cls=Host, ip='10.0.0.16', defaultRoute=None)
    h17 = net.addHost('h17', cls=Host, ip='10.0.0.17', defaultRoute=None)
    h18 = net.addHost('h18', cls=Host, ip='10.0.0.18', defaultRoute=None)
    h19 = net.addHost('h19', cls=Host, ip='10.0.0.19', defaultRoute=None)
    h20 = net.addHost('h20', cls=Host, ip='10.0.0.20', defaultRoute=None)
    h21 = net.addHost('h21', cls=Host, ip='10.0.0.21', defaultRoute=None)
    h22 = net.addHost('h22', cls=Host, ip='10.0.0.22', defaultRoute=None)
    h23 = net.addHost('h23', cls=Host, ip='10.0.0.23', defaultRoute=None)
    h24 = net.addHost('h24', cls=Host, ip='10.0.0.24', defaultRoute=None)
    
    

    info( '*** Add links\n')
    net.addLink(s1, h1)
    net.addLink(s2, h2 )
    net.addLink(s3, h3 )
    net.addLink(s4, h4 )
    net.addLink(s5, h5 )
    net.addLink(s6, h6 )
    net.addLink(s7, h7 )
    net.addLink(s8, h8 )
    net.addLink(s9, h9 )
    net.addLink(s10, h24)
    net.addLink(s10, h10)
    net.addLink(s11, h11)
    net.addLink(s12, h12)
    net.addLink(s13, h13)
    net.addLink(s14, h14)
    net.addLink(s15, h15)
    net.addLink(s16, h16)
    net.addLink(s17, h17)
    net.addLink(s18, h18)
    net.addLink(s19, h19)
    net.addLink(s20, h20)
    net.addLink(s21, h21)
    net.addLink(s22, h22)
    net.addLink(s23, h23)
#switch esterni che inviano 13-19-17-12-10
#switch esterni che ricevono 1-3-14-15-9 quindi sono collegati a quelli che inviano solo tramite la rete
#switch core 18-2-11-5
    #net.addLink(s1, s3)
    net.addLink(s1, s7)
    #net.addLink(s1, s16)
    net.addLink(s2, s4)
    net.addLink(s2, s7)
    #net.addLink(s2, s12)
    #net.addLink(s2, s13)
    net.addLink(s2, s18)
    net.addLink(s2, s23)
      #aggiunti
    net.addLink(s2, s11)
    net.addLink(s2, s6)
    #net.addLink(s3, s10)
    #net.addLink(s3, s11)
    #net.addLink(s3, s14)
    net.addLink(s3, s21)
    #net.addLink(s4, s16)
     #aggiunti
    #net.addLink(s4, s6)
    net.addLink(s4, s14)
    net.addLink(s4, s20)
    net.addLink(s5, s8)
    net.addLink(s5, s16)
     #aggiunti
    net.addLink(s5, s11)
     #net.addLink(s6, s7)
    net.addLink(s6, s19)
     #aggiunti
    net.addLink(s6, s13)
    net.addLink(s6, s18)
     #net.addLink(s7, s17)
     #net.addLink(s7, s19)
    net.addLink(s7, s21)
    #aggiunti
    net.addLink(s7, s18)
    net.addLink(s8, s9)
    #aggiunti
    net.addLink(s8, s20)
    #net.addLink(s9, s15)
    #net.addLink(s9, s16)
    #net.addLink(s10, s11)
    #net.addLink(s10, s12)
    net.addLink(s10, s16)
    #net.addLink(s10, s17)
    #aggiunti
    net.addLink(s11, s20)
    net.addLink(s11, s21)
    net.addLink(s11, s22)
    net.addLink(s11, s16)
    net.addLink(s12, s22)
    #net.addLink(s13, s14)
    #net.addLink(s13, s17)
    #net.addLink(s13, s19)
    net.addLink(s15, s20)
    #net.addLink(s17, s20)
    net.addLink(s17, s23)
    net.addLink(s18, s21)
    #net.addLink(s20, s22)
    #aggiunti
    net.addLink(s22, s23)


#topos = { 'geant': ( lambda: Geant() )}
    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s14').start([c0])
    net.get('s7').start([c0])
    net.get('s11').start([c0])
    net.get('s21').start([c0])
    net.get('s4').start([c0])
    net.get('s23').start([c0])
    net.get('s18').start([c0])
    net.get('s15').start([c0])
    net.get('s8').start([c0])
    net.get('s1').start([c0])
    net.get('s12').start([c0])
    net.get('s5').start([c0])
    net.get('s22').start([c0])
    net.get('s19').start([c0])
    net.get('s9').start([c0])
    net.get('s16').start([c0])
    net.get('s3').start([c0])
    net.get('s13').start([c0])
    net.get('s6').start([c0])
    net.get('s10').start([c0])
    net.get('s20').start([c0])
    net.get('s17').start([c0])
    net.get('s2').start([c0])

    info( '*** Post configure switches and hosts\n')
    dict1 ={}
    with open('./host_IP.json', 'w') as host_IP:
     for i in range(24):
     	msg = 'h'+str(i+1)
     	host = net.get(msg)
     	ip = host.IP(None)
     	dict1[msg]=ip
     json.dump(dict1, host_IP, indent=2)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()


