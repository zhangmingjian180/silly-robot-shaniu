from jnius import autoclass
from android.runnable import run_on_ui_thread

@run_on_ui_thread
def set_status_bar_icons_light(is_light:bool):
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    View = autoclass('android.view.View')
    
    activity = PythonActivity.mActivity
    window = activity.getWindow()
    
    Build = autoclass('android.os.Build$VERSION')
    # 如果 Android >= 23，设置状态栏图标颜色
    if Build.SDK_INT >= 23:
        decorView = window.getDecorView()
        flags = decorView.getSystemUiVisibility()
        if is_light:
            # 浅色图标（用于深色背景）
            flags &= ~View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
        else:
            # 深色图标（用于浅色背景，如白色）
            flags |= View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
        decorView.setSystemUiVisibility(flags)


@run_on_ui_thread
def set_status_bar_color(color_hex, light_icons=False):
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Color = autoclass('android.graphics.Color')
    LayoutParams = autoclass("android.view.WindowManager$LayoutParams")
    
    activity = PythonActivity.mActivity
    window = activity.getWindow()

    # 确保 Android >= 21 (Lollipop)
    Build = autoclass('android.os.Build$VERSION')
    if Build.SDK_INT >= 21:
        # 取消半透明状态栏
        window.clearFlags(LayoutParams.FLAG_TRANSLUCENT_STATUS)
        window.addFlags(LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)

        # 设置状态栏颜色
        window.setStatusBarColor(Color.parseColor(color_hex))
        set_status_bar_icons_light(light_icons)

@run_on_ui_thread
def set_status_bar_float(is_float:bool):
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    LayoutParams = autoclass("android.view.WindowManager$LayoutParams")
    
    activity = PythonActivity.mActivity
    window = activity.getWindow()

    if is_float:
        window.addFlags(LayoutParams.FLAG_TRANSLUCENT_STATUS)
    else:
        window.clearFlags(LayoutParams.FLAG_TRANSLUCENT_STATUS)

def set_orientation(orientation:str):
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    ActivityInfo = autoclass('android.content.pm.ActivityInfo')

    activity = PythonActivity.mActivity
    if orientation == "landscape":
        activity.setRequestedOrientation(
            ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
        )
    elif orientation == "portrait":
        activity.setRequestedOrientation(
            ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
        )
    else:
        pass
