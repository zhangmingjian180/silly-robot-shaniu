import os.path
import threading

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.image import Image
from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from ffpyplayer.player import MediaPlayer

Builder.load_file(
    os.path.join("views", "robot_screen", "ffmpeg_video", "ffmpeg_video.kv"))

class VideoScreen(MDFloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = MDApp.get_running_app()

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
                self.app.send_cmd_to_server("d")
            else:
                self.app.send_cmd_to_server("a")

        elif abs(dy) > threshold:
            if dy > 0:
                self.app.send_cmd_to_server("w")
            else:
                self.app.send_cmd_to_server("s")

        else:
            self.app.send_cmd_to_server("f")
        return True

class FfmpegVideo(VideoScreen, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.first_frame = True
        self.url = None
        self.player = None

    def start(self):
        robot_id = MDApp.get_running_app().current_robot["id"]
        self.url = f'rtmp://cddes.cn:1935/mytv/{robot_id}'
        self.create_placeholder_texture()
        self.ids.loading_circular.active = True
        self.first_frame = True
        Clock.schedule_once(self.start_player, 0)

    def stop(self):
        if self.player is None:
            return
        #self.player.close()
        Clock.unschedule(self.update)
        self.player = None

    def create_placeholder_texture(self):
        w, h = self.size
        self.texture = Texture.create(size=(w, h), colorfmt='rgb')
        byte = b'\000' * (w * h * 3)
        self.texture.blit_buffer(byte, colorfmt='rgb', bufferfmt='ubyte')
        self.canvas.ask_update()

    def start_player(self, dt):
        threading.Thread(target=self._init_player, daemon=True).start()

    def _init_player(self):
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
            if self.first_frame:
                self.first_frame = False
                self.ids.loading_circular.active = False
                self.texture = Texture.create(size=img.get_size(), colorfmt='rgb')
            self.texture.blit_buffer(img.to_bytearray()[0], colorfmt='rgb', bufferfmt='ubyte')
            self.texture.flip_vertical()
            self.canvas.ask_update()
