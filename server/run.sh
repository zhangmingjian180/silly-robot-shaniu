#!/bin/bash

ss -K sport = :7921
ss -K sport = :7922

if [ ! -e /var/log/silly-robot-shaniu ]; then
    mkdir /var/log/silly-robot-shaniu
fi

cd /opt/silly-robot-shaniu/server
source ../venv-py312/bin/activate

python3 server.py &

wait
