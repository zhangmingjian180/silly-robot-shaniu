import os.path
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import platform

from kivymd.app import MDApp

from utils import server_msg
from utils import set_status_bar_color

if platform != "android":
    Window.size = (432, 768)
Window.clearcolor = (1, 1, 1, 1)    # 如果你的背景是白色
Window.fullscreen = False

# 示例：白色背景，深色图标
set_status_bar_color("#FFFFFF", light_icons=False)

# setup fonts
LabelBase.register(
    name="NotoSansCJK-Regular",
    fn_regular="assets/fonts/NotoSansCJK-Regular.ttc",
)
LabelBase.register(
    name="Roboto",
    fn_regular="assets/fonts/NotoSansCJK-Regular.ttc",
)
LabelBase.register(
    name="RobotoLight",
    fn_regular="assets/fonts/NotoSansCJK-Regular.ttc",
)
LabelBase.register(
    name="RobotoMedium",
    fn_regular="assets/fonts/NotoSansCJK-Regular.ttc",
)

import views

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue" # "Red" "Indigo"  # 主色
        self.theme_cls.theme_style = "Light"       # 默认主题

    def build(self):
        root_widget = Builder.load_file(os.path.join("views", "screen_manager.kv"))
        return root_widget

    def send_cmd_to_server(self, cmd):
        server_msg.send_cmd(cmd)

if __name__ == "__main__":
    MainApp().run()
