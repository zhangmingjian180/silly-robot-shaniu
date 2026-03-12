import os.path
from kivy.utils import platform
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu

from utils import set_status_bar_color
from utils.data_file import read_json
from utils.config import config
from views.add_robot import AddRobot
from views.wifi_configure import WifiConfigure

ROBOTS_FILE = config["robots_file"]

Builder.load_file(
    os.path.join("views", "home_screen", "home_screen.kv"))

class RobotCard(MDCard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.robot = None
        self.app = MDApp.get_running_app()

    def menu_callback(self, x):
        print(x)

    def menu_open(self):
        menu_items = [
            {
                "leading_icon": "pencil-outline",
                "text": "重命名",
                "on_release": lambda x="hello": self.menu_callback(x),
            },
            {
                "leading_icon": "information",
                "text": "详细信息",
                "on_release": lambda x="hello": self.menu_callback(x),
            },
            {
                "leading_icon": "trash-can-outline",
                "text": "删除",
                "on_release": lambda x="hello": self.menu_callback(x),
            }
        ]
        MDDropdownMenu(
            caller=self.ids.card_menu_module,
            items=menu_items
        ).open()

    def set(self, robot):
        self.robot = robot
        self.ids.label.text = "多尔斯机器人-" + self.robot["id"]
        return self
    
    def on_release(self):
        self.app.current_robot = self.robot
        self.app.root.current = "robot"

    def goto_wifi_configure(self):
        if self.app.root.has_screen("wifi_configure"):
            self.app.root.remove_widget(self.app.root.get_screen("wifi_configure"))
        self.app.root.add_widget(WifiConfigure())
        self.app.current_robot = self.robot
        self.app.root.current = "wifi_configure"

class HomeScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.robots = read_json(ROBOTS_FILE)

    def on_kv_post(self, base_widget):
        for robot in self.robots:
            self.ids.box_r.add_widget(self.create_robot_card(robot), index=1)

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

    def goto_add_robot(self):
        if self.app.root.has_screen("add_robot"):
            self.app.root.remove_widget(self.app.root.get_screen("add_robot"))
        self.app.root.add_widget(AddRobot())
        self.app.root.current = "add_robot"

    def create_robot_card(self, robot):
        return RobotCard().set(robot)
