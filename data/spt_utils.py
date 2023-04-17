# vscode-fold=2
import os
import subprocess
import threading
import typing
import webbrowser
from configparser import ConfigParser
from dataclasses import dataclass

import requests
from ahk import AHK, Hotkey
from bs4 import BeautifulSoup
from win32api import GetSystemMetrics

# from data.frames.tabs_frame

if typing.TYPE_CHECKING:
    from spt import UI

ahk = AHK()
CONFIG_FILE = os.path.join(os.getcwd(), "myconfig.ini")


class Config(ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__()
        print("Reading config file")
        self.read(CONFIG_FILE)
        self.versions_list = self.get_versions()
        self.read_config()
        print(self.versions_list)

    def read_config(self):
        self.selected_version: str = self.get("prog_data", "selected_version")
        self.server_folder: str = self.get(self.selected_version, "folder_path")
        self.mods_folder: str = os.path.join(self.server_folder, "user/mods")
        if os.path.exists(self.mods_folder):
            self.mods_list = os.listdir(self.mods_folder)
            self.mod_folders_list = [
                os.path.join(self.mods_folder, each) for each in self.mods_list
            ]
        else:
            return print("Mods folder not found")
        self.auto_start_launcher: str = self.get("general", "auto_start_launcher")
        self.server_exe: str = os.path.join(self.server_folder, "Aki.Server.exe")
        self.launcher_exe: str = os.path.join(self.server_folder, "Aki.Launcher.exe")
        self.profile_id: str = self.get(self.selected_version, "profile_id")
        self.wait_time: int = self.getint(self.selected_version, "launcher_wait_time")

    def write_config(self, section: str, option: str, value: str):
        self.set(section, option, value)
        with open(CONFIG_FILE, "w+") as f:
            self.write(f)

    def add_new_version_data(self, section: str, folder_path: str, profile_id: str):
        self.add_section(section)
        self.set(section, "folder_path", folder_path)
        self.set(section, "profile_id", profile_id)
        self.set(section, "launcher_wait_time", "10")
        with open(CONFIG_FILE, "w+") as f:
            self.write(f)

    def get_versions(self):
        versions = []
        for vers in self.sections():
            if vers.startswith("SPT-AKI"):
                versions.append(vers)
        return versions


class Utils:
    def __init__(self, cfg: ConfigParser):
        self.cfg = cfg
        self.selected_version = cfg.get("prog_data", "selected_version")
        self.server_folder = cfg.get(
            self.selected_version, "folder_path", fallback=os.getcwd()
        )
        self.hotkeys = Hotkeys(cfg)

    def open_spt_dir(self):
        ahk.run_script(f"Run {self.server_folder}")

    def hide_window(self, window_title):
        script = f"WinMinimize {window_title}"
        ahk.run_script(script)

    def show_window(self, window_title):
        script = f"WinActivate {window_title}"
        ahk.run_script(script)

    # callbacks
    def start_thread(self, func):
        thread = threading.Thread(target=func)
        thread.start()

    def start_server(self, master: "UI"):
        # start server
        width, height = GetSystemMetrics(0), GetSystemMetrics(1)
        try:
            server_win = ahk.win_wait(title=master.cfg.selected_version, timeout=5)
        except TimeoutError:
            server_win = ahk.win_wait(title=master.cfg.versions_list[0], timeout=5)
        if server_win:
            server_win.move(x="-5", y="0", width=width / 2, height=height)
        else:
            args = ["wt", "-d", master.cfg.server_folder, master.cfg.server_exe]
            subprocess.Popen(args, stdout=subprocess.PIPE)

        auto_start = self.cfg.getboolean("general", "auto_start_launcher")
        if auto_start:
            try:
                server_win = ahk.win_wait(title=master.cfg.selected_version, timeout=5)
            except TimeoutError:
                server_win = ahk.win_wait(title=master.cfg.versions_list[0], timeout=5)
            server_win.move(x="-5", y="0", width=width / 2, height=height)
            # master.auto_start_countdown(master.cfg.wait_time)
            master.launcher_tab_frame.auto_start_countdown(master.cfg.wait_time)
            self.start_thread(self.start_launcher)
        master.launcher_tab_frame.start_launcher_button.configure(text="Start Launcher")
        self.server_running = True
        # utils.hide_window("SPT Launcher")

    def start_launcher(self, master: "UI"):
        win = ahk.win_get(title="Aki.Launcher")
        if win:
            win.activate()
        else:
            subprocess.Popen(
                rf"{master.cfg.launcher_exe}", cwd=master.cfg.server_folder
            )
        self.launcher_running = True


class Hotkeys:
    def __init__(self, cfg: ConfigParser):
        print("Initializing Hotkeys")
        self.hotkeys = {
            "show_launcher": cfg.get("general", "show_ui_hotkey"),
            "hide_launcher": cfg.get("general", "hide_ui_hotkey"),
        }

    def __str__(self):
        return f"{self.hotkeys}"

    def start(self, window):
        self.show_window_hotkey("SPT Launcher")
        self.hide_window_hotkey("SPT Launcher")
        print("Hotkeys Started")
        # window.after(10000, self.refresh, window)

    def show_window_hotkey(self, window_title: str):
        script = f"WinActivate {window_title}"
        self.show_hotkey = Hotkey(ahk, self.hotkeys["show_launcher"], script)
        if not self.show_hotkey.running:
            self.show_hotkey.start()

    def hide_window_hotkey(self, window_title: str):
        script = f"WinMinimize {window_title}"
        self.hide_hotkey = Hotkey(ahk, self.hotkeys["hide_launcher"], script)
        if not self.hide_hotkey.running:
            self.hide_hotkey.start()


@dataclass
class Mod:
    name: str
    author: str
    version: str


class ModManager:
    def __init__(self, cfg: Config, mods: list[Mod]):
        cfg.read_config()
        self.enabled_mods: list[Mod] = mods

    def parse_urls(self, url):
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, features="html.parser")
        dl_button = soup.find_all(attrs={"itemprop": "downloadUrl"})
        dl_link = dl_button[0].get("href")
        self.open_browser(dl_link)

    def open_browser(self, url):
        webbrowser.open_new_tab(url)
