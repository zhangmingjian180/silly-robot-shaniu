import logging
import socket
import sys

from pynput import keyboard

logging.basicConfig(
    format="[ %(asctime)s : %(levelname)s ] %(message)s",
    level=logging.DEBUG)

logging.info("starting ...")

s = socket.socket()
addr = ("zhangmingjian180.love", 7921)
key_set = {b'w', b's', b'a', b'd', b'q', b'l'}

try:
    s.connect(addr)
except TimeoutError:
    logging.error("time out to connet %s"%str(addr))
    sys.exit(0)
except ConnectionRefusedError:
    logging.error("Connection Refused to connet %s"%str(addr))
    sys.exit(0)
logging.info("conneted %s"%str(addr))
logging.info("please type 'w s a d' to send, 'Enter' to exit.")


def on_press(key):
    if hasattr(key, "char"):
        i = bytes(key.char, "ascii")
        if i in key_set:
            count = s.send(i)
            if count != len(i):
                logging.error("failed to send.")

with keyboard.Listener(on_press=on_press) as lsn:
    input()

s.close()

# 恢复配置
logging.info("finished")



