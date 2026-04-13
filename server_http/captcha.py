import random
import string
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

WIDTH = 120
HEIGHT = 40

def random_code(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_captcha_image(code: str):
    img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 字体（可换成本地字体更好看）
    try:
        font = ImageFont.truetype("NotoSansCJK-Regular.ttc", 28)
    except:
        font = None

    # 绘制文字
    for i, char in enumerate(code):
        draw.text(
            (10 + i * 25, random.randint(0, 10)),
            char,
            fill=random_color(),
            font=font
        )

    # 干扰线
    for _ in range(5):
        draw.line(
            (
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT)
            ),
            fill=random_color(),
            width=1
        )

    # 噪点
    for _ in range(30):
        draw.point(
            (random.randint(0, WIDTH), random.randint(0, HEIGHT)),
            fill=random_color()
        )

    buf = BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return buf


def random_color():
    return (
        random.randint(0, 150),
        random.randint(0, 150),
        random.randint(0, 150)
    )
