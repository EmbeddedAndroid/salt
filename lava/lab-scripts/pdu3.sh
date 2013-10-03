#!/bin/bash
# Example ./pdu3.sh <ip_addr> <port> <1/2>
if [ $2 -gt 0 ] && [ $2 -lt 9 ]
then
        if [ "$#" -eq 3 ]
        then
		echo "BANK 1: Controlling Port: $2"
		snmpset -v1 -c private 192.168.1.13 .1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.$2 i $3
        elif [ "$#" -eq 2 ]
        then
		echo "BANK 1: Resetting Port: $2"
		snmpset -v1 -c private 192.168.1.13 .1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.$2 i 2
                sleep 10
	        snmpset -v1 -c private 192.168.1.13 .1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.$2 i 1
        else
		echo "Too many arguments"
        fi
else
	echo "Port number is out of range"
fi
