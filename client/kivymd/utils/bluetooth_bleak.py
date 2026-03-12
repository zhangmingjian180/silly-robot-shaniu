import asyncio
import json
from bleak import BleakScanner, BleakClient

from .bluetooth_utils import (
    SERVICE_UUID,
    INFO_CHAR_UUID,
    WIFI_CHAR_UUID,
    WIFI_CON_CHAR_UUID,
    WIFI_STATUS_CHAR_UUID
)

from .bluetooth_utils import PacketAssembler
assembler = PacketAssembler()

def on_notify(_, data: bytearray):
    msg = assembler.feed(bytes(data))
    if msg:
        print("✅ complete message:")

async def get_robot_list():
    print("🔍 扫描蓝牙设备...")
    devices = await BleakScanner.discover()
    print(devices)
    robots = []
    for d in devices:
        if d.name == "RobotBLE":
            robots.append(d)
    return robots

async def get_info(addr):
    client = BleakClient(addr)
    async with client as client:
        print("🔗 已连接机器人")
        r = await client.read_gatt_char(INFO_CHAR_UUID)
        r = json.loads(bytes(r))
        return r

async def get_info_list():
    info_list = []
    grl = await get_robot_list()
    for e in grl:
        t = await get_info(e.address)
        t["address"] = e.address
        info_list.append(t)
    return info_list

async def get_wifi_list(addr):
    await get_robot_list()
    client = BleakClient(addr)
    async with client as client:
        print("🔗 已连接机器人")
        await client.start_notify(WIFI_CHAR_UUID, on_notify)
        await asyncio.sleep(3)
        await client.stop_notify(WIFI_CHAR_UUID)
        return json.loads(assembler.result)

async def connect_wifi(addr, ssid, password=""):
    data = bytes(json.dumps({
        "ssid": ssid,
        "password": password
    }), "utf-8")
    result_event = asyncio.Event()
    wifi_result = {"status": None}

    def notify_handler(_, value: bytearray):
        status = int.from_bytes(value, "little")
        print("📡 WiFi 状态:", status)
        if status != 255:   # 非 connecting
            wifi_result["status"] = status
            result_event.set()

    async with BleakClient(addr) as client:
        print("🔗 已连接机器人")
        await client.write_gatt_char(WIFI_CON_CHAR_UUID, data)
        await client.start_notify(WIFI_STATUS_CHAR_UUID, notify_handler)
        try:
            await asyncio.wait_for(result_event.wait(), timeout=120)
        except asyncio.TimeoutError:
            return -1
        finally:
            await client.stop_notify(WIFI_STATUS_CHAR_UUID)
        return wifi_result["status"]

def run_get_robot_list():
    return asyncio.run(get_robot_list())

def run_get_info(addr):
    return asyncio.run(get_info(addr))

def run_get_info_list():
    return asyncio.run(get_info_list())

def run_get_wifi_list(addr):
    return asyncio.run(get_wifi_list(addr))

def run_connect_wifi(addr, ssid, password=''):
    return asyncio.run(connect_wifi(addr, ssid, password=''))

if __name__ == "__main__":
    addr = "2C:CF:67:47:CD:6E"
    ssid = "ZR_D467590"
    #ssid = "ziroom02-703"
    #password = "efdsdsdsdsw"
    password = ''
    #print(run_get_info_list())
    print(run_get_wifi_list(addr))
    print(run_connect_wifi(addr, ssid, password))
