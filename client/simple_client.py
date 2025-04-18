import sys
import os
import termios
import socket
import sys

from log import logging

logging.info("starting ...")

s = socket.socket()
addr = ("localhost", 7921)

try:
    s.connect(addr)
except TimeoutError:
    logging.error("time out to connet %s"%str(addr))
    sys.exit(0)
except ConnectionRefusedError:
    logging.error("Connection Refused to connet %s"%str(addr))
    sys.exit(0)
logging.info("conneted %s"%str(addr))
logging.info("please type 'w s a d' to send, 'Enter' to exit, others no action")

key_set = {b'w', b's', b'a', b'd', b'q'}

i = input().encode("ascii")
if i in key_set:
    count = s.send(i)
    if count != len(i):
        logging.error("failed to send.")
while i != b'q':
    i = input().encode("ascii")
    if i in key_set:
        count = s.send(i)
        if count != len(i):
            logging.error("failed to send.")

s.close()

# 恢复配置
logging.info("finished")
