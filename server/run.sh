#!/bin/sh

cd /opt/silly-robot-shaniu/server

/usr/bin/python3 server.py 1>/dev/null 2>&1 &

wait
