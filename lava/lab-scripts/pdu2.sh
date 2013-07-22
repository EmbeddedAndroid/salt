#!/bin/bash
# Example ./pdu1.sh <ip_addr> <port> <0/1>
if [ $2 -gt 0 ] && [ $2 -lt 9 ]
then
        if [ "$#" -eq 3 ]
        then
		echo "BANK 1: Controlling Port: $2"
		snmpset -v1 -c private $1 .1.3.6.1.4.1.19865.1.2.2.$2.0 i $3
        elif [ "$#" -eq 2 ]
        then
		echo "BANK 1: Resetting Port: $2"
		snmpset -v1 -c private $1 .1.3.6.1.4.1.19865.1.2.2.$2.0 i 0
                sleep 10
	        snmpset -v1 -c private $1 .1.3.6.1.4.1.19865.1.2.2.$2.0 i 1
        else
		echo "Too many arguments"
        fi
else
	echo "Port number is out of range"
fi

