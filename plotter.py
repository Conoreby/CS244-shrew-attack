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
                    dest="file")

args = parser.parse_args()

data = read_list(args.file)

m.rc('figure', figsize=(16, 6))
fig = figure()
ax = fig.add_subplot(111)
plt.title('Shrew-attack TCP throughput')
xs = col(0, data)
ys = col(1, data)
plt.plot(xs, ys)
plt.xlabel('seconds')
plt.ylabel("% thoroughput")
plt.grid(True)

plt.savefig("result.png")
