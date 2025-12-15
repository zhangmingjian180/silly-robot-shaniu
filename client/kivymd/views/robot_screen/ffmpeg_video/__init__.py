from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.image import Image

from kivymd.uix.floatlayout import MDFloatLayout
from ffpyplayer.player import MediaPlayer
from utils import server_msg

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

