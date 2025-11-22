import logging

logging.basicConfig(
    filename="/var/log/silly-robot-shaniu/robot.log",
    format="[ %(asctime)s : %(levelname)s ] %(message)s",
    level=logging.DEBUG
)
