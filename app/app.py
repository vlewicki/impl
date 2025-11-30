import sys
import os
import dearcygui as dcg

from .components import MainWindow
from .helpers.font import make_font
from .helpers.theme import LightTheme

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class App(dcg.Context):
    def __init__(self):
        super().__init__()
        light_theme = LightTheme(self)
        theme = dcg.ThemeStyleImGui(self, frame_rounding=5, window_rounding=5, child_rounding=5)
        font = dcg.AutoFont(self, font_creator=make_font, main_font_path=resource_path('res/Roboto-Regular.ttf'))
        self.viewport.initialize(width=800, height=600, theme=dcg.ThemeList(self, children=[light_theme, theme]), font=font)
        MainWindow(self, primary=True)

    def run(self):
        while self.running:
            self.viewport.render_frame()
