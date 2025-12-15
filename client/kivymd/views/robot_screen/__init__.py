import os.path
from kivy.core.window import Window
from kivy.utils import platform
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen


from .ffmpeg_video import FfmpegVideo

Builder.load_file(
    os.path.join("views", "robot_screen", "robot1_screen.kv"))

class Robot1Screen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.old_clearcolor = None
        self.old_theme_style = None

    def on_pre_enter(self):
        if platform != "android":
            Window.size = (960, 540)
        else:
            from utils.platform_android import (
                set_orientation,
                set_status_bar_float,
                set_status_bar_icons_light
            )
            set_orientation("landscape")
            set_status_bar_float(True)
            set_status_bar_icons_light(True)
        self.old_theme_style = self.theme_cls.theme_style
        self.theme_cls.theme_style = "Dark"
        self.old_clearcolor = Window.clearcolor
        Window.clearcolor = (0, 0, 0, 1)
        self.app.send_cmd_to_server('o')

    def on_pre_leave(self):
        if platform != "android":
            Window.size = (432, 768)
        else:
            from utils.platform_android import (
                set_orientation,
                set_status_bar_float,
                set_status_bar_icons_light
            )
            set_orientation("portrait")
            set_status_bar_float(False)
            if self.old_theme_style == "Light":
                set_status_bar_icons_light(False)
        self.theme_cls.theme_style = self.old_theme_style
        Window.clearcolor = self.old_clearcolor
        self.app.send_cmd_to_server('p')
