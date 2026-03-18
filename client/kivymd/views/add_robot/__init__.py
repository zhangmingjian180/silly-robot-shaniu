from threading import Thread
import os.path
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.list.list import (
    MDListItem,
    MDListItemLeadingIcon,
    MDListItemHeadlineText,
    MDListItemSupportingText,
    MDListItemTertiaryText,
    MDListItemTrailingCheckbox
)
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.app import MDApp

from utils.bluetooth import run_get_info_list
from utils.data_file import add_to_json, read_json
from utils.config import config

Builder.load_file(
    os.path.join("views", "add_robot", "add_robot.kv"))

ROBOTS_FILE = config["robots_file"]

class AddRobot(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scan_info = None
        self.selected_info = set()
        self.app = MDApp.get_running_app()
        self.saved_info = [e["id"] for e in read_json(ROBOTS_FILE)]

    def back_home(self):
        self.app.refresh_screen("home")
        self.app.root.current = "home"

    def active_change(self, checkbox, active):
        if active:
            self.selected_info.add(checkbox.id)
        else:
            self.selected_info.remove(checkbox.id)

    def add_selected_to_file(self):
        info = []
        for e in self.scan_info:
            if e["id"] in self.selected_info:
                info.append(e)

        add_to_json(info, ROBOTS_FILE)
        for device in self.ids.devices_list.children:
            self.ids.devices_list.remove_widget(device)
        self.selected_info = set()
        self.saved_info = [e["id"] for e in read_json(ROBOTS_FILE)]
        self._on_load_done()

    def on_enter(self):
        Thread(
            target=self._load_devices,
            daemon=True
        ).start()

    def _load_devices(self):
        try:
            self.scan_info = run_get_info_list()
        except Exception:
            self.scan_info = []
        Clock.schedule_once(lambda dt: self._on_load_done())

    def _on_load_done(self):
        self.ids.loading_circular.active = False
        if len(self.scan_info) == 0:
            self.add_widget(
                MDLabel(
                    text="未发现机器人。如果机器刚启动，需等待3~4分钟以便蓝牙初始化。",
                    halign="center",
                    size_hint_x=0.8,
                    pos_hint={"center_x": 0.5}
                )
            )
            return
        for e in self.scan_info:
            if e["id"] not in self.saved_info:
                tail = MDListItemTrailingCheckbox(
                    id=e["id"],
                    on_active=self.active_change
                )
            else:
                tail = MDIcon(
                    icon="check",
                    pos_hint={"center_y": 0.5}
                )
            list_item = MDListItem(
                MDListItemLeadingIcon(
                    icon="robot-outline",
                ),
                MDListItemHeadlineText(
                    text="多尔斯机器人-" + e["id"],
                ),
                MDListItemSupportingText(
                    text=e["address"],
                ),
                tail
            )
            self.ids.devices_list.add_widget(list_item)
