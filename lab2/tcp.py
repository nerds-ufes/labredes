#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Host, Node
from mininet.cli import CLI
from mininet.link import TCLink, Intf
from mininet.log import setLogLevel, info
from subprocess import call

def myNetwork():

    net = Mininet(topo=None,
                       build=False,
                       ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    info( '*** Add switches/APs\n')
    r3 = net.addHost('r3', cls=Node, ip='0.0.0.0')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')
    r1 = net.addHost('r1', cls=Node, ip='0.0.0.0')
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r5 = net.addHost('r5', cls=Node, ip='0.0.0.0')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')
    r2 = net.addHost('r2', cls=Node, ip='0.0.0.0')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')
    r6 = net.addHost('r6', cls=Node, ip='0.0.0.0')
    r6.cmd('sysctl -w net.ipv4.ip_forward=1')
    r4 = net.addHost('r4', cls=Node, ip='0.0.0.0')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')

    info( '*** Add hosts/stations\n')
    h3 = net.addHost('h3', cls=Host, ip='10.0.11.3/24', defaultRoute='10.0.11.1')
    h4 = net.addHost('h4', cls=Host, ip='10.0.14.3/24', defaultRoute='10.0.14.1')
    h1 = net.addHost('h1', cls=Host, ip='10.0.13.3/24', defaultRoute='10.0.13.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.15.3/24', defaultRoute='10.0.15.1')

    info( '*** Add links\n')
    net.addLink(r5, r1,intfName1='r5-eth1',intfName2='r1-eth2',cls=TCLink,bw=10)
    net.addLink(r3, r1,intfName1='r3-eth1',intfName2='r1-eth3',cls=TCLink,bw=10)
    net.addLink(r1, r2,intfName1='r1-eth1',intfName2='r2-eth1',cls=TCLink,bw=10)
    net.addLink(r2, r4,intfName1='r2-eth3',intfName2='r4-eth1',cls=TCLink,bw=10)
    net.addLink(r2, r6,intfName1='r2-eth2',intfName2='r6-eth1',cls=TCLink,bw=10)
    net.addLink(h1, r3,intfName1='h1-eth1',intfName2='r3-eth2',cls=TCLink,bw=10)
    net.addLink(h2, r4,intfName1='h2-eth1',intfName2='r4-eth2',cls=TCLink,bw=10)
    net.addLink(r5, h3,intfName1='r5-eth2',intfName2='h3-eth1',cls=TCLink,bw=10)
    net.addLink(r6, h4,intfName1='r6-eth2',intfName2='h4-eth1',cls=TCLink,bw=10)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches/APs\n')

    info( '*** Post configure nodes\n')

    # Router 1
    r1.cmd("ifconfig r1-eth1 10.0.2.1/24")
    r1.cmd("ifconfig r1-eth2 10.0.1.1/24")
    r1.cmd("ifconfig r1-eth3 10.0.3.1/24")
    # Router 2
    r2.cmd("ifconfig r2-eth1 10.0.2.2/24")
    r2.cmd("ifconfig r2-eth2 10.0.4.1/24")
    r2.cmd("ifconfig r2-eth3 10.0.5.1/24")
    # Router 3
    r3.cmd("ifconfig r3-eth1 10.0.3.2/24")
    r3.cmd("ifconfig r3-eth2 10.0.13.1/24")
    # Router 4
    r4.cmd("ifconfig r4-eth1 10.0.5.2/24")
    r4.cmd("ifconfig r4-eth2 10.0.15.1/24")
    # Router 5
    r5.cmd("ifconfig r5-eth1 10.0.1.2/24")
    r5.cmd("ifconfig r5-eth2 10.0.11.1/24")
    # Router 6
    r6.cmd("ifconfig r6-eth1 10.0.4.2/24")
    r6.cmd("ifconfig r6-eth2 10.0.14.1/24")

    # Router 1
    r1.cmd("route add default gw 10.0.2.2")
    r1.cmd("route add -net 10.0.11.0/24 gw 10.0.1.2")
    r1.cmd("route add -net 10.0.13.0/24 gw 10.0.3.2")
    # Router 2
    r2.cmd("route add default gw 10.0.2.1")
    r2.cmd("route add -net 10.0.14.0/24 gw 10.0.4.2")
    r2.cmd("route add -net 10.0.15.0/24 gw 10.0.5.2")
    # Router 3
    r3.cmd("route add default gw 10.0.3.1")
    # Router 4
    r4.cmd("route add default gw 10.0.5.1")
    # Router 5
    r5.cmd("route add default gw 10.0.1.1")
    # Router 6
    r6.cmd("route add default gw 10.0.4.1")

    # Host 1
    h1.cmd("route add default gw 10.0.13.1")
    # Host 2
    h2.cmd("route add default gw 10.0.15.1")
    # Host 3
    h3.cmd("route add default gw 10.0.11.1")
    # Host 4
    h4.cmd("route add default gw 10.0.14.1")


    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
