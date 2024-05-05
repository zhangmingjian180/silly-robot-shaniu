import socket
import multiprocessing
import threading

from log import logging

queue = multiprocessing.Queue()
lock = threading.Lock()

def socket_thread(subs):
    while True:
        try:
            i = subs.recv(1)
        except:
            return
        if i == b'':
            logging.warning("connection client interrupt %s." % str(subs))
            return
        logging.debug(str(i))
        with lock:
            queue.put(i)

def key_server():
    addr = ("0.0.0.0", 7921)
    s = socket.socket()
    s.bind(addr)
    s.listen()
    while True:
        subs, _ = s.accept()
        logging.info("build connection %s" % str(subs))
        th = threading.Thread(target=socket_thread, args=[subs])
        th.start()

def esp_thread(subs):
    while True:
        with lock:
            i = queue.get()

        status = subs.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if status != 0:
            logging.warning("connection refused %s." % str(subs))
            queue.put(i)
            return

        try:
            count = subs.send(i)
            if count != len(i):
                logging.warning("failed to send %s." % str(subs))

        except:
            logging.warning("connection interrupted %s." % str(subs))
            queue.put(i)
            return

def esp_server():
    addr = ("0.0.0.0", 7922)
    s = socket.socket()
    s.bind(addr)
    s.listen()
    while True:
        subs, _ = s.accept()
        logging.info("build connection %s" % str(subs))
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

