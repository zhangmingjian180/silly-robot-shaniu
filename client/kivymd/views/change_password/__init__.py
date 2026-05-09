import os
from kivy.lang import Builder
from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
        MDDialog,
        MDDialogHeadlineText,
        MDDialogSupportingText,
        MDDialogButtonContainer
)
from utils.server_http import api_post_user_me_password
from utils.storage import get_token

Builder.load_file(
    os.path.join("views", "change_password", "change_password.kv"))

class ChangePassword(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

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

    def change_password(self):
        old_password = self.ids.old_password.text
        if not old_password:
            self.ids.old_password.error_color = "red"
            self.ids.old_password.error = True
            self.show_dialog("修改密码失败", "原密码不能为空!")
            return
        new_password = self.ids.new_password.text
        if not new_password:
            self.ids.new_password.error_color = "red"
            self.ids.new_password.error = True
            self.show_dialog("修改密码失败", "新密码不能为空!")
            return
        if len(new_password) < 10 or len(new_password) > 20:
            self.ids.new_password.error_color = "red"
            self.ids.new_password.error = True
            self.show_dialog("修改密码失败", "新密码长度错误!")
            return
        new_password_confirm = self.ids.new_password_confirm.text
        if new_password != new_password_confirm:
            self.ids.new_password_confirm.error_color = "red"
            self.ids.new_password_confirm.error = True
            self.show_dialog("修改密码失败", "两次密码不一致!")
            return
        token = get_token()
        try:
            api_post_user_me_password(token, old_password, new_password)
        except Exception as e:
            self.show_dialog("修改密码失败", e.args[0])
            return
        dialog = MDDialog(
            MDDialogHeadlineText(
                text="修改密码成功",
                halign="left",
            ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="确定"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                spacing="8dp",
            ),
        )
        dialog.open()
