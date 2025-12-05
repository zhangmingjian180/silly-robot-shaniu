import socket
import json

ID = "001"

class ServerMessages():
    def __init__(self, addr):
        self.server_addr = addr
        self.server_sock = socket.socket(type=socket.SOCK_DGRAM)

    def send_cmd(self, cmd:str):
        content = {"id": ID, "robot_cmd": cmd}
        content = bytes(json.dumps(content), "ascii")
        count = self.server_sock.sendto(content, self.server_addr)
        return True if count == len(content) else False

    def receive_msg(self):
        content, _ = self.server_sock.recvfrom(1024)
        content = json.loads(content)
        return content
