#!/bin/bash
./hpilo_power_off_node.exp $1
sleep 20
./hpilo_power_on_node.exp $1
