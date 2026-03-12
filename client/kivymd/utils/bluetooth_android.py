import json
import time
from threading import Event
from jnius import autoclass
from android import activity

from .bluetooth_utils import (
    SERVICE_UUID,
    INFO_CHAR_UUID,
    WIFI_CHAR_UUID,
    WIFI_CON_CHAR_UUID,
    WIFI_STATUS_CHAR_UUID
)

from .bluetooth_utils import PacketAssembler
assembler = PacketAssembler()

PythonActivity = autoclass("cn.cddes.robot.MainActivity")

def run_get_robot_list():
    return PythonActivity.getRobotList()

def run_get_info(addr):
    r = PythonActivity.getInfo(SERVICE_UUID, INFO_CHAR_UUID, addr)
    r = bytes(r)
    if r == b'':
        return {"id": "XXX"}
    else:
        print("r ", str(r))
        return json.loads(r)

def run_get_info_list():
    infos = []
    print("start run_get_info_list")
    for addr in run_get_robot_list():
        print("**********")
        info = run_get_info(addr)
        info["address"] = addr
        infos.append(info)
        print("---------")
    print("infos" + str(infos))
    return infos

def run_get_wifi_list(addr):
    # print(run_get_robot_list())
    r = PythonActivity.getWifiList(SERVICE_UUID, WIFI_CHAR_UUID, addr)
    r = bytes(r)
    if r == b'':
        return {}
    else:
        print("getWifiList: ", str(r))
        return json.loads(r)

def run_connect_wifi(addr, ssid, password=""):
    data = bytes(json.dumps({
        "ssid": ssid,
        "password": password
    }), "utf-8")
    return PythonActivity.connectWifi(
        SERVICE_UUID,
        WIFI_CON_CHAR_UUID,
        WIFI_STATUS_CHAR_UUID,
        addr,
        data)
