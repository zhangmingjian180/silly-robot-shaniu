#!/bin/sh

if [ ! -e /var/log/silly-robot-shaniu ]; then
    mkdir /var/log/silly-robot-shaniu
fi

cp silly-robot-shaniu.service /lib/systemd/system/
systemctl daemon-reload
systemctl enable silly-robot-shaniu
service silly-robot-shaniu start
