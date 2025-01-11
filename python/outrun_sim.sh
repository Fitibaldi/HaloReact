#!/bin/bash


# Check if a parameter is provided, otherwise use a default sleep time
SLEEP_TIME=${1:-20}

mosquitto_pub -h localhost -t pod_status -m "HELLO|N1"
mosquitto_pub -h localhost -t pod_status -m "HELLO|N2"

mosquitto_pub -h localhost -t pod_status -m "START|OUTRUN|MUTED"

mosquitto_pub -h localhost -t pod_status -m "STAT|N1|HIGH|Red"


echo "Starting the process..."
sleep $SLEEP_TIME
echo "Process completed after $SLEEP_TIME seconds."

mosquitto_pub -h localhost -t pod_status -m "STAT|N2|HIGH|Red"

