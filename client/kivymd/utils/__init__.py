from kivy.utils import platform

def set_status_bar_color(color_hex, light_icons=False):
    pass

# run in android
if platform == "android":
    from utils.platform_android import set_status_bar_color

from . import server
SERVER_ADDR = ("cddes.cn", 7921)
server_msg = server.ServerMessages(SERVER_ADDR)
