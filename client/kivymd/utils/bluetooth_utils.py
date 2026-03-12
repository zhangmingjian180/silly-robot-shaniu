SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
INFO_CHAR_UUID = "12345678-1234-5678-1234-56789abcdef1"
WIFI_CHAR_UUID = "12345678-1234-5678-1234-56789abcdef2"
WIFI_CON_CHAR_UUID = '12345678-1234-5678-1234-56789abcdef3'
WIFI_STATUS_CHAR_UUID = '12345678-1234-5678-1234-56789abcdef4'

FRAME_HEAD = 0xAA

class PacketAssembler:
    def __init__(self):
        self.buffer = bytearray()
        self.expected_len = None
        self.last_seq = None
        self.result = None

    def reset(self):
        self.buffer.clear()
        self.expected_len = None
        self.last_seq = None

    def feed(self, data: bytes):
        if len(data) < 4:
            return None
        head, seq = data[0], data[1]
        total = int.from_bytes(data[2:4], "little")
        payload = data[4:]
        if head != FRAME_HEAD:
            print("❌ bad frame head")
            self.reset()
            return None
        if self.last_seq is not None and ((self.last_seq + 1) & 0xFF) != seq:
            print("❌ seq error")
            self.reset()
            return None
        if self.expected_len is None:
            self.expected_len = total
        self.buffer.extend(payload)
        self.last_seq = seq
        if len(self.buffer) >= self.expected_len:
            self.result = bytes(self.buffer[:self.expected_len])
            self.reset()
            return self.result
        return None
