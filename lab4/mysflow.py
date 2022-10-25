#!/usr/bin/env python

import sys
import re
import socket

from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference
from json import dumps
from requests import put
from mininet.util import quietRun
from os import listdir, environ
from fcntl import ioctl
from array import array
from struct import pack, unpack

def getIfInfo(dst):
    is_64bits = sys.maxsize > 2**32
    struct_size = 40 if is_64bits else 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    max_possible = 8 # initial value
    while True:
      bytes = max_possible * struct_size
      names = array('B')
      for i in range(0, bytes):
        names.append(0)
      outbytes = unpack('iL', ioctl(
        s.fileno(),
        0x8912,  # SIOCGIFCONF
        pack('iL', bytes, names.buffer_info()[0])
      ))[0]
      if outbytes == bytes:
        max_possible *= 2
      else:
        break
    s.connect((dst, 0))
    ip = s.getsockname()[0]
    for i in range(0, outbytes, struct_size):
      addr = socket.inet_ntoa(names[i+20:i+24])
      if addr == ip:
        name = names[i:i+16]
        try:
          name = name.tobytes().decode('utf-8')
        except AttributeError:
          name = name.tostring()
        name = name.split('\0', 1)[0]
        return (name,addr)

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

    #info("*** Creating Controller\n")
    #c0 = net.addController('c0')

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
    #c0.start()
    sw1.start([])
    ap1.start([])
    ap2.start([])
    ap3.start([])
    ap4.start([])

    info("*** Creating Monitoring Interfaces\n")
    ap1.cmd('iw dev %s-eth2 interface add %s-mon0 type monitor' %
                 (ap1.name, ap1.name))
    ap2.cmd('iw dev %s-eth2 interface add %s-mon0 type monitor' %
                 (ap2.name, ap2.name))
    ap3.cmd('iw dev %s-eth2 interface add %s-mon0 type monitor' %
                 (ap3.name, ap3.name))
    ap4.cmd('iw dev %s-eth2 interface add %s-mon0 type monitor' %
                 (ap4.name, ap4.name))
           

    ap1.cmd('ifconfig %s-mon0 up' % ap1.name)
    ap2.cmd('ifconfig %s-mon0 up' % ap2.name)
    ap3.cmd('ifconfig %s-mon0 up' % ap3.name)
    ap4.cmd('ifconfig %s-mon0 up' % ap4.name)

    info("*** Configuring sFlow-RT\n")
    collector = environ.get('COLLECTOR','127.0.0.1')
    (ifname, agent) = getIfInfo(collector)
    sampling = environ.get('SAMPLING','10')
    polling = environ.get('POLLING','10')
    sflow = 'ovs-vsctl -- --id=@sflow create sflow agent=%s target=%s ' \
            'sampling=%s polling=%s --' % (ifname,collector,sampling,polling)
            
    info("*** Configuring sFlow-RT at APs\n")
    for ap in net.aps:
        sflow += ' -- set bridge %s sflow=@sflow' % ap
        info(' '.join([ap.name for ap in net.aps]) + "\n")
        quietRun(sflow)

    info("*** Configuring sFlow-RT at Switches\n")
    for s in net.switches:
        sflow += ' -- set bridge %s sflow=@sflow' % s
        info(' '.join([s.name for s in net.switches]) + "\n")
        quietRun(sflow)

    info("*** Sending topology\n")
    topo = {'nodes':{}, 'links':{}}
    for ap in net.aps:
        topo['nodes'][ap.name] = {'agent':agent, 'ports':{}}

    for s in net.switches:
        topo['nodes'][s.name] = {'agent':agent, 'ports':{}}
    path = '/sys/devices/virtual/mac80211_hwsim/'
    for child in listdir(path):
        dir_ = '/sys/devices/virtual/mac80211_hwsim/'+'%s' % child+'/net/'
        for child_ in listdir(dir_):
            node = child_[:3]
            if node in topo['nodes']:
                ifindex = open(dir_+child_+'/ifindex').read().split('\n',1)[0]
                topo['nodes'][node]['ports'][child_] = {'ifindex': ifindex}

    path = '/sys/devices/virtual/net/'
    for child in listdir(path):
        parts = re.match('(^.+)-(.+)', child)
        if parts is None: continue
        if parts.group(1) in topo['nodes']:
            ifindex = open(path+child+'/ifindex').read().split('\n',1)[0]
            topo['nodes'][parts.group(1)]['ports'][child] = {'ifindex': ifindex}

    linkName = '%s-%s' % (ap1.name, s.name)
    topo['links'][linkName] = {'node1': ap1.name, 'port1': 'ap1-eth2',
                               'node2': s.name,   'port2': 'sw1-eth1'}
    linkName = '%s-%s' % (ap2.name, s.name)
    topo['links'][linkName] = {'node1': ap2.name, 'port1': 'ap2-eth2',
                               'node2': s.name,   'port2': 'sw1-eth2'}
    linkName = '%s-%s' % (ap3.name, s.name)
    topo['links'][linkName] = {'node1': ap3.name, 'port1': 'ap3-eth2',
                               'node2': s.name,   'port2': 'sw1-eth3'}
    linkName = '%s-%s' % (ap4.name, s.name)
    topo['links'][linkName] = {'node1': ap4.name, 'port1': 'ap4-eth2',
                               'node2': s.name, 'port2': 'sw1-eth4'}
#    linkName = '%s-%s' % (ap1.name, s.name)
#    topo['links'][linkName] = {'node1': ap1.name, 'port1': ap1.wintfs[0].name,
#                               'node2': ap2.name, 'port2': ap2.wintfs[0].name}

    put('http://127.0.0.1:8008/topology/json', data=dumps(topo))

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
