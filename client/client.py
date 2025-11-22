import json
import logging
import socket
import sys

from pynput import keyboard

logging.basicConfig(
    format="[ %(asctime)s : %(levelname)s ] %(message)s",
    level=logging.DEBUG)

logging.info("starting ...")

s = socket.socket(type=socket.SOCK_DGRAM)
addr = ("cddes.cn", 7921)
key_set = {'w', 's', 'a', 'd', 'q', 'e', 'f', 'l'}

logging.info("please type 'w s a d q e f l' to send, 'Enter' to exit.")


def on_press(key):
    if hasattr(key, "char"):
        cmd = key.char
        if cmd in key_set:
            content = {"id": "001", "robot_cmd": cmd}
            s.sendto(bytes(json.dumps(content), "ascii"), addr)

with keyboard.Listener(on_press=on_press) as lsn:
    input()

s.close()

# 恢复配置
logging.info("finished")



