# vscode-fold=2
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
import ctypes as ct

from data.frames.tabs_frame import MasterTabsFrame
from data.frames.version_frame import VersionFrame

from data.spt_mods import SPTMM
from data.spt_utils import Config, Utils

class UI(ctk.CTk):
    """
    The main window of the application.

    Children:
        - MainFrame (main_frame)
        - MasterTabsFrame (tabs_frame)
        - VersionFrame (version_frame)
    """
    def __init__(self):
        super().__init__()

        # Init config and utils
        self.cfg = Config()
        self.cfg.read_config()
        self.utils = Utils(self)
        self.sptmm = SPTMM(self)

        # Set window properties
        self.title("SPT Launcher")
        self.configure(bg="#282828")
        self._set_appearance_mode("Dark")

        self.w = 600  # width for the Tk root
        self.h = 200  # height for the Tk root
        self.minsize(self.w, self.h)

        # Resize and center window
        self.resize_and_center_window()

        # Configure row and column weights for resizing purposes
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create widgets
        self.create_widgets()

        # Set running flags
        self.server_running = False
        self.launcher_running = False

    def resize_and_center_window(self):
        # get screen width and height
        self.screen_width = self.winfo_screenwidth()  # width of the screen
        self.screen_height = self.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        self.x = (self.screen_width / 2) - (self.w / 2)
        self.y = (self.screen_height / 2) - (self.h / 2) - 200

        # set the window to a certain size and position it at the center of the screen
        self.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x, self.y))

    def create_widgets(self):
        # @ Main frame
        self.main_frame = MainFrame(self)
        self.main_frame.grid(padx=5, pady=5, column=0, row=0, sticky='nsew')

        # @ Tabs frame
        self.tabs_frame = MasterTabsFrame(self, self.main_frame)
        self.tabs_frame.grid(padx=5, pady=5, column=0, row=0)

        # # @ Version Frame
        self.version_frame = VersionFrame(self)
        self.version_frame.grid(padx=5, pady=5, column=1, row=0, sticky='nsew')

class MainFrame(ctk.CTkFrame):
    width = 370
    height = 50

    def __init__(self, master: "UI", **kwargs):
        """
        Main frame (not version frame) within the main window.

        Parent:\n
                - UI

        Children:\n
                - MasterTabsFrame

        Args:
            master (UI): The master window.
        """
        super().__init__(
            master,
            width=self.width,
            height=self.height,
        )


def main():
    main = UI()
    main.mainloop()


if __name__ == "__main__":
    main()
