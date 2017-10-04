#!/bin/bash

# Utility functions
logfile="/home/pi/pi_ups/pi_ups.log"
bin_pi_ups="/usr/bin/python3 /home/pi/pi_ups/pi_ups.py"
function start_pi_ups {
	if [ -f $logfile ]; then
		rm $logfile
	fi
	$bin_pi_ups > $logfile 2>&1 &
}
function kill_pi_ups {
	pids=$(ps -ef | grep "pi_ups.py$" | awk '{print $2}')
	for pid in $pids; do
		kill $pid
	done
}

# Cleanup here
function cleanup {
	kill_pi_ups
	exit
}
trap "cleanup" SIGTERM

# pi_ups and other programs
start_pi_ups

# Monitoring
while true; do
    # No monitoring right now

	# Don't waste too many cpu cycles
	sleep 5
done
