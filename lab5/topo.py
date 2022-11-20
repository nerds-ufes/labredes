import os
import inspect
import atexit
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import lg, info, setLogLevel
from mininet.link import Intf, TCLink
from mininet.node import Node, Switch, OVSKernelSwitch
from mininet.nodelib import NAT
from time import sleep

setLogLevel('info')

class Router(Switch):
    """Defines a new router that is inside a network namespace so that the
    individual routing entries don't collide.

    """
    ID = 0
    isSetup = True
    
    def __init__(self, name, **kwargs):
        kwargs['inNamespace'] = True
        kwargs['lo'] = 'up'
        Switch.__init__(self, name, **kwargs)
        Router.ID += 1
        self.switch_id = Router.ID

    def defaultIntf( self ):
        "Return interface for lowest port"
        return Node.defaultIntf( self )

    @staticmethod
    def setup():
        return

    def start(self, controllers):
        pass

    def stop(self):
        self.deleteIntfs()


class MyTopo( Topo ):
    "Topology Lab 3 - Ativ 3"

    def __init__( self, setNat=False ):
        "Create custom self."

        # Initialize topology
        Topo.__init__( self )

        # Create Nodes
        dr = {'defaultRoute': 'via 10.0.1.26'}
        h1 = self.addHost('h1', ip='10.0.0.101/23',**dr)
        h2 = self.addHost('h2', ip='10.0.0.102/23',**dr)
        h3 = self.addHost('h3', ip='10.0.0.103/23',**dr)
        h4 = self.addHost('h4', ip='10.0.0.104/23',**dr)
        h5 = self.addHost('h5', ip='10.0.0.105/23',**dr)
        s1 = self.addSwitch('sw2_1')
        s2 = self.addSwitch('sw2_2')
        s3 = self.addSwitch('sw2_3')
        s4 = self.addSwitch('sw2_4')
        s5 = self.addSwitch('sw2_5')
        s31 = self.addSwitch('sw3_1')

        r1 = self.addSwitch('r1', cls=Router)
        r2 = self.addSwitch('r2', cls=Router)
        r3 = self.addSwitch('r3', cls=Router)
        r4 = self.addSwitch('r4', cls=Router)
        r5 = self.addSwitch('r5', cls=Router)
        if setNat is True:
            r6 = self.addSwitch('r6', cls=Router)
            self.configNAT()
        else:
            r6 = self.addSwitch('r6', cls=Router)
        # Create links
        # Subnet 10.0.0.0/23
        self.addLink('h1','sw2_1')
        self.addLink('h2','sw2_2')
        self.addLink('h3','sw2_3')
        self.addLink('h4','sw2_4')
        self.addLink('h5','sw2_5')
        self.addLink('sw2_1','sw2_5')
        self.addLink('sw2_2','sw2_5')
        self.addLink('sw2_3','sw2_5')
        self.addLink('sw2_4','sw2_5')
        self.addLink('sw2_5','sw3_1')
        self.addLink('sw3_1','r4',intfName2='r4-eth1')
        self.addLink('sw3_1','r5',intfName2='r5-eth2')
        self.addLink('sw3_1','r6',intfName2='r6-eth5')
        #
        self.addLink('r1','r2',intfName1='r1-eth1',intfName2='r2-eth2')
        self.addLink('r1','r5',intfName1='r1-eth3',intfName2='r5-eth1')
        self.addLink('r2','r3',intfName1='r2-eth1',intfName2='r3-eth2')
        self.addLink('r3','r4',intfName1='r3-eth1',intfName2='r4-eth2')

        # Host x
        x1 = self.addHost('x1', ip='10.0.2.1/23',defaultRoute='via 10.0.2.21')
        self.addLink('x1','r1',intfName2='r1-eth4')
        # Host y
        y1 = self.addHost('y1', ip='10.0.12.1/23',defaultRoute='via 10.0.12.24')
        self.addLink('y1','r4',intfName2='r4-eth4')

    def configNAT( self ):
        # NAT options
        inetIntf = 'eth0'
        localIntf = 'r6-eth2'
        localIP = '10.0.2.2/24'
        localSubnet = '10.0.0.0/23'
        nat = self.addNode('nat1', cls=NAT, subnet=localSubnet,
           inetIntf=inetIntf, ip=localIP, inNamespace=False)
        self.addLink(nat, 'r6', intfName2=localIntf)


def startRouters():
    routers = net.get('r1', 'r2', 'r3', 'r4', 'r5', 'r6')

    for router in net.switches:
        router.cmd("sysctl -w net.ipv4.ip_forward=1")
        router.cmd("sysctl -w net.ipv4.conf.all.rp_filter=2")
    sleep(3)

    for router in routers:
        router.cmd("/usr/lib/quagga/zebra -f confs/%s/zebra-%s.conf -d -i /tmp/zebra-%s.pid > logs/%s-zebra-stdout 2>&1" % (router.name, router.name, router.name, router.name))
        router.cmd("/usr/lib/quagga/ospfd -f confs/%s/ospfd-%s.conf -d -i /tmp/ospf-%s.pid > logs/%s-ospf-stdout 2>&1" % (router.name, router.name, router.name, router.name), shell=True)
        sleep(1)
        info("Starting zebra and ospfd on %s\n" % router.name)

def configRouters():
    "Configuring routers interfaces IP address"

    r1, r2, r3, r4 , r5, r6 = net.get('r1', 'r2', 'r3', 'r4', 'r5', 'r6')
    # Router 1
    r1.cmd("ifconfig lo 127.0.0.1")
    r2.cmd("ifconfig lo 127.0.0.1")
    r3.cmd("ifconfig lo 127.0.0.1")
    r4.cmd("ifconfig lo 127.0.0.1")
    r5.cmd("ifconfig lo 127.0.0.1")
    r6.cmd("ifconfig lo 127.0.0.1")

    r1.cmd("ifconfig r1-eth1 10.0.4.21/23")
    r1.cmd("ifconfig r1-eth3 10.0.10.21/23")
    r1.cmd("ifconfig r1-eth4 10.0.2.21/23")
    # Router 2
    r2.cmd("ifconfig r2-eth1 10.0.6.22/23")
    r2.cmd("ifconfig r2-eth2 10.0.4.22/23")
    # Router 3
    r3.cmd("ifconfig r3-eth1 10.0.8.23/23")
    r3.cmd("ifconfig r3-eth2 10.0.6.23/23")
    # Router 4
    r4.cmd("ifconfig r4-eth1 10.0.1.24/23")
    r4.cmd("ifconfig r4-eth2 10.0.8.24/23")
    r4.cmd("ifconfig r4-eth4 10.0.12.24/23")
    # Router 5
    r5.cmd("ifconfig r5-eth1 10.0.10.25/23")
    r5.cmd("ifconfig r5-eth2 10.0.1.25/23")
    # Router 6
    r6.cmd("ifconfig r6-eth5 10.0.1.26/23")
    r6.cmd("ifconfig r6-eth2 10.0.2.15/24")


def setRoutes():
    "Setting static routes for all routers"

    r1, r2, r3, r4 , r5, r6 = net.get('r1', 'r2', 'r3', 'r4', 'r5', 'r6')
    # Router 1
    r1.cmd("route add default gw 10.0.10.25")
    r1.cmd("route add -net 10.0.6.0/23 gw 10.0.4.22")
    r1.cmd("route add -net 10.0.8.0/23 gw 10.0.4.22")
    # Router 2
    r2.cmd("route add default gw 10.0.6.23")
    r2.cmd("route add -net 10.0.0.0/23 gw 10.0.4.21")
    r2.cmd("route add -net 10.0.2.0/23 gw 10.0.4.21")
    r2.cmd("route add -net 10.0.10.0/23 gw 10.0.4.21")
    # Router 3
    r3.cmd("route add default gw 10.0.8.24")
    r3.cmd("route add -net 10.0.2.0/23 gw 10.0.6.22")
    r3.cmd("route add -net 10.0.4.0/23 gw 10.0.6.22")
    # Router 4
    r4.cmd("route add -net 10.0.2.0/23 gw 10.0.1.25")
    r4.cmd("route add -net 10.0.10.0/23 gw 10.0.1.25")
    r4.cmd("route add -net 10.0.4.0/23 gw 10.0.1.25")
    r4.cmd("route add -net 10.0.6.0/23 gw 10.0.8.23")
    # Router 5
    r5.cmd("route add -net 10.0.2.0/23 gw 10.0.10.21")
    r5.cmd("route add -net 10.0.4.0/23 gw 10.0.10.21")
    r5.cmd("route add -net 10.0.6.0/23 gw 10.0.1.24")
    r5.cmd("route add -net 10.0.8.0/23 gw 10.0.1.24")
    r5.cmd("route add -net 10.0.12.0/23 gw 10.0.1.24")
    # Router 6
    r6.cmd("route add -net 10.0.2.0/23 gw 10.0.1.25")
    r6.cmd("route add -net 10.0.10.0/23 gw 10.0.1.25")
    r6.cmd("route add -net 10.0.4.0/23 gw 10.0.1.25")
    r6.cmd("route add -net 10.0.12.0/23 gw 10.0.1.24")
    r6.cmd("route add -net 10.0.8.0/23 gw 10.0.1.24")
    r6.cmd("route add -net 10.0.6.0/23 gw 10.0.1.24")
    r6.cmd("route add default gw 10.0.2.2")

def setNATRoute():
    nat, r6 = net.get('nat1', 'r6')
    r6.cmd("route add default gw 10.0.2.2")
    nat.cmd('route add -net 10.0.0.0/23 gw 10.0.2.15')

def startNetwork():
    os.system("rm -f /tmp/R*.log /tmp/R*.pid logs/*")
    os.system("mn -c >/dev/null 2>&1")
    os.system("killall -9 zebra ospfd > /dev/null 2>&1")

    topo = MyTopo(setNat=False)
    global net
    net = Mininet(topo=topo, autoSetMacs=True, link=TCLink)
    net.start()
    info( '*** Starting routers\n')
    startRouters()
    info( '*** Configuring routers\n')
    configRouters()
    #info( '*** Setting up routes\n')
    #setRoutes()
    #setNATRoute()

    CLI(net)

    net.stop()
    os.system("killall -9 zebra ospfd")


if __name__ == '__main__':
 # atexit.register(stopNetwork)
 setLogLevel('info')
 startNetwork()
