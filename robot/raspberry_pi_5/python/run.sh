#!/bin/sh

work_dir=/opt/silly-robot-shaniu/robot/raspberry_pi_5/python
host=cddes.cn
port=1935
robot_id=001

if [ ! -e /var/log/silly-robot-shaniu ]; then
    mkdir /var/log/silly-robot-shaniu
fi

cd $work_dir

source /opt/miniconda3/bin/activate
python main.py &
/usr/bin/ffmpeg -fflags nobuffer -flags +low_delay -input_format mjpeg -s 1280x720 -framerate 30 -f v4l2 -i /dev/video0 -f flv -fflags nobuffer rtmp://${host}:${port}/mytv/${robot_id} > /dev/null 2>&1 &
wait
