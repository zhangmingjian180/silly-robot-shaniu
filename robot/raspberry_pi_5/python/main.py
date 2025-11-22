import socket
import json
import asyncio
import traceback
from motor_driver import MotorDriver
from log import logging

HOST = "cddes.cn"
PORT = 7922         # 服务器端口
LOCAL_PORT = 9000   # 本机端口，两边共享它


def create_shared_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", LOCAL_PORT))
    sock.setblocking(False)  # asyncio 必须非阻塞
    return sock


async def send_status(sock):
    addr = (HOST, PORT)
    while True:
        try:
            robot_stat = {"id": "001"}
            sock.sendto(json.dumps(robot_stat).encode("ascii"), addr)
            logging.debug("successful to send: %s", robot_stat)
            await asyncio.sleep(15)
        except Exception:
            logging.error(traceback.format_exc())


async def receive_cmd(sock):
    md = MotorDriver()

    loop = asyncio.get_running_loop() #get_event_loop()

    while True:
        try:
            data, addr = await loop.sock_recvfrom(sock, 1024)
            if not data:
                logging.debug("faild to receive: %s", str(addr))
                continue
            logging.debug("successful to receive: %s", str(data))
            r = json.loads(data)
            c = r["cmd"]

            if c == 'w': md.front()
            elif c == 's': md.back()
            elif c == 'a': md.left()
            elif c == 'd': md.right()
            elif c == 'q': md.left_rotate()
            elif c == 'e': md.right_rotate()
            elif c == 'f': md.stop()
            elif c == 'l': md.toggle_led()

        except Exception:
            logging.error(traceback.format_exc())

async def main():
    sock = create_shared_socket()

    await asyncio.gather(
        send_status(sock),
        receive_cmd(sock)
    )


if __name__ == "__main__":
    asyncio.run(main())

