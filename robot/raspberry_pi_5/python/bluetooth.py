import sys
sys.path.append("/usr/lib/python3/dist-packages")

import time
import json
from threading import Thread
from bluezero import peripheral

from wifi import scan_wifi, connect_wifi
from config import config
from log import logging

ID = config["id"]
SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
INFO_CHAR_UUID = '12345678-1234-5678-1234-56789abcdef1'
WIFI_CHAR_UUID = '12345678-1234-5678-1234-56789abcdef2'
WIFI_CON_CHAR_UUID = '12345678-1234-5678-1234-56789abcdef3'
WIFI_STATUS_CHAR_UUID = '12345678-1234-5678-1234-56789abcdef4'

def info_read_callback(options):
    info = {
        "id": ID
    }
    s = json.dumps(info)
    return list(bytearray(s, 'utf-8'))

def notify_long(characteristic, data: bytes):
    seq = 0
    total = len(data)
    PAYLOAD_SIZE = 16  # 保守值，稳定
    for i in range(0, total, PAYLOAD_SIZE):
        payload = data[i:i + PAYLOAD_SIZE]
        frame = bytes([
            0xAA,
            seq & 0xFF
        ]) + total.to_bytes(2, "little") + payload
        characteristic.set_value(list(frame))
        seq = (seq + 1) & 0xFF

def wifi_notify_callback(notifying, characteristic):
    if notifying:
        networks = scan_wifi()
        s = json.dumps(networks)
        notify_long(characteristic, bytes(s, 'utf-8'))

status = 255

def wifi_con_write_callback(value, options):
    logging.debug("wifi_con_write_callback: %s", str(value))
    buffer = json.loads(bytes(value))

    def connect_wifi_thread():
        global status
        status = connect_wifi(buffer["ssid"], buffer["password"])

    Thread(
        target=connect_wifi_thread,
        daemon=True
    ).start()
    logging.debug("wifi_con_write_callback: over")

def wifi_status_notify_callback(notifying, characteristic):
    global status
    if notifying:
        while True:
            characteristic.set_value([status])
            if status != 255:
                status = 255
                break
            time.sleep(1)
    else:
        status = 255

# 创建 Peripheral
robot_bluetooth = peripheral.Peripheral(
    adapter_address='2C:CF:67:47:CD:6E',
    local_name='RobotBLE'
)

# 添加 Service
robot_bluetooth.add_service(
    srv_id=1,
    uuid=SERVICE_UUID,
    primary=True
)

# 添加 Info Characteristic
robot_bluetooth.add_characteristic(
    srv_id=1,
    chr_id=1,
    uuid=INFO_CHAR_UUID,
    value=[],
    notifying=False,
    flags=['read'],
    read_callback=info_read_callback,
)

# 添加 Wifi Characteristic
robot_bluetooth.add_characteristic(
    srv_id=1,
    chr_id=2,
    uuid=WIFI_CHAR_UUID,
    value=[],
    notifying=False,
    flags=['notify'],
    notify_callback=wifi_notify_callback
)

robot_bluetooth.add_characteristic(
    srv_id=1,
    chr_id=3,
    uuid=WIFI_CON_CHAR_UUID,
    value=[],
    notifying=False,
    flags=['write'],
    write_callback=wifi_con_write_callback,
)

robot_bluetooth.add_characteristic(
    srv_id=1,
    chr_id=4,
    uuid=WIFI_STATUS_CHAR_UUID,
    value=[],
    notifying=False,
    flags=['notify'],
    notify_callback=wifi_status_notify_callback,
)

if __name__ == "__main__":
    logging.debug("bluetooth is running.")
    robot_bluetooth.publish()
