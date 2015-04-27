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
for period in #TODO: different period lengths; do
	dir=#TODO: dirname

	python buffersizing.py --bw-host 1000 \ #TODO: set value
		--cong reno \
		--bw-net 62.5 \ #TODO: set value
		--delay 43.5 \ #TODO: set value
		--dir $dir \
		-n 3 \
		--iperf $iperf
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
