from threading import Thread
import os.path
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.app import MDApp
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
from kivymd.uix.dialog import MDDialog

from utils.bluetooth import run_get_wifi_list, run_connect_wifi

Builder.load_file(
    os.path.join("views", "wifi_configure", "wifi_configure.kv"))

class WifiListItem(MDListItem):
    ssid = StringProperty()

class AuthDialog(MDDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssid = None
        self.caller = None

    def set(self, ssid, caller):
        self.ssid = ssid
        self.caller = caller
        supporting_text = f"请输入\"{ssid}\"密码："
        self.headline.text = supporting_text
        return self

    def connect(self):
        if self.password.text == '':
            return
        print(self.ssid, self.password.text)
        self.dismiss()
        self.caller.start_connect(
            self.ssid,
            self.password.text
        )

class WifiConfigure(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.scan_wifi = None
        self.current_list_item = None
        self.current_connected_status = None

    def set(self, current_connected_status=None):
        self.current_connected_status = current_connected_status

    def show_dialog(self):
        AuthDialog().set(
            self.current_list_item.ssid, caller=self
        ).open()

    def click(self, list_item):
        self.current_list_item = list_item
        self.start_connect(self.current_list_item.ssid)

    def start_connect(self, ssid, pwd=''):
        self.ids.loading_circular.active = True
        Thread(
            target=self._connect_wifi,
            args=(ssid, pwd),
            daemon=True
        ).start()

    def _connect_wifi(self, ssid, pwd):
        self.current_connected_status = run_connect_wifi(
            self.app.current_robot["address"],
            ssid, pwd
        )
        Clock.schedule_once(lambda dt: self._connected_done())

    def _connected_done(self):
        self.ids.loading_circular.active = False
        if self.current_connected_status != 0:
            self.show_dialog()
        else:
            self.ids.wifi_list.clear_widgets()
            self.ids.loading_circular.active = True
            self.on_enter()

    def on_enter(self):
        Thread(
            target=self._load_devices,
            daemon=True
        ).start()

    def _load_devices(self):
        try:
            self.scan_wifi = run_get_wifi_list(self.app.current_robot["address"])
        except Exception as e:
            print(e)
            self.scan_wifi = []
        Clock.schedule_once(lambda dt: self._load_done())

    def _load_done(self):
        self.ids.loading_circular.active = False
        if len(self.scan_wifi) == 0:
            self.add_widget(
                MDLabel(
                    text="未发现可用 Wi-Fi，请重试",
                    halign="center",
                    size_hint_x=0.8,
                    pos_hint={"center_x": 0.5}
                )
            )
            return

        in_use = None
        for e in self.scan_wifi:
            if e["in_use"]:
                in_use = e["ssid"]
        added = set()
        for e in self.scan_wifi:
            if e["ssid"] == '' or e["ssid"] in added:
                continue
            added.add(e["ssid"])
            wifi_strength = e["signal"] // 25 + 1
            wifi_strength = 4 if wifi_strength > 4 else wifi_strength
            tail = None if e["ssid"] != in_use else MDIcon(
                icon="check",
                pos_hint={"center_y": 0.5}
            )
            lock = '-lock' if e["security"] != "" else ""
            list_item = WifiListItem(
                MDListItemLeadingIcon(
                    icon=f"wifi-strength-{wifi_strength}{lock}",
                ),
                MDListItemHeadlineText(
                    text=e["ssid"],
                ),
                tail,
                ssid=e["ssid"],
                on_release=self.click
            )
            self.ids.wifi_list.add_widget(list_item)
