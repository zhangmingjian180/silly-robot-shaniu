import os
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.core.image import Image
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
from utils.server_http import apt_get_captcha, api_sms_code, api_delete_user_me
from utils.storage import get_info, get_token, clear_token, clear_info

Builder.load_file(
    os.path.join("views", "delete_account", "delete_account.kv"))

class DeleteAccountDialog(MDDialog):
    def __init__(self, parent, *args, **kwargs):
        self._parent = parent
        super().__init__(*args, **kwargs)

    def click_button(self):
        self.dismiss()
        self._parent.delete_account()

class DeleteAccount(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.captcha_id = None

    def on_enter(self):
        self.update_captcha()

    def send_sms_code(self):
        # 这里调用接口发送短信
        phone = get_info().get("phone")
        code = self.ids.del_captcha.text
        if not code:
            self.ids.del_captcha.error_color = "red"
            self.ids.del_captcha.error = True
            self.show_dialog("获取短信验证码失败", "图形验证码不能为空!")
            return
        try:
            api_sms_code(phone, code, self.captcha_id)
        except Exception as e:
            self.show_dialog("获取短信验证码失败", e.args[0])
            return

        # 开始倒计时
        self.seconds = 60
        self.ids.btn_send_code.disabled = True
        self.ids.btn_send_code_text.text = f" {self.seconds}s后重试 "

        # 每秒执行一次
        self.event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.seconds -= 1

        if self.seconds > 0:
            self.ids.btn_send_code_text.text = f" {self.seconds:02d}s后重试 "
        else:
            # 倒计时结束
            self.event.cancel()
            self.ids.btn_send_code_text.text = "重发验证码"
            self.ids.btn_send_code.disabled = False

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

    def update_captcha(self):
        try:
            picture, captcha_id = apt_get_captcha()
        except Exception as e:
            self.show_dialog("获取验证码失败", e.args[0])
            return
        self.captcha_id = captcha_id
        self.ids.captcha_img.texture = Image(
            picture, ext="png").texture

    def delete_account(self):
        token = get_token()
        phone = get_info().get("phone")
        sms_code = self.ids.del_sms_code.text
        if not sms_code:
            self.ids.del_sms_code.error_color = "red"
            self.ids.del_sms_code.error = True
            self.show_dialog("注销失败", "短信验证码不能为空!")
            return
        try:
            api_delete_user_me(token, phone, sms_code)
        except Exception as e:
            self.show_dialog("注销失败", e.args[0])
            return
        clear_token()
        clear_info()
        dialog = MDDialog(
            MDDialogHeadlineText(
                text="注销成功",
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
        self.app.refresh_screen("home")
        self.app.root.current = "home"

    def click_button(self):
        DeleteAccountDialog(self).open()
