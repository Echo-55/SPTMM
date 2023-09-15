# vscode-fold=2
import json
import os
import tkinter as tk
import typing

import customtkinter as ctk
from termcolor import cprint

from data.exceptions import MissingProfileJson
from data.windows import NewVersionWindow

if typing.TYPE_CHECKING:
    from spt import UI


class VersionFrame(ctk.CTkFrame):
    """
    Frame that shows selected version and character info.

    Args:
        master (UI): The master window.
    """

    width = 370
    height = 50

    def __init__(self, master_window: "UI", **kwargs):
        super().__init__(
            master_window,
            width=self.width,
            height=self.height,
        )
        self.master_window: UI = master_window

        self.versions_list = self.master_window.cfg.versions_list
        self.versions_list.append("Add New Version...")

        self.version_select_menu = ctk.CTkOptionMenu(
            self,
            values=self.versions_list,
            command=self.select_version_cb,
            font=("Fira Code", 12),
        )
        self.version_select_menu.grid(row=0, column=0, sticky="nsew", columnspan=2)
        self.version_select_menu.set(self.master_window.cfg.selected_version)

        self.char_info = self.get_char_info()

        self.display_char_name()
        self.display_char_level()
        self.display_char_edition()

    def select_version_cb(self, value: str):
        if value == "Add New Version...":
            NewVersionWindow(self.master_window, self.master_window.cfg)
        else:
            self.master_window.cfg.selected_version = value
            self.version_select_menu.set(value)
            self.master_window.cfg.write_to_config("prog_data", "selected_version", value)
            self.update_char_info()

    def get_char_info(self):
        cprint("Reading profile.json...", "yellow")
        # read the config file
        self.master_window.cfg.read_config()
        profile_json = os.path.join(
            self.master_window.cfg.server_folder,
            "user\\profiles\\",
            self.master_window.cfg.profile_id + ".json",
        )
        try:
            with open(profile_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            cprint("Profile.json read successfully.", "green")
        except FileNotFoundError:
            cprint("Profile.json not found.", "red")
            raise MissingProfileJson(
                profile_json=profile_json,
                selected_version=self.master_window.cfg.selected_version,
            )
        name = data["characters"]["pmc"]["Info"]["Nickname"]
        level = data["characters"]["pmc"]["Info"]["Level"]
        edition = data["info"]["edition"]
        char_info = {"name": name, "level": level, "edition": edition}
        return char_info

    def update_char_info(self):
        print(self.master_window.cfg.selected_version)
        print("Updating character info...")
        data = self.get_char_info()
        self.char_name.set(data["name"])
        self.char_level.set(data["level"])
        self.char_edition.set(data["edition"])

    def display_char_name(self):
        self.character_name_label = ctk.CTkLabel(
            self, anchor="w", text="Name: ", font=("Fira Code", 10)
        )
        self.character_name_label.grid(padx=1, pady=1, column=0, row=1)
        self.char_name = tk.StringVar(self, value=self.char_info["name"])
        self.character_name = ctk.CTkLabel(
            self, textvariable=self.char_name, font=("Fira Code", 12)
        )
        self.character_name.grid(padx=1, pady=1, column=1, row=1)

    def display_char_level(self):
        self.character_level_label = ctk.CTkLabel(
            self, anchor="w", text="Level: ", font=("Fira Code", 10)
        )
        self.character_level_label.grid(padx=1, pady=1, column=0, row=2)
        self.char_level = tk.StringVar(self, value=self.char_info["level"])
        self.character_level = ctk.CTkLabel(
            self, textvariable=self.char_level, font=("Fira Code", 12)
        )
        self.character_level.grid(padx=1, pady=1, column=1, row=2)

    def display_char_edition(self):
        self.character_edition_label = ctk.CTkLabel(
            self, anchor="w", text="Edition: ", font=("Fira Code", 10)
        )
        self.character_edition_label.grid(padx=1, pady=1, column=0, row=3)
        self.char_edition = tk.StringVar(self, value=self.char_info["edition"])
        self.character_edition = ctk.CTkLabel(
            self, textvariable=self.char_edition, font=("Fira Code", 12)
        )
        self.character_edition.grid(padx=1, pady=1, column=1, row=3)
