import os.path
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
        MDDialog,
        MDDialogHeadlineText,
        MDDialogSupportingText,
        MDDialogButtonContainer
)
from utils.server_http import api_user_login, api_get_user_me
from utils.storage import save_token, save_info

Builder.load_file(
    os.path.join("views", "login_screen", "login_screen.kv"))

class LoginScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

    def login(self):
        """登录按钮事件"""
        username = self.ids.username.text
        password = self.ids.password.text
        try:
            token = api_user_login(username, password)
            info = api_get_user_me(token)
        except Exception as e:
            self.show_dialog("登录失败", e.args[0])
            return
        save_token(token)
        save_info(info)
        self.app.refresh_screen("home")
        self.app.root.current = "home"

    def show_dialog(self, title, text):
        """通用对话框"""
        self.dialog = MDDialog(
            MDDialogHeadlineText(
                text=title,
                halign="left",
            ),
            MDDialogSupportingText(
                text=text,
                halign="left",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="确定"),
                    style="text",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                spacing="8dp",
            ),
        )
        self.dialog.open()

    def close(self):
        self.app.refresh_screen("home")
        self.app.root.current = "home"
