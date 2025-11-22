from datetime import datetime, timedelta, UTC
import socket
import multiprocessing
import threading
import json
import traceback
import redis

from log import logging

redis_db = redis.Redis()
ADDR_ROBOT_SERVER = ("0.0.0.0", 7922)
ADDR_CLIENT_SERVER = ("0.0.0.0", 7921)
sock_robot_server = socket.socket(type=socket.SOCK_DGRAM)
sock_robot_server.bind(ADDR_ROBOT_SERVER)

# build server of client
def key_server():
    sock = socket.socket(type=socket.SOCK_DGRAM)
    sock.bind(ADDR_CLIENT_SERVER)
    while True:
        try:
            buf, addr_client = sock.recvfrom(1024)
            logging.debug("successful to receive: %s", str(buf))
            r = json.loads(buf)
            _addr = "silly:%s:addr" % r["id"]
            if not redis_db.exists(_addr):
                content = {"code": 1002, "message": "The robot is not online"}
                content = bytes(json.dumps(content), "ascii")
                count = sock.sendto(content, addr_client)
                if count == len(content):
                    logging.debug("successful to send: %s, %s", str(content), str(addr_client))
                else:
                    logging.debug("failed to send: %s, %s", str(content), str(addr_client))
            else:
                addr_robot = redis_db.get(_addr).decode().split(':')
                addr_robot= (addr_robot[0], int(addr_robot[1]))
                content = {"cmd": r["robot_cmd"]}
                content = bytes(json.dumps(content), "ascii")
                count = sock_robot_server.sendto(content, addr_robot)
                if count == len(content):
                    logging.debug("successful to send: %s, %s", str(content), str(addr_robot))
                else:
                    logging.debug("failed to send: %s, %s", str(content), str(addr_robot))
        except Exception:
            logging.error(traceback.format_exc())

# build server of robot
def esp_server():
    while True:
        try:
            buf, addr = sock_robot_server.recvfrom(1024)
            logging.debug("successful to receive: %s, %s", str(buf), str(addr))
            _addr = "silly:%s:addr" % json.loads(buf)["id"]
            value = "%s:%s" % (addr[0], str(addr[1]))
            redis_db.set(_addr, value, ex=18)
            logging.debug("write %s: %s", _addr, value)
        except Exception:
            logging.error(traceback.format_exc())

if __name__ == "__main__":
    key_process = multiprocessing.Process(target=key_server)
    key_process.daemon = True
    key_process.start()

    esp_process = multiprocessing.Process(target=esp_server)
    esp_process.daemon = True
    esp_process.start()

    key_process.join()
    esp_process.join()

