#!/usr/bin/env python

import sys

from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference


def topology(args):
    info("*** Creating Network\n")
    net = Mininet_wifi(link=wmediumd,
                       wmediumd_mode=interference)

    info("*** Creating Access Points\n")
    ap1 = net.addAccessPoint('ap1', ssid="ap1-ssid", 
                                    mode="g",
                                    channel="1", 
                                    position='20,20,0', 
                                    failMode='standalone')
    ap2 = net.addAccessPoint('ap2', ssid="ap2-ssid", 
                                    mode="g",
                                    channel="6", 
                                    position='80,20,0', 
                                    failMode='standalone')
    ap3 = net.addAccessPoint('ap3', ssid="ap3-ssid", 
                                    mode="g",
                                    channel="8", 
                                    position='80,80,0', 
                                    failMode='standalone')
    ap4 = net.addAccessPoint('ap4', ssid="ap4-ssid", 
                                    mode="g",
                                    channel="11", 
                                    position='20,80,0', 
                                    failMode='standalone')

    info("*** Creating Wireless Stations\n")
    sta1 = net.addStation('sta1', ip="10.0.0.1/24", 
                                  position='10,10,0')
    sta2 = net.addStation('sta2', ip="10.0.0.2/24", 
                                  position='90,10,0')
    sta3 = net.addStation('sta3', ip="10.0.0.3/24", 
                                  position='90,90,0')
    sta4 = net.addStation('sta4', ip="10.0.0.4/24", 
                                  position='10,90,0')

    info("*** Creating Switches\n")
    sw1 = net.addSwitch('sw1', failMode='standalone')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4.3)

    info("*** Configuring WiFi Nodes\n")
    net.configureWifiNodes()

    info("*** Adding Links\n")
    net.addLink(ap1, sw1)
    net.addLink(ap2, sw1)
    net.addLink(ap3, sw1)
    net.addLink(ap4, sw1)
    
    if '-p' not in args:
        net.plotGraph(max_x=100, max_y=100)

    info("*** Starting network\n")
    net.build()
    sw1.start([])
    ap1.start([])
    ap2.start([])
    ap3.start([])
    ap4.start([])

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
