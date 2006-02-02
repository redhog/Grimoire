#!/bin/sh
#
# grimoire     Start the default Grimoire server
#
# chkconfig: - 85 15
# description: Grimoire is a (remote) system and user management \
#              frameworkd.
# processname: grimoire
# config: /etc/Grimoire
# pidfile: /var/run/Grimoire.pid

. /etc/rc.d/init.d/functions

NAME=Grimoire
BIND=""

case "$1" in
	start)
	        echo -n "Starting Grimoire server: "
		daemon --check="$NAME" "bash -c \"grimoire '_' '_.trees.server.dirt$BIND(fork=1)' > '/var/run/$NAME.pid'\""
		echo
		;;
	stop)
	        echo -n 'Stopping Grimoire server.'
	        killproc "$NAME"
		echo
		;;
	restart | force-reload)
		$0 stop
		sleep 2
		$0 start
		;;
        status)
	        ;;
	*)
		echo "Usage: /etc/init.d/grimoire {start|stop|restart|force-reload}"
		exit 1 
esac

exit 0
