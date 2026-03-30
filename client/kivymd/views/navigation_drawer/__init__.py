import os.path

from kivy.lang import Builder
from kivymd.uix.navigationdrawer import MDNavigationDrawer

Builder.load_file(
    os.path.join("views", "navigation_drawer", "navigation_drawer.kv"))

class NavigationDrawer(MDNavigationDrawer):
    pass
