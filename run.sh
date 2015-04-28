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
for period in 1 2 3 4 5; do
	dir=$rootdir/test

	python shrewattack.py --bw-host 15 \
		--cong reno \
		--bw-net 1.5 \
		--delay 12 \
		--dir $dir \
		--iperf $iperf \
		--period $period \
		--length 0.150
		#TODO: add extra necessary params

	#TODO: Plot the correct results
	python $plotpath/plot_queue.py -f $dir/qlen_$iface.txt -o $dir/q.png
	python $plotpath/plot_tcpprobe.py -f $dir/tcp_probe.txt -o $dir/cwnd.png --histogram
done
done

cat $rootdir/*/result.txt | sort -n -k 1
python plot-results.py --dir $rootdir -o $rootdir/result.png
echo "Started at" $start
echo "Ended at" `date`
