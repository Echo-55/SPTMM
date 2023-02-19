# vscode-fold=2
import os
import webbrowser
from configparser import ConfigParser
from dataclasses import dataclass

import requests
from ahk import AHK, Hotkey
from bs4 import BeautifulSoup

ahk = AHK()
cwd = os.getcwd()
CONFIG_FILE = os.path.join(cwd, "new_spt.ini")


class Config(ConfigParser):
    def __init__(self):
        super().__init__()
        self.read_config()

    def read_config(self):
        self.read(CONFIG_FILE)
        self.selected_version: str = self.get("prog_data", "selected_version")
        self.server_folder: str = self.get(self.selected_version, "folder_path")
        self.mods_list = os.listdir(os.path.join(self.server_folder, "user/mods"))
        self.mods_folders = [
            os.path.join(self.server_folder, "user/mods", each)
            for each in self.mods_list
        ]
        self.mods_folder: str = os.path.join(self.server_folder, "user\\mods")
        self.auto_start_launcher: str = self.get("general", "auto_start_launcher")
        self.server_exe: str = os.path.join(self.server_folder, "Aki.Server.exe")
        self.launcher_exe: str = os.path.join(self.server_folder, "Aki.Launcher.exe")
        self.profile_id: str = self.get(self.selected_version, "profile_id")
        self.wait_time: int = self.getint(self.selected_version, "launcher_wait_time")

    def write_config(self, section: str, option: str, value: str):
        # print(section)
        # print(option)
        # print(value)
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


class Utils:
    def __init__(self, cfg: ConfigParser):
        # self.cfg = cfg
        self.selected_version = cfg.get("prog_data", "selected_version")
        self.server_folder = cfg.get(self.selected_version, "folder_path", fallback=cwd)

    def open_spt_dir(self):
        ahk.run_script(f"Run {self.server_folder}")

    def hide_window(self, window_title):
        script = f"WinMinimize {window_title}"
        ahk.run_script(script)

    def show_window(self, window_title):
        script = f"WinActivate {window_title}"
        ahk.run_script(script)


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
