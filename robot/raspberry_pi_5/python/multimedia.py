import subprocess

FFMPEG_CMD = [
    "ffmpeg",
    "-loglevel", "error",
    "-fflags", "nobuffer",
    "-flags", "+low_delay",
    "-input_format", "mjpeg",
    "-s", "1280x720",
    "-framerate", "30",
    "-f", "v4l2",
    "-i", "/dev/video0",
    "-f", "flv",
    "-fflags", "nobuffer",
    "rtmp://cddes.cn:1935/mytv/001"
]

class Ffmpeg:
    def __init__(self, cmd, log_file):
        self.cmd = cmd
        self.log_file = log_file
        self.process = None

    def start(self):
        log = open(self.log_file, mode="a")

        # 使用 Popen 让进程持续运行
        self.process = subprocess.Popen(
            self.cmd,
            stdout=log,
            stderr=subprocess.STDOUT
        )

    def wait(self):
        # 如果希望等待结束，可用：
        self.process.wait()

    def stop(self):
        self.process.terminate()

    def is_running(self):
        r = self.process.poll()
        if r is None:
            return True
        return False
