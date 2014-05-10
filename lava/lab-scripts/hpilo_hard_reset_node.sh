#!/bin/bash
/usr/local/lab-scripts/hpilo_power_off_node.exp $1
sleep 20
/usr/local/lab-scripts/hpilo_power_on_node.exp $1
