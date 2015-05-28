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

for file in args.files:
	data = read_list(file)

#def skip_last(iterator):
#    prev = next(iterator)
#    for item in iterator:
#        yield prev
#        prev = item

#thoroughput = []
#iterate over all graphs
#intervals = [1.0, 2.0, 3.0, 4.0, 5.0]
#maxv = 0
#for l in intervals:
#	print "test" 
#	rates = []
#	ifile = open('shrewattack-Apr30-08:21/'+str(l)+'-bwm.txt', "rb")
#	reader = csv.reader(ifile)
#	for row in skip_last(reader):
#		rates.append(float(row[3]))
	#remove first 20
	#rates=rates:[20:]
#	average = sum(rates)
#	average = average / float(len(rates))
#	if maxv < average:
#		maxv = average
#	thoroughput.append( avg(rates) )
#	ifile.close()
	xs = col(0, data)
	ys = col(1, data)
	plt.plot(
m.rc('figure', figsize=(16, 6))
fig = figure()
ax = fig.add_subplot(111)
#plt.ylim(0, maxv)
plt.title('Shrew-attack TCP throughput')
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
