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
for period in 0.0 0.5 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5 5.0; do
	dir=$rootdir

	python shrewattack.py --bw-host 15 \
		--cong reno \
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
