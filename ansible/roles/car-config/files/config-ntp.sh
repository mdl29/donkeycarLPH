#!/bin/bash

get_manager() {
	avahi-browse -r -t _http._tcp | awk -F'[] []' '/_donkeycarmanager/ { getline; getline; getline; print $7; end }'
}

MANAGER="$(get_manager)"
count="0"
while [ -z "$MANAGER" ] && [ "$count" -lt "16" ]; do
	logger "Failed to get donkeycar manager's ip, retrying ($((count + 1)))"
	sleep 1
	MANAGER="$(get_manager)"
	((count++))
done

if [ "$count" -gt "15" ]; then
	logger "Couldn't get the donkeycar manager's ip"
	exit 1
fi

logger "Got donkeycar manager ip: $MANAGER"

sed -i "/^server/ s/.*/server $MANAGER prefer iburst/g" /etc/ntp.conf

timedatectl set-timezone Europe/Paris
