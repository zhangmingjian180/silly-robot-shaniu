from kivy.utils import platform

if platform == "android":
    from .bluetooth_android import (
        run_get_robot_list,
        run_get_info,
        run_get_info_list,
        run_get_wifi_list,
        run_connect_wifi
    )
else:
    from .bluetooth_bleak import (
        run_get_robot_list,
        run_get_info,
        run_get_info_list,
        run_get_wifi_list,
        run_connect_wifi
    )
