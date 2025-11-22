from periphery import GPIO
import time

# BCM 引脚编号（你的原代码）
LB0, LB1 = 27, 22
LF0, LF1 = 10, 9
RF0, RF1 = 6, 13
RB0, RB1 = 19, 26

LED_PIN = 17

# 所有 GPIO 都来自 gpiochip4（Raspberry Pi 5）
GPIO_CHIP = "/dev/gpiochip4"

class MotorDriver:
    def __init__(self):
        pins = [LB0, LB1, LF0, LF1, RF0, RF1, RB0, RB1, LED_PIN]
        self.gpio = {}

        # 打开所有 GPIO，引脚设置为输出
        for p in pins:
            self.gpio[p] = GPIO(GPIO_CHIP, p, "out")
            self.gpio[p].write(False)

    def _set_pair(self, a, b, va, vb):
        self.gpio[a].write(bool(va))
        self.gpio[b].write(bool(vb))

    def rotate_forward(self, wheel):
        mapping = {
            "LB": (LB0, LB1),
            "LF": (LF0, LF1),
            "RF": (RF0, RF1),
            "RB": (RB0, RB1)
        }
        a, b = mapping[wheel]
        self._set_pair(a, b, 0, 1)

    def rotate_backward(self, wheel):
        mapping = {
            "LB": (LB0, LB1),
            "LF": (LF0, LF1),
            "RF": (RF0, RF1),
            "RB": (RB0, RB1)
        }
        a, b = mapping[wheel]
        self._set_pair(a, b, 1, 0)

    def front(self):
        for w in ["LF", "LB", "RF", "RB"]:
            self.rotate_forward(w)

    def back(self):
        for w in ["LF", "LB", "RF", "RB"]:
            self.rotate_backward(w)

    def left(self):
        self.rotate_backward("LF")
        self.rotate_forward("LB")
        self.rotate_forward("RF")
        self.rotate_backward("RB")

    def right(self):
        self.rotate_forward("LF")
        self.rotate_backward("LB")
        self.rotate_backward("RF")
        self.rotate_forward("RB")

    def left_rotate(self):
        self.rotate_backward("LF")
        self.rotate_backward("LB")
        self.rotate_forward("RF")
        self.rotate_forward("RB")

    def right_rotate(self):
        self.rotate_backward("RF")
        self.rotate_backward("RB")
        self.rotate_forward("LF")
        self.rotate_forward("LB")

    def stop(self):
        for p in [LB0, LB1, LF0, LF1, RF0, RF1, RB0, RB1]:
            self.gpio[p].write(False)

    def toggle_led(self):
        cur = self.gpio[LED_PIN].read()
        self.gpio[LED_PIN].write(not cur)

    def close(self):
        for pin in self.gpio.values():
            pin.close()

