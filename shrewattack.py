#!/usr/bin/python


from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

import subprocess
from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
import termcolor as T
from argparse import ArgumentParser

import sys
import os
from util.monitor import monitor_qlen
from util.helper import stdev


# Number of samples to skip for reference util calibration.
CALIBRATION_SKIP = 10

# Number of samples to grab for reference util calibration.
CALIBRATION_SAMPLES = 30

# Set the fraction of the link utilization that the measurement must exceed
# to be considered as having enough buffering.
TARGET_UTIL_FRACTION = 0.98

# Fraction of input bandwidth required to begin the experiment.
# At exactly 100%, the experiment may take awhile to start, or never start,
# because it effectively requires waiting for a measurement or link speed
# limiting error.
START_BW_FRACTION = 0.9

# Number of samples to take in get_rates() before returning.
NSAMPLES = 3

# Time to wait between samples, in seconds, as a float.
SAMPLE_PERIOD_SEC = 1.0

# Time to wait for first sample, in seconds, as a float.
SAMPLE_WAIT_SEC = 3.0


def cprint(s, color, cr=True):
    """Print in color
       s: string to print
       color: color to use"""
    if cr:
        print T.colored(s, color)
    else:
        print T.colored(s, color),


# Parse arguments

parser = ArgumentParser(description="Shrew attack tests")
parser.add_argument('--bw-host', '-B',
                    dest="bw_host",
                    type=float,
                    action="store",
                    help="Bandwidth of host links",
                    required=True)

parser.add_argument('--bw-net', '-b',
                    dest="bw_net",
                    type=float,
                    action="store",
                    help="Bandwidth of network link",
                    required=True)

parser.add_argument('--delay',
                    dest="delay",
                    type=float,
                    help="Delay in milliseconds of host links",
                    default=87)

parser.add_argument('--dir', '-d',
                    dest="dir",
                    action="store",
                    help="Directory to store outputs",
                    default="results",
                    required=True)

parser.add_argument('-n',
                    dest="n",
                    type=int,
                    action="store",
                    help="Number of nodes in star.  Must be >= 3",
                    required=True)


parser.add_argument('--maxq',
                    dest="maxq",
                    action="store",
                    help="Max buffer size of network interface in packets",
                    default=1000)

parser.add_argument('--cong',
                    dest="cong",
                    help="Congestion control algorithm to use",
                    default="bic")

parser.add_argument('--iperf',
                    dest="iperf",
                    help="Path to custom iperf",
                    required=True)

parser.add_argument('--period',
		    dest="period",
		    type=float,
                    action="store",
		    help="Period between attacks in sec",
		    required=True)

parser.add_argument('--length',
		    dest="length",
		    type=int,
		    action="store",
		    help="Length of attack in ms",
		    required=True)

# Expt parameters
args = parser.parse_args()

CUSTOM_IPERF_PATH = args.iperf
assert(os.path.exists(CUSTOM_IPERF_PATH))

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

lg.setLogLevel('info')

# Topology to be instantiated in Mininet
class StarTopo(Topo):
    "Star topology for Buffer Sizing experiment"

    def build(self, n=3, cpu=None, bw_host=None, bw_net=None,
	      delay=None, maxq=None):
	#TODO: Set up one regular host, one bad host, and shared reciever
	# connected by a switch
    switch = self.addSwitch('server')
    server= self.addHost('server')
    for h in range(n-1):
        host = self.addHost('h%s' %(h+1)) #host should start at 1
        self.addLink(host, switch, bw=bw_host, cpu=cpu, max_queue_size=maxq, delay=delay)
    	return
    host = self.addHost('attacker')
    #not sure what parameters are for attacker link

def start_tcpprobe():
    "Install tcp_probe module and dump to file"
    os.system("rmmod tcp_probe 2>/dev/null; modprobe tcp_probe;")
    Popen("cat /proc/net/tcpprobe > %s/tcp_probe.txt" %
          args.dir, shell=True)

def stop_tcpprobe():
    os.system("killall -9 cat; rmmod tcp_probe &>/dev/null;")



def get_txbytes(iface):
    f = open('/proc/net/dev', 'r')
    lines = f.readlines()
    for line in lines:
        if iface in line:
            break
    f.close()
    if not line:
        raise Exception("could not find iface %s in /proc/net/dev:%s" %
                        (iface, lines))
    # Extract TX bytes from:
    #Inter-|   Receive                                                |  Transmit
    # face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    # lo: 6175728   53444    0    0    0     0          0         0  6175728   53444    0    0    0     0       0          0
    return float(line.split()[9])

def get_rates(iface, nsamples=NSAMPLES, period=SAMPLE_PERIOD_SEC,
              wait=SAMPLE_WAIT_SEC):
    """Returns the interface @iface's current utilization in Mb/s.  It
    returns @nsamples samples, and each sample is the average
    utilization measured over @period time.  Before measuring it waits
    for @wait seconds to 'warm up'."""
    # Returning nsamples requires one extra to start the timer.
    nsamples += 1
    last_time = 0
    last_txbytes = 0
    ret = []
    sleep(wait)
    while nsamples:
        nsamples -= 1
        txbytes = get_txbytes(iface)
        now = time()
        elapsed = now - last_time
        #if last_time:
        #    print "elapsed: %0.4f" % (now - last_time)
        last_time = now
        # Get rate in Mbps; correct for elapsed time.
        rate = (txbytes - last_txbytes) * 8.0 / 1e6 / elapsed
        if last_txbytes != 0:
            # Wait for 1 second sample
            ret.append(rate)
        last_txbytes = txbytes
        print '.',
        sys.stdout.flush()
        sleep(period)
    return ret

#TODO: Change this to be the shared reciever
#I dont' think we have to change anything here, except maybe the name
# Hint: iperf command to start the receiver:
#       '%s -s -p %s > %s/iperf_server.txt' %
#        (CUSTOM_IPERF_PATH, 5001, args.dir)
# Note: The output file should be <args.dir>/iperf_server.txt
#       It will be used later in count_connections()

def start_receiver(net):
    seconds = 3600
    server = net.get('receiver')

    server.popen('%s -s -p %s > %s/iperf_server.txt' % (CUSTOM_IPERF_PATH, 5001, args.dir), shell=True)
    pass

#TODO: These will be the regular (non-DOS) flows, we can just start with 1
# Start args.nflows flows across the senders in a round-robin fashion
# Hint: use get() to get a handle on the sender (A or B in the
# figure) and receiver node (C in the figure).
# Hint: iperf command to start flow:
#       '%s -c %s -p %s -t %d -i 1 -yc -Z %s > %s/%s' % (
#           CUSTOM_IPERF_PATH, server.IP(), 5001, seconds, args.cong, args.dir, output_file)
# It is a good practice to store output files in a place specific to the
# experiment, where you can easily access, e.g., under args.dir.
# It will be very handy when debugging.  You are not required to
# submit these in your final submission.

def start_senders(net):
    # Seconds to run iperf; keep this very high
    seconds = 3600
    server = net.get('h0')
    nflows = args.nflows * (args.n - 1)
    
    for h in range(nflows):
	hostNumber = (h % (args.n - 1)) + 1
	host = net.get('h%s' % hostNumber)
	host.cmd('touch {0}/output_file'.format(args.dir))
        host.popen('%s -c %s -p %s -t %d -i 1 -yc -Z %s > %s/%s' % (
            CUSTOM_IPERF_PATH, server.IP(), 5001, seconds, args.cong, args.dir, "output_file"),shell=True)
    return

#TODO: Start attack flow in a daemon thread to periodically 
# send 
def start_attacker(net):
    return
def main():
    "Create network and run Buffer Sizing experiment"

    start = time()
    # Reset to known state
    topo = StarTopo(n=args.n, bw_host=args.bw_host,
                    delay='%sms' % (args.delay/2),
                    bw_net=args.bw_net, maxq=args.maxq)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNodeConnections(net.hosts)
    net.pingAll()

    start_receiver(net)

    start_tcpprobe()

    cprint("Starting experiment", "green")

    start_attacker(net)

    start_senders(net)

    #TODO: measure the throughput of the normal flow(s)
    # and figure out how to plot that like figure 4 in the paper

    # Shut down iperf processes
    os.system('killall -9 ' + CUSTOM_IPERF_PATH)

    net.stop()
    Popen("killall -9 top bwm-ng tcpdump cat mnexec", shell=True).wait()
    stop_tcpprobe()
    end = time()

if __name__ == '__main__':
    try:
        main()
    except:
        print "-"*80
        print "Caught exception.  Cleaning up..."
        print "-"*80
        import traceback
        traceback.print_exc()
        os.system("killall -9 top bwm-ng tcpdump cat mnexec iperf; mn -c")

