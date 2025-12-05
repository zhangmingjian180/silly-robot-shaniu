from kivy.core.text import LabelBase
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import StringProperty

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
        MDDialog,
        MDDialogHeadlineText,
        MDDialogSupportingText,
        MDDialogButtonContainer
)

from ffpyplayer.player import MediaPlayer

from utils import server

from kivy.core.window import Window
Window.clearcolor = (1, 1, 1, 1)    # 如果你的背景是白色
Window.fullscreen = False

from jnius import autoclass
from android.runnable import run_on_ui_thread

PythonActivity = autoclass('org.kivy.android.PythonActivity')
Color = autoclass('android.graphics.Color')
View = autoclass('android.view.View')

@run_on_ui_thread
def set_status_bar_color(color_hex, light_icons=False):
    activity = PythonActivity.mActivity
    window = activity.getWindow()

    # 确保 Android >= 21 (Lollipop)
    Build = autoclass('android.os.Build$VERSION')
    if Build.SDK_INT >= 21:
        # 取消半透明状态栏
        window.clearFlags(0x04000000)  # FLAG_TRANSLUCENT_STATUS
        window.addFlags(-0x80000000)   # FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS

        # 设置状态栏颜色
        window.setStatusBarColor(Color.parseColor(color_hex))

        # 如果 Android >= 23，设置状态栏图标颜色
        if Build.SDK_INT >= 23:
            decorView = window.getDecorView()
            flags = decorView.getSystemUiVisibility()
            if light_icons:
                # 浅色图标（用于深色背景）
                flags &= ~View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
            else:
                # 深色图标（用于浅色背景，如白色）
                flags |= View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
            decorView.setSystemUiVisibility(flags)

# 示例：白色背景，深色图标
set_status_bar_color("#FFFFFF", light_icons=False)

# 示例：黑色背景，浅色图标
# set_status_bar_color("#000000", light_icons=True)


LabelBase.register(
    name="NotoSansCJK-Regular",
    fn_regular="assets/fonts/NotoSansCJK-Regular.ttc",
)

LabelBase.register(
    name="Roboto",
    fn_regular="assets/fonts/NotoSansCJK-Regular.ttc",
)

LabelBase.register(
    name="RobotoLight",
    fn_regular="assets/fonts/NotoSansCJK-Regular.ttc",
)

LabelBase.register(
    name="RobotoMedium",
    fn_regular="assets/fonts/NotoSansCJK-Regular.ttc",
)

SERVER_ADDR = ("cddes.cn", 7921)

server_msg = server.ServerMessages(SERVER_ADDR)

class VideoScreen(MDFloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__()

    def on_touch_down(self, touch):
        # start collecting points in touch.ud
        # create a line to display the points
        userdata = touch.ud
        with self.canvas:
            Color(1, 1, 1, 0.5)
            d = 30.
            userdata['ellipse'] = Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
            userdata['line'] = Line(points=(touch.x, touch.y))
        return True

    def on_touch_move(self, touch):
        # store points of the touch movement
        try:
            d = 30.
            touch.ud['ellipse'].pos = (touch.x -  d / 2, touch.y -  d / 2)
            touch.ud['line'].points += [touch.x, touch.y]
            return True
        except KeyError as e:
            pass
        return True

    def on_touch_up(self, touch):
        if 'line' not in touch.ud:
            return True
        self.canvas.remove(touch.ud['ellipse'])
        self.canvas.remove(touch.ud['line'])
        sx = touch.ud['line'].points[0]
        sy = touch.ud['line'].points[1]
        ex, ey = touch.pos
        
        dx = ex - sx
        dy = ey - sy

        # 阈值（距离太短忽略）
        threshold = 40

        if abs(dx) > abs(dy) and abs(dx) > threshold:
            if dx > 0:
                server_msg.send_cmd("d")
            else:
                server_msg.send_cmd("a")

        elif abs(dy) > threshold:
            if dy > 0:
                server_msg.send_cmd("w")
            else:
                server_msg.send_cmd("s")

        else:
            server_msg.send_cmd("f")
        return True

class FfmpegVideo(VideoScreen, Image):
    url = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.start_player, 0)

    def start_player(self, dt):
        if not self.url:
            return
        self.player = MediaPlayer(self.url, ff_opts={'fflags': 'nobuffer', 'flags': 'low_delay'})
        Clock.schedule_interval(self.update, 1/60)

    def update(self, dt):
        if not hasattr(self, 'player'):
            return
        frame, val = self.player.get_frame()
        if frame is not None:
            img, t = frame
            if self.texture is None:
                self.texture = Texture.create(size=img.get_size(), colorfmt='rgb')
            self.texture.blit_buffer(img.to_bytearray()[0], colorfmt='rgb', bufferfmt='ubyte')
            self.texture.flip_vertical()
            self.canvas.ask_update()

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue" # "Red" "Indigo"  # 主色
        self.theme_cls.theme_style = "Light"       # 默认主题

    def switch_theme(self):
        """切换浅色/深色模式"""
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

    def login(self):
        """登录按钮事件"""
        username = self.root.get_screen("login").ids.username.text
        password = self.root.get_screen("login").ids.password.text
        if username == "admin" and password == "123":
            self.root.current = "home"
        else:
            self.show_dialog("登录失败", "用户名或密码错误")

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

    def send_cmd_to_server(self, cmd):
        server_msg.send_cmd(cmd)

    def enter_robot(self, robotname):
        self.root.current = robotname
        self.send_cmd_to_server('o')

    def exit_robot(self):
        self.send_cmd_to_server('p')
        self.root.current = "home"

if __name__ == "__main__":
    MainApp().run()
