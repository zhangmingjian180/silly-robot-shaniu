import subprocess

def scan_wifi():
    cmd = ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "dev", "wifi", "list"]
    result = subprocess.check_output(cmd, encoding="utf-8")
    networks = []
    for line in result.strip().split("\n"):
        in_use, ssid, signal, security = line.split(":")
        networks.append({
            "ssid": ssid,
            "signal": int(signal),
            "security": security,
            "in_use": in_use == "*"
        })
    return networks

def connect_wifi(ssid, password=''):
    cmd = [
        "nmcli", "dev", "wifi", "connect", ssid,
        "password", password
    ] if password != '' else [
        "nmcli", "dev", "wifi", "connect", ssid
    ]
    cpl = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf-8'
    )
    return cpl.returncode
