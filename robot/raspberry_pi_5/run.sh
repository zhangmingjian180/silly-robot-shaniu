#!/bin/sh

work_dir=/opt/silly-robot-shaniu/robot/raspberry_pi_5/
host=cddes.cn
port=1935
robot_id=001

cd $work_dir

./a.out > /dev/null 2>&1 &
/usr/bin/ffmpeg -f v4l2 -i /dev/video0 -f flv rtmp://${host}:${port}/mytv/${robot_id} > /dev/null 2>&1
