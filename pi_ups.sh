#!/bin/bash

PID_PI_UPS_LAUNCHER=/var/run/pi_ups_launcher.pid
PI_UPS_LAUNCHER=/home/pi/pi_ups/pi_ups_launcher.sh

case "$1" in
	start)
		# Bail if the launcher has already started
		if [ -e $PID_PI_UPS_LAUNCHER -a -e /proc/`cat $PID_PI_UPS_LAUNCHER 2> /dev/null` ]; then
			echo "$0 already started"
			exit 1
		fi
		# Start launcher
		touch $PID_PI_UPS_LAUNCHER
		$PI_UPS_LAUNCHER &
		echo $! > $PID_PI_UPS_LAUNCHER
		;;
	stop)
		# Kill launcher
		if [[ -f "$PID_PI_UPS_LAUNCHER" ]]; then
			kill `cat $PID_PI_UPS_LAUNCHER`
			rm $PID_PI_UPS_LAUNCHER
		fi
		;;
esac
