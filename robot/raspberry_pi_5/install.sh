#!/bin/sh

apt install -y libcairo2-dev libgirepository1.0-dev python3-dbus

if [ ! -e /var/log/silly-robot-shaniu ]; then
    mkdir /var/log/silly-robot-shaniu
fi

cp silly-robot-shaniu.service /lib/systemd/system/
systemctl daemon-reload
systemctl enable silly-robot-shaniu
service silly-robot-shaniu start
