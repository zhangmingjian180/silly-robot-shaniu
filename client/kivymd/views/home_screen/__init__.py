import os.path
from kivy.utils import platform
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from utils import set_status_bar_color

Builder.load_file(
    os.path.join("views", "home_screen", "home_screen.kv"))

class HomeScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def switch_theme(self):
        """切换浅色/深色模式"""
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )
        if self.theme_cls.theme_style == "Dark":
            Window.clearcolor = (0, 0, 0, 1)
            set_status_bar_color("#000000", light_icons=True)
        else:
            Window.clearcolor = (1, 1, 1, 1)    # 如果你的背景是白色
            set_status_bar_color("#FFFFFF", light_icons=False)
