import socket
import multiprocessing
import threading

from log import logging

queue = multiprocessing.Queue()
lock_r = threading.Lock()
lock_w = threading.Lock()

# client thread
def socket_thread(subs):
    while True:
        try:
            i = subs.recv(1)
        except Exception:
            return

        if i == b'':
            logging.warning("connection client interrupt %s.", str(subs))
            return

        with lock_w:
            queue.put(i)
            logging.debug("put: %s", str(i))
        logging.debug("successful to receive: %s", str(i))

# build server of client
def key_server():
    addr = ("0.0.0.0", 7921)
    s = socket.socket()
    s.bind(addr)
    s.listen()
    while True:
        subs, _ = s.accept()
        logging.info("build connection %s", str(subs))
        th = threading.Thread(target=socket_thread, args=[subs])
        th.start()

# robot thread
def esp_thread(subs):
    while True:
        with lock_r:
            i = queue.get()
            logging.debug("get: %s", str(i))
        try:
            count = subs.send(i)
        except Exception:
            logging.warning("connection interrupted %s.", str(subs))
            return
        if count != len(i):
            logging.warning("failed to send %s.", str(subs))
            return

        # check if connection is ok
        status = subs.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if status != 0:
            logging.warning("failed to check send %s.", str(subs))
            return
        recv_flag = subs.recv(1)
        if recv_flag ==  b'':
            logging.warning("can not receive flag %s.", str(subs))
            return
        logging.debug("successful to send: %s", str(i))

# build server of robot
def esp_server():
    addr = ("0.0.0.0", 7922)
    s = socket.socket()
    s.bind(addr)
    s.listen()
    while True:
        subs, _ = s.accept()
        logging.info("build connection %s", str(subs))
        subs.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        th = threading.Thread(target=esp_thread, args=[subs])
        th.start()

if __name__ == "__main__":
    key_process = multiprocessing.Process(target=key_server)
    key_process.daemon = True
    key_process.start()

    esp_process = multiprocessing.Process(target=esp_server)
    esp_process.daemon = True
    esp_process.start()

    key_process.join()
    esp_process.join()

