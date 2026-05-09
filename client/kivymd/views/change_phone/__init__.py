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
from utils.server_http import apt_get_captcha, api_sms_code, api_post_user_me_phone
from utils.storage import get_info, get_token

Builder.load_file(
    os.path.join("views", "change_phone", "change_phone.kv"))

class ChangePhone(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.old_phone_captcha_id = None
        self.new_phone_captcha_id = None

    def update_old_phone_captcha(self):
        try:
            picture, captcha_id = apt_get_captcha()
        except Exception as e:
            self.show_dialog("获取验证码失败", e.args[0])
            return
        self.old_phone_captcha_id = captcha_id
        self.ids.old_phone_captcha_img.texture = Image(
            picture, ext="png").texture

    def update_new_phone_captcha(self):
        try:
            picture, captcha_id = apt_get_captcha()
        except Exception as e:
            self.show_dialog("获取验证码失败", e.args[0])
            return
        self.new_phone_captcha_id = captcha_id
        self.ids.new_phone_captcha_img.texture = Image(
            picture, ext="png").texture

    def on_enter(self):
        self.update_old_phone_captcha()
        self.update_new_phone_captcha()

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

    def send_old_phone_sms_code(self):
        # 这里调用接口发送短信
        phone = get_info().get("phone")
        code = self.ids.old_phone_captcha_code.text
        if not code:
            self.ids.old_phone_captcha_code.error_color = "red"
            self.ids.old_phone_captcha_code.error = True
            self.show_dialog("获取短信验证码失败", "图形验证码不能为空!")
            return
        try:
            api_sms_code(phone, code, self.old_phone_captcha_id)
        except Exception as e:
            self.show_dialog("获取短信验证码失败", e.args[0])
            return

        # 开始倒计时
        self.seconds = 60
        self.ids.old_phone_btn_send_code.disabled = True
        self.ids.old_phone_btn_send_code_text.text = f" {self.seconds}s后重试 "

        # 每秒执行一次
        self.event = Clock.schedule_interval(self.old_phone_update_timer, 1)

    def old_phone_update_timer(self, dt):
        self.seconds -= 1

        if self.seconds > 0:
            self.ids.old_phone_btn_send_code_text.text = f" {self.seconds:02d}s后重试 "
        else:
            # 倒计时结束
            self.event.cancel()
            self.ids.old_phone_btn_send_code_text.text = "重发验证码"
            self.ids.old_phone_btn_send_code.disabled = False

    def send_sms_code(self):
        # 这里调用接口发送短信
        old_phone = get_info().get("phone")
        phone = self.ids.phone.text
        if not phone:
            self.ids.phone.error_color = "red"
            self.ids.phone.error = True
            self.show_dialog("获取短信验证码失败", "手机号不能为空!")
            return
        if phone == old_phone:
            self.ids.phone.error_color = "red"
            self.ids.phone.error = True
            self.show_dialog("获取短信验证码失败", "不能与原手机号相同!")
            return
        code = self.ids.captcha_code.text
        if not code:
            self.ids.captcha_code.error_color = "red"
            self.ids.captcha_code.error = True
            self.show_dialog("获取短信验证码失败", "图形验证码不能为空!")
            return
        try:
            api_sms_code(phone, code, self.new_phone_captcha_id)
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

    def change_phone(self):
        old_phone_sms_code = self.ids.old_phone_sms_code.text
        if not old_phone_sms_code:
            self.ids.old_phone_sms_code.error_color = "red"
            self.ids.old_phone_sms_code.error = True
            self.show_dialog("修改手机失败", "原手机短信验证码不能为空!")
            return
        phone = self.ids.phone.text
        sms_code = self.ids.sms_code.text
        if not sms_code:
            self.ids.sms_code.error_color = "red"
            self.ids.sms_code.error = True
            self.show_dialog("修改手机失败", "新手机短信验证码不能为空!")
            return
        token = get_token()
        try:
            api_post_user_me_phone(token, old_phone_sms_code, phone, sms_code)
        except Exception as e:
            self.show_dialog("修改手机失败", e.args[0])
            return
        dialog = MDDialog(
            MDDialogHeadlineText(
                text="修改手机成功",
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
