import os.path
from kivy.utils import platform
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog

from utils import set_status_bar_color
from utils.data_file import read_json, update_json, delete_json
from utils.config import config
from views.add_robot import AddRobot
from views.wifi_configure import WifiConfigure
from views.navigation_drawer import NavigationDrawer

ROBOTS_FILE = config["robots_file"]

Builder.load_file(
    os.path.join("views", "home_screen", "home_screen.kv"))

class InfoDialog(MDDialog):
    robot_info = None

    def __init__(self, robot, robot_name, *args, **kwargs):
        self.robot_info = (
            "设备ID：%s\n"
            "设备名：%s\n"
            "蓝牙地址：%s"
        ) % (robot["id"], robot_name, robot["address"])
        super().__init__(*args, **kwargs)

class RenameDialog(MDDialog):
    robot_name = None

    def __init__(self, robot_name, *args, **kwargs):
        self.robot_name = robot_name
        super().__init__(*args, **kwargs)
        self.card = None
        self.robot_id = None

    def set(self, robot_id, card):
        self.robot_id = robot_id
        self.card = card
        return self

    def rename(self):
        newname = self.ids.newname.text
        self.card.rename(newname)
        update_json(self.robot_id, "name", newname, ROBOTS_FILE)
        self.dismiss()

class DeleteDialog(MDDialog):
    robot_name = None

    def __init__(self, grandparent, parent, robot_id, robot_name, *args, **kwargs):
        self.grandparent = grandparent
        self._parent = parent
        self.robot_id = robot_id
        self.robot_name = robot_name
        super().__init__(*args, **kwargs)

    def delete_robot(self):
        delete_json(self.robot_id, ROBOTS_FILE)
        self.grandparent.delete_card(self._parent)
        self.dismiss()

class RobotCard(MDCard):
    def __init__(self, _parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.robot = None
        self.robot_name = None
        self.app = MDApp.get_running_app()
        self.dropdown_menu = None
        self._parent = _parent

    def show_dialog_rename(self):
        RenameDialog(self.robot_name).set(self.robot["id"], self).open()
        self.dropdown_menu.dismiss()

    def show_dialog_info(self):
        InfoDialog(self.robot, self.robot_name).open()
        self.dropdown_menu.dismiss()

    def show_dialog_delete(self):
        DeleteDialog(self._parent, self, self.robot["id"], self.robot_name).open()
        self.dropdown_menu.dismiss()

    def menu_open(self):
        menu_items = [
            {
                "leading_icon": "pencil-outline",
                "text": "重命名",
                "on_release": lambda : self.show_dialog_rename(),
            },
            {
                "leading_icon": "information",
                "text": "详细信息",
                "on_release": lambda : self.show_dialog_info(),
            },
            {
                "leading_icon": "trash-can-outline",
                "text": "删除",
                "on_release": lambda : self.show_dialog_delete(),
            }
        ]
        self.dropdown_menu = MDDropdownMenu(
            caller=self.ids.card_menu_module,
            hor_growth="left",
            items=menu_items
        )
        self.dropdown_menu.open()

    def set(self, robot):
        self.robot = robot
        self.robot_name = self.robot.get("name", "多尔斯机器人-" + self.robot["id"])
        self.ids.label.text = self.robot_name
        return self

    def rename(self, newname):
        self.robot_name = newname
        self.ids.label.text = self.robot_name
    
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
        self.app = MDApp.get_running_app()
        self.robots = read_json(ROBOTS_FILE)
        super().__init__(*args, **kwargs)

    def on_kv_post(self, base_widget):
        for robot in self.robots:
            self.ids.box_r.add_widget(self.create_robot_card(robot, self), index=1)

    def delete_card(self, card):
        self.ids.box_r.remove_widget(card)

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

    def create_robot_card(self, robot, parent):
        return RobotCard(parent).set(robot)
