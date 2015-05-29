import csv
from util.helper import *
import util.plot_defaults

from matplotlib.ticker import MaxNLocator
from pylab import figure

parser = argparse.ArgumentParser()

parser.add_argument('--file', '-f',
                    help="data file",
                    required=True,
                    action="store",
					nargs='+',
                    dest="files")

parser.add_argument('-o',
                    help="Output directory",
                    required=True,
                    action="store",
                    dest="dir")

args = parser.parse_args()

to_plot = []


cong = ['reno', 'newreno', 'tahoe', 'sack']
graphfiles = []
for file in args.files:
     for tcptype in cong:
          data = read_list(file + '/' + tcptype + '-0.03-raw_data.txt')
          xs = col(0, data)
          ys = col(1, data)
          plt.plot(xs, ys)
plt.title('Shrew-attack TCP throughput')
plt.legend(['reno', 'newreno', 'tahoe', 'sack'], loc='upper left')
#<<<<<<< 
plt.xlabel('seconds')
plt.ylabel("% thoroughput")
plt.grid(True)

plt.savefig("{0}/result.png".format(args.dir))
#=======
#plt.plot(intervals, thoroughput)
#plt.xlabel('seconds')
#plt.ylabel("% thoroughput")
#plt.grid(True)
#plt.savefig("thoroughput.png")
