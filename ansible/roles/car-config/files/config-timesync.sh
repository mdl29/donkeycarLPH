#!/bin/sh

get_manager() {
	avahi-browse -r -t _http._tcp | awk -F'[] []' '/_donkeycarmanager/ { getline; getline; getline; print $7; end }'
}

MANAGER="$(get_manager)"
count="0"
while [ -z "$MANAGER" ] || [ "$count" -gt "15" ]; do
	sleep 1
	MANAGER="$(get_manager)"
	((count++))
done

if [ "$count" -gt "15" ]; then
	logger "Couldn't get the donkeycar manager's ip"
	exit 1
fi

{
	echo "[Time]"
	echo "NTP=$MANAGER:123"
} > /etc/systemd/timesyncd.conf

timedatectl set-nntp true
