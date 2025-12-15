from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import shprint
from os.path import join, exists
import sh


class FFmpegRtmpRecipe(Recipe):
    name = "ffmpeg"
    version = "4.3.1"
    url = "https://ffmpeg.org/releases/ffmpeg-{version}.tar.bz2"

    built_libraries = {
        "libavcodec.so": "libavcodec",
        "libavdevice.so": "libavdevice",
        "libavfilter.so": "libavfilter",
        "libavformat.so": "libavformat",
        "libavutil.so": "libavutil",
        "libpostproc.so": "libpostproc",
        "libswscale.so": "libswscale",
        "libswresample.so": "libswresample",
    }

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        toolchain = self.ctx.ndk_toolchain_dir

        env["SYSROOT"] = f"{toolchain}/sysroot"
        env["AR"] = f"{toolchain}/bin/llvm-ar"
        env["STRIP"] = f"{toolchain}/bin/llvm-strip"
        env["NM"] = f"{toolchain}/bin/llvm-nm"
        env["CC"] = f"{toolchain}/bin/aarch64-linux-android24-clang"
        env["CXX"] = f"{toolchain}/bin/aarch64-linux-android24-clang++"

        return env

    def build_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        env = self.get_recipe_env(arch)

        configure = sh.Command(join(build_dir, "configure"))

        configure_args = [
            "--disable-static",
            "--enable-shared",
            "--enable-pic",

            "--enable-gpl",
            "--enable-nonfree",
            "--enable-small",

            "--enable-protocol=rtmp",
            "--enable-demuxer=live_flv",
            "--enable-decoder=flv",

            "--arch=aarch64",
            "--target-os=android",
            "--enable-cross-compile",
            "--cross-prefix=aarch64-linux-android-",

            f"--sysroot={env['SYSROOT']}",
            f"--cc={env['CC']}",
            f"--cxx={env['CXX']}",
            f"--ar={env['AR']}",
            f"--strip={env['STRIP']}",
            f"--nm={env['NM']}",

            "--disable-programs",
            "--disable-doc",
            "--disable-debug",
        ]

        shprint(configure, *configure_args, _cwd=build_dir)
        shprint(sh.make, "-j4", _cwd=build_dir)

recipe = FFmpegRtmpRecipe()
