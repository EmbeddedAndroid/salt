#!/bin/bash
echo "Connected."
while true
do
    telnet $1 $2
    sleep 0.5
done
