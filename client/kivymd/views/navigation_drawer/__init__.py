import os.path
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from utils.storage import clear_token, get_info, clear_info

Builder.load_file(
    os.path.join("views", "navigation_drawer", "navigation_drawer.kv"))

class NavigationDrawer(MDNavigationDrawer):
    def __init__(self, *args, **kwargs):
        self.app = MDApp.get_running_app()
        info = get_info()
        self.info = info if info else {"phone": "", "id": 0}
        super().__init__(*args, **kwargs)

    def logout(self):
        clear_token()
        clear_info()
        self.app.root.current = "login"
