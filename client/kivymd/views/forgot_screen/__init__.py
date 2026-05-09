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
from utils.server_http import apt_get_captcha, api_sms_code, api_post_phone_password

Builder.load_file(
    os.path.join("views", "forgot_screen", "forgot_screen.kv"))

class ForgotScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()
        self.captcha_id = None

    def update_captcha(self):
        try:
            picture, captcha_id = apt_get_captcha()
        except Exception as e:
            self.show_dialog("获取验证码失败", e.args[0])
            return
        self.captcha_id = captcha_id
        self.ids.captcha_img.texture = Image(
            picture, ext="png").texture

    def on_enter(self):
        self.update_captcha()

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

    def send_sms_code(self):
        # 这里调用接口发送短信
        phone = self.ids.phone.text
        if not phone:
            self.ids.phone.error_color = "red"
            self.ids.phone.error = True
            self.show_dialog("获取短信验证码失败", "手机号不能为空!")
            return
        code = self.ids.captcha_code.text
        if not code:
            self.ids.captcha_code.error_color = "red"
            self.ids.captcha_code.error = True
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

    def reset_password(self):
        phone = self.ids.phone.text
        sms_code = self.ids.sms_code.text
        if not sms_code:
            self.ids.sms_code.error_color = "red"
            self.ids.sms_code.error = True
            self.show_dialog("重设密码失败", "短信验证码不能为空!")
            return
        password = self.ids.password.text
        if not password:
            self.ids.password.error_color = "red"
            self.ids.password.error = True
            self.show_dialog("重设密码失败", "密码不能为空!")
            return
        if len(password) < 10 or len(password) > 20:
            self.ids.password.error_color = "red"
            self.ids.password.error = True
            self.show_dialog("重设密码失败", "密码长度错误!")
            return
        password_confirm = self.ids.password_confirm.text
        if password != password_confirm:
            self.ids.password_confirm.error_color = "red"
            self.ids.password_confirm.error = True
            self.show_dialog("重设密码失败", "两次密码不一致!")
            return
        try:
            api_post_phone_password(phone, sms_code, password)
        except Exception as e:
            self.show_dialog("重设密码失败", e.args[0])
            return
        dialog = MDDialog(
            MDDialogHeadlineText(
                text="重设密码成功",
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
        self.app.root.current = "login"
