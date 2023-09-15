# vscode-fold=4
import os
import subprocess
import threading
import typing
import time
from configparser import ConfigParser

import customtkinter as ctk
from PIL import Image

from ahk import AHK, Hotkey
from ahk.directives import NoTrayIcon
from termcolor import cprint
from win32api import GetSystemMetrics
import win32gui

if typing.TYPE_CHECKING:
    from spt import UI

CONFIG_FILE = os.path.join(os.getcwd(), "myconfig.ini")

class Config(ConfigParser):
    """
    This class handles the config file.\n
    Args:
        None
    """
    def __init__(self, *args, **kwargs):
        # super init ConfigParser class
        super().__init__()
        cprint("Loading config...", "yellow")

        # read the config file
        self.read_config()
        cprint("Loading config complete.", "green")

    def read_config(self):
        """
        This function reads the config file and sets the class variables to the data in the config file. A wrapper for configparser's read function.

        Args:
            None
        Returns:
            None
        """
        # read the config file with configparser's read function
        self.read(CONFIG_FILE)

        # make a list of the versions in the config file
        self.versions_list = self.get_versions()

        # set the variables to the data in the config file
        self.selected_version: str = self.get("prog_data", "selected_version")
        self.server_folder: str = self.get(self.selected_version, "folder_path")

        self.auto_start_launcher: str = self.get("general", "auto_start_launcher")
        self.server_exe: str = os.path.join(self.server_folder, "Aki.Server.exe")
        self.launcher_exe: str = os.path.join(self.server_folder, "Aki.Launcher.exe")
        self.profile_id: str = self.get(self.selected_version, "profile_id")
        self.wait_time: int = self.getint(self.selected_version, "launcher_wait_time")

    def write_to_config(self, section: str, option: str, value: str):
        """
        Writes the config file with the new data. Does not handle updating data, just writing to config. A wrapper for configparser's write function.
        
        Args:
            section (str): The section to write to.
            option (str): The option to write to.
            value (str): The value to write.
        Returns:
            None
        """
        cprint(f'Writing config: "{section}" "{option}" "{value}"', "yellow")
        # write the config file with configparser's write function
        self.set(section, option, value)
        with open(CONFIG_FILE, "w+") as f:
            self.write(f)
        cprint("Writing config complete.", "green")

    def update_config(self):
        """
        Updates the config file with the new data that has been set.
        """
        with open(CONFIG_FILE, "w+") as f:
            self.write(f)
        cprint("Updating config complete.", "green")

    def add_new_version_data_to_config(self, section: str, folder_path: str, profile_id: str):
        """
        For adding new version sections and data to the config file. Also calls update_config to write the new data to the config file.
        
        Args:
            section (str): The section to add.
            folder_path (str): The folder path to add.
            profile_id (str): The profile id to add.
        Returns:
            None
        """
        self.add_section(section)
        self.set(section, "folder_path", folder_path)
        self.set(section, "profile_id", profile_id)
        self.set(section, "launcher_wait_time", "10")
        self.update_config()

    def get_versions(self):
        """
        Parses the section names in the config file, checks they start with "SPT-AKI", and returns a list of the versions.

        Args:
            None
        Returns:
            versions (list): A list of the versions.
        """
        versions = []
        for vers in self.sections():
            if vers.startswith("SPT-AKI"):
                versions.append(vers)
        return versions


class Utils:
    """
    This class handles the utility functions.\n
    """
    def __init__(self, master_window: "UI"):
        # Master window ref
        self.master_window = master_window

        # init AHK class
        self.master_ahk = AHK(directives=[NoTrayIcon])
        # init hotkey class
        self.hotkeys = Hotkeys(self.master_ahk, master_window.cfg)

        # get screen width and height for window size
        self.screen_width, self.screen_height = GetSystemMetrics(0), GetSystemMetrics(1)
        # save positions of the top left, and bottom left corners of the screen
        self.screen_top_left = (0, 0)
        self.screen_bottom_left = (0, self.screen_height)

        # subtract the height of the taskbar from the screen height so windows don't cover the taskbar
        taskbar = win32gui.FindWindow("Shell_traywnd", None)
        taskbar_height = win32gui.GetWindowRect(taskbar)[3] - win32gui.GetWindowRect(taskbar)[1]
        self.screen_height -= taskbar_height

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

    def open_spt_dir(self):
        """
        Opens the SPT folder in explorer.
        """
        self.selected_version = self.master_window.cfg.get("prog_data", "selected_version")
        self.server_folder = self.master_window.cfg.get(
            self.selected_version, "folder_path", fallback=os.getcwd()
        )
        os.startfile(self.server_folder)

    def hide_frames(self, frames: list):
        """
        Hides the given frames.
        
        Args:
            *args: The frames to hide.
        Returns:
            None
        """
        for frame in frames:
            frame.grid_forget()

    def hide_window(self, window_title):
        """
        Hides the window with the given title.

        Args:
            window_title (str): The title of the window to hide.
        Returns:
            None
        """
        win = win32gui.FindWindow(None, window_title)
        if win:
            win32gui.ShowWindow(win, 2)
        else:
            cprint(f"Window: {window_title} not found.", "red")

    def show_window(self, window_title):
        """
        Shows the window with the given title.
        
        Args:
            window_title (str): The title of the window to show.
        Returns:
            None
        """
        win = win32gui.FindWindow(None, window_title)
        if win:
            win32gui.ShowWindow(win, 1)
        else:
            cprint(f"Window: {window_title} not found.", "red")

    def wait_for_window(self, window_title: str, max_wait_time: int):
        """
        Function to wait for a window to open. Must be called in a thread for non-blocking.
        
        Args:
            window_title (str): The title of the window to wait for.
            max_wait_time (int): The max wait time in seconds.
        Returns:
            win (int): The window handle. 0 if the window was not found."""
        start_time = time.time()
        # while loop based on time monkaW
        # probably a better way to do this. some kind of safety check maybe?
        while time.time() - start_time < max_wait_time:
            win = win32gui.FindWindow(None, window_title)
            if win != 0:
                cprint(f"{window_title} started.", "green")
                return win
            time.sleep(0.1)

        self.handle_start_error()
        return 0
    
    def handle_start_error(self):
        """
        Handles the error when the server or launcher does not start within the timeout.
        
        Args:
            None
        Returns:
            None
        """
        self.master_window.tabs_frame.launcher_tab_frame.start_launcher_button.configure(text="Launcher did not start.", text_color="red")
        cprint("Launcher did not start within the timeout.", "red")

    def start_thread(self, func, *args, **kwargs):
        """
        Starts a thread for the given function.
        
        Args:
            func (function): The function to start the thread for.
            *args: The arguments for the function.
            **kwargs: The keyword arguments for the function.
        Returns:
            thread (threading.Thread): The thread that was started.
        """
        print(args)
        print(kwargs)
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    def start_server(self):
        """
        Starts the server. If the server is already running, brings the server window to the foreground.

        Args:
            None
        Returns:
            None
        """

        # try to find the server window if it's already open
        server_win = win32gui.FindWindow(None, self.master_window.cfg.selected_version)

        # if the server_win was not found, start the server
        if server_win == 0:
            cprint("Server window not found, starting new server...", "yellow")
            args = ["wt", "-d", self.master_window.cfg.server_folder, self.master_window.cfg.server_exe]
            subprocess.Popen(args, stdout=subprocess.PIPE)

            # while loop waiting for the server to open
            max_wait_time = 5
            start_time = time.time()
            while time.time() - start_time < max_wait_time:
                server_win = win32gui.FindWindow(None, self.master_window.cfg.selected_version)
                if server_win != 0: # server_win was found, break the loop
                    cprint("Server started.", "green")
                    # set the server_running variable to True
                    self.master_window.server_running = True
                    # TODO: make a config option for auto moving the server window
                    # move the server window to the left 1/3 of the screen
                    win32gui.MoveWindow(server_win, self.screen_top_left[0], self.screen_top_left[1], int(self.screen_width / 3), self.screen_height, True)
                    break
                time.sleep(0.1)

            if not server_win:
                cprint("Server did not start within the timeout.", "red")
                return

        else: # server window was found, bring it to the foreground
            cprint("Server window found, bringing to foreground...", "green")
            win32gui.ShowWindow(server_win, 1)
            win32gui.SetForegroundWindow(server_win)

        # we wont move the server window here because it's already open

        # this option is toggled in the settings tab to auto start the launcher after the server is started
        # I haven't been able to figure out how to read the server window to know when it says "Server started/ready."
        # So for now I am just making it a configurable wait time
        auto_start_launcher = self.master_window.cfg.getboolean("general", "auto_start_launcher")
        if auto_start_launcher:
            # read the wait time from the config
            wait_time = self.master_window.cfg.getint(self.master_window.cfg.selected_version, "launcher_wait_time")

            # start the countdown in the launcher tab on the start_launcher_button
            cd_thread = self.start_thread(self.master_window.tabs_frame.launcher_tab_frame.auto_start_countdown, wait_time)

            # wait for the countdown to finish
            cd_thread.join()

            # start the launcher
            self.start_launcher()

            # minimize the sptmm window
            self.hide_window("SPT Launcher")

    def start_launcher(self):
        """
        Starts the launcher. If the launcher is already running, brings the launcher window to the foreground.
        
        Args:
            None
        Returns:
            None
        """
        launcher_title = "Aki.Launcher"
        max_wait_time = 5

        # set the launcher_running variable to True
        self.master_window.launcher_running = True

        # set the button text back to "Start Launcher" because I'd rather do it here than in the launcher tab frame
        self.master_window.tabs_frame.launcher_tab_frame.start_launcher_button.configure(text="Start Launcher")

        launcher_win = win32gui.FindWindow(None, launcher_title)

        # if the launcher window was not found, start the launcher
        if launcher_win == 0:
            try:
                cprint("Launcher window not found, starting new launcher...", "yellow")
                # removes the quotes from the path and fixes slashes. Not really sure it's necessary but it works.
                norm_path = os.path.normpath(self.master_window.cfg.launcher_exe)
                # start the launcher in a thread
                self.start_thread(subprocess.run, norm_path, cwd=self.master_window.cfg.server_folder, check=True)
                # wait for the launcher window to open
                launcher_win = self.wait_for_window(launcher_title, max_wait_time)
            except subprocess.CalledProcessError:
                self.handle_start_error()
                return

        # launcher window was found, bring it to the foreground
        else:
            cprint("Launcher window found, bringing to foreground...", "green")
            win32gui.ShowWindow(launcher_win, 1)
            win32gui.SetForegroundWindow(launcher_win)
        
        # TODO: Move this to a function. Not sure I'll even use it tbh
        # move the launcher window to the center of the screen
        launcher_win_rect = win32gui.GetWindowRect(launcher_win)
        launcher_win_height = launcher_win_rect[3] - launcher_win_rect[1]
        launcher_win_width = launcher_win_rect[2] - launcher_win_rect[0]
        # print(launcher_win_rect)
        # print(launcher_win_height)
        # print(launcher_win_width)
        x = int(self.screen_width / 2 - launcher_win_width / 2)
        y = int(self.screen_height / 2 - launcher_win_height / 2)
        # TODO disabled. move the launcher window to the center of the screen
        # win32gui.MoveWindow(launcher_win, x, y, launcher_win_width, launcher_win_height, True)
        
        # # enable the launcher button
        self.master_window.tabs_frame.launcher_tab_frame.start_launcher_button.configure(state="normal")


class Hotkeys:
    """
    This class handles the hotkeys.\n
    Args:
        utils_ahk (AHK): The AHK class from Utils.
        master_cfg (ConfigParser): The master config.
    """
    def __init__(self, master_ahk: AHK, master_cfg: ConfigParser):
        print("Initializing Hotkeys")

        self.ahk = master_ahk
        self.master_cfg = master_cfg

        self.hotkeys = {
            "show_launcher": master_cfg.get("general", "show_ui_hotkey"),
            "hide_launcher": master_cfg.get("general", "hide_ui_hotkey"),
        }

    def __str__(self):
        return f"{self.hotkeys}"

    def start(self, ahk):
        self.show_window_hotkey(ahk, "SPT Launcher")
        self.hide_window_hotkey(ahk, "SPT Launcher")
        print("Hotkeys Started")
        # window.after(10000, self.refresh, window)

    def show_window_hotkey(self, ahk: AHK, window_title: str):
        script = f"WinActivate {window_title}"
        self.show_hotkey = Hotkey(ahk, self.hotkeys["show_launcher"], script)
        if not self.show_hotkey.running:
            self.show_hotkey.start()

    def hide_window_hotkey(self, ahk: AHK, window_title: str):
        script = f"WinMinimize {window_title}"
        self.hide_hotkey = Hotkey(ahk, self.hotkeys["hide_launcher"], script)
        if not self.hide_hotkey.running:
            self.hide_hotkey.start()
