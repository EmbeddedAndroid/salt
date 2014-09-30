#!/bin/bash
echo "Connected."
while true
do
    telnet $1 $2
    sleep 1 
done
