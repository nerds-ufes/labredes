import atexit
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import info,setLogLevel
net = None

def createTopo():
	topo=Topo()
	#Create Nodes
	topo.addHost("h1")
	topo.addHost("h2")
	topo.addHost("h3")
	topo.addHost("h4")
	topo.addSwitch('s1')
	topo.addSwitch('s2')
	topo.addSwitch('s3')
	#Create links
	topo.addLink('s1','s2')
	topo.addLink('s1','s3')
	topo.addLink('h1','s2')
	topo.addLink('h2','s2')
	topo.addLink('h3','s3')
	topo.addLink('h4','h3')
	return topo

def startNetwork():
	topo = createTopo()
	global net
	net = Mininet(topo=topo, autoSetMacs=True)
	net.start()
	CLI(net)

def stopNetwork():
	if net is not None:
		net.stop()

if __name__ == '__main__':
	atexit.register(stopNetwork)
	setLogLevel('info')
	startNetwork()
