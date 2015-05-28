#!/bin/bash

# Exit on any failure
set -e

# Check for uninitialized variables
set -o nounset

ctrlc() {
	killall -9 python
	mn -c
	exit
}

trap ctrlc SIGINT

start=`date`
exptid=`date +%b%d-%H:%M`

rootdir=shrewattack-$exptid
plotpath=util
iperf=~/iperf-patched/src/iperf

for run in 1; do
for period in 0.5 0.6 0.7 0.8 0.9 0.95 1.0 1.05 1.1 1.15 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2.0 2.5 3.0 3.5 4.0 4.5 5.0; do
	dir=$rootdir

	python shrewattack.py --bw-host 15 \
		--cong sack \
		--bw-net 1.5 \
		--delay 2 \
		--dir $dir \
		--iperf $iperf \
		--period $period \
		--length 0.150
		#TODO: add extra necessary params

	#TODO: Plot the correct results
    python convert_data.py -f $dir/$period-bwm.txt -p $period -o $dir/raw_data.txt
done
done

python plotter.py -f $dir/raw_data.txt
echo "Started at" $start
echo "Ended at" `date`
