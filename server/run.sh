#!/bin/sh

ss -K sport = :7921
ss -K sport = :7922

if [ ! -e /var/log/silly-robot-shaniu ]; then
    mkdir /var/log/silly-robot-shaniu
fi

cd /opt/silly-robot-shaniu/server

/usr/bin/python3 server.py &

wait
