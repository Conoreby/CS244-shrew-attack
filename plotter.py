import csv
from helper import *
import plot_defaults

from matplotlib.ticker import MaxNLocator
from pylab import figure


ifile  = open('test.txt', "rb")
reader = csv.reader(ifile)
rates = []
for row in reader:
    rates.append(row[8])        
ifile.close()
rates = map(float, rates)
#get percentages
maxRate = max(rates)
ratepercentage = [x / maxRate for x in rates]
print ratepercentage
m.rc('figure', figsize=(16, 6))
fig = figure()
ax = fig.add_subplot(111)
plt.plot(ratepercentage)
plt.ylabel("% thoroughput")
plt.grid(True)

plt.savefig("test.png")
