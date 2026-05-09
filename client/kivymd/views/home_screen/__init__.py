from threading import Thread
import os.path
from kivy.clock import Clock
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
from utils.data_file import read_json, update_json, delete_json, add_to_json
from utils.config import config
from utils.storage import exists_token, get_token
from utils.server_http import api_post_user_me_robots, api_get_user_me_robots
from views.add_robot import AddRobot
from views.wifi_configure import WifiConfigure
from views.navigation_drawer import NavigationDrawer

ROBOTS_FILE = config["robots_file"]

Builder.load_file(
    os.path.join("views", "home_screen", "home_screen.kv"))

class TipMDDialog(MDDialog):
    def __init__(self, title, text, *args, **kwargs):
        self._title = title
        self._text = text
        super().__init__(*args, **kwargs)

class InfoDialog(MDDialog):
    robot_info = None

    def __init__(self, robot, robot_name, *args, **kwargs):
        self.robot_info = (
            "设备ID：%s\n"
            "设备名：%s\n"
            "蓝牙地址：%s"
        ) % (robot["id"], robot_name, robot.get("address"))
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
        self.robot_name = self.robot.get("name", "多尔斯机器人-" + format(self.robot["id"], "03d"))
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
        self.has_token = exists_token()
        super().__init__(*args, **kwargs)
        self.error_text = None
        self.robots_download = None

    def account_on_press(self):
        if self.has_token:
            self.ids.nav_drawer.set_state("toggle")
        else:
            self.app.root.current = "login"

    def _upload_done(self):
        self.ids.loading_circular.active = False
        if self.error_text:
            TipMDDialog("上传错误！", self.error_text).open()
            self.error_text = None
        else:
            TipMDDialog("上传成功！", "信息已上传至云端").open()

    def _upload(self):
        token = get_token()
        robots = [robot["id"] for robot in self.robots]
        try:
            api_post_user_me_robots(token, robots)
        except Exception as e:
            self.error_text = str(e.args[0])
        Clock.schedule_once(lambda dt: self._upload_done())

    def cloud_arrow_up_on_press(self):
        if self.has_token:
            self.ids.loading_circular.active = True
            Thread(
                target=self._upload,
                daemon=True
            ).start()
        else:
            self.app.root.current = "login"

    def _download_done(self):
        self.ids.loading_circular.active = False
        if self.error_text:
            TipMDDialog("下载错误！", self.error_text).open()
            self.error_text = None
        else:
            old_robots_id = [robot["id"] for robot in self.robots]
            new_robots_id = [robot for robot in self.robots_download if robot not in old_robots_id]
            new_robots = [{"id": robot_id} for robot_id in new_robots_id]
            add_to_json(new_robots, ROBOTS_FILE)
            self.robots = read_json(ROBOTS_FILE)
            self.robots_download = None
            for robot in new_robots:
                self.ids.box_r.add_widget(self.create_robot_card(robot, self), index=1)
            TipMDDialog("下载成功！", "信息已下载至本地").open()

    def _download(self):
        token = get_token()
        try:
            self.robots_download = api_get_user_me_robots(token)
        except Exception as e:
            self.error_text = str(e.args[0])
        Clock.schedule_once(lambda dt: self._download_done())

    def cloud_arrow_down_on_press(self):
        if self.has_token:
            self.ids.loading_circular.active = True
            Thread(
                target=self._download,
                daemon=True
            ).start()
        else:
            self.app.root.current = "login"

    def on_kv_post(self, base_widget):
        for robot in self.robots:
            self.ids.box_r.add_widget(self.create_robot_card(robot, self), index=1)

    def delete_card(self, card):
        self.ids.box_r.remove_widget(card)
        self.robots.remove(card.robot)

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
