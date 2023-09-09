# vscode-fold=2
import tkinter as tk

import customtkinter as ctk
from PIL import Image
from tkinterdnd2 import TkinterDnD

from data.frames.options_frame import OptionsFrame
from data.frames.tabs_frame import (
    LauncherTabFrame,
    MasterTabsFrame,
    ModsTabFrame,
    SettingsTabFrame,
)
from data.frames.version_frame import VersionFrame
from data.spt_mods import SPTMM
from data.spt_utils import Config, Utils

class UI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("SPT Launcher")
        self.configure(bg="#282828")

        self.w = 600  # width for the Tk root
        self.h = 200  # height for the Tk root
        self.minsize(self.w, self.h)

        # get screen width and height
        self.screen_width = self.winfo_screenwidth()  # width of the screen
        self.screen_height = self.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        self.x = (self.screen_width / 2) - (self.w / 2)
        self.y = (self.screen_height / 2) - (self.h / 2) - 200

        # set the window to a certain size and position it at the center of the screen
        self.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x, self.y))
        # self.geometry(f'{w}x{h} + {x} + {y}')

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Init config and utils
        self.cfg = Config()
        self.cfg.read_config()
        self.utils = Utils(self)

        self.images = {
            "settings": ctk.CTkImage(
                Image.open("data\\assets\\settings.png"), size=(15, 15)
            ),
            "add": ctk.CTkImage(Image.open("data\\assets\\add.png"), size=(15, 15)),
            "button": ctk.CTkImage(
                Image.open("data\\assets\\button.png"), size=(10, 10)
            ),
            "link": ctk.CTkImage(Image.open("data\\assets\\link.png"), size=(15, 15)),
        }

        self.create_widgets()

        self.server_running = False
        self.launcher_running = False

    def create_widgets(self):
        # @ Options frame
        self.options_frame = OptionsFrame(self)
        self.options_frame.grid(padx=5, pady=5, column=0, sticky=tk.NSEW)
        # Using pack makes the frames dynamcially resize
        # self.options_frame.pack(padx=10, pady=10, side='left', fill='both', expand=True)

        # @ Tabs frame
        self.tabs_frame = MasterTabsFrame(self, self.options_frame)
        self.tabs_frame.grid(padx=5, pady=5, column=0, row=0)

        # @ Launcher tab
        self.launcher_tab_frame = LauncherTabFrame(self, self.tabs_frame)
        self.launcher_tab_frame.grid(padx=5, pady=5, column=0, row=2)

        # # @ Mods tab
        self.mods_tab_frame = ModsTabFrame(self, self.tabs_frame)
        self.mods_tab_frame.grid(padx=5, pady=5, row=0, column=0, sticky=tk.NS)

        # # @ Settings tab
        self.settings_tab_frame = SettingsTabFrame(self, self.tabs_frame)
        self.settings_tab_frame.grid(padx=5, pady=5, row=0, column=0, sticky=tk.NS)

        # # @ Version Frame
        self.version_frame = VersionFrame(self)
        self.version_frame.grid(padx=5, pady=5, column=1, row=0, sticky=tk.NSEW)

    def show_frame(self, frames=[]):
        pass

    def hide_frame(self, frames=[]):
        for f in frames:
            f.grid_forget()


def main():
    main = UI()

    sptmm = SPTMM(main)

    # main.after(1000, main.utils.hotkeys.start, main)
    main.mainloop()


if __name__ == "__main__":
    main()
