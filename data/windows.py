import os
import tkinter as tk
import typing

import customtkinter as ctk

from data.spt_utils import Config

if typing.TYPE_CHECKING:
    from spt import UI


class ErrorWindow(ctk.CTkToplevel):
    def __init__(self, parent: "UI", cfg: Config):
        super().__init__(parent)
        # self.parent = parent
        # self.cfg = cfg


class NewVersionWindow(ctk.CTkToplevel):
    def __init__(self, parent: "UI", cfg: Config):
        super().__init__(parent)
        self.parent: "UI" = parent
        self.cfg = cfg

        self.title("Add New Version")
        self.geometry("%dx%d+%d+%d" % (269, 191, parent.x + 20, parent.y - 20))

        self.new_version_frame = ctk.CTkFrame(self)
        self.new_version_frame.grid(row=0, column=0, sticky="nsew")

        self.version_entry_label = ctk.CTkLabel(
            self.new_version_frame, text="Version: SPT-AKI", font=("Fire Code", 12)
        )
        self.version_entry_label.grid(padx=5, pady=5, row=0, column=0)
        self.version_entry_var = tk.StringVar(self, value="x.x.x")
        self.version_entry = ctk.CTkEntry(
            self.new_version_frame,
            placeholder_text=self.version_entry_var.get(),
            textvariable=self.version_entry_var,
            font=("Fire Code", 12),
        )
        self.version_entry.grid(padx=5, pady=5, row=0, column=1)

        self.spt_folder_label = ctk.CTkLabel(
            self.new_version_frame, text="SPT Folder:", font=("Fire Code", 12)
        )
        self.spt_folder_label.grid(padx=5, pady=5, row=1, column=0)
        self.spt_folder_entry_var = tk.StringVar(self, value="path/to/SPTFolder")
        self.spt_folder_entry = ctk.CTkEntry(
            self.new_version_frame,
            placeholder_text=self.spt_folder_entry_var.get(),
            textvariable=self.spt_folder_entry_var,
            font=("Fire Code", 12),
        )
        self.spt_folder_entry.grid(padx=5, pady=5, row=1, column=1)

        self.profile_id_label = ctk.CTkLabel(
            self.new_version_frame, text="Profile ID: ", font=("Fire Code", 12)
        )
        self.profile_id_label.grid(padx=5, pady=5, row=2, column=0)
        self.profile_id_entry_var = tk.StringVar(
            self.new_version_frame, value="5779936a22cb6908c7eb84f2.json"
        )
        self.profile_id_entry = ctk.CTkEntry(
            self.new_version_frame,
            placeholder_text=self.profile_id_entry_var.get(),
            textvariable=self.profile_id_entry_var,
            font=("Fire Code", 12),
        )
        self.profile_id_entry.grid(padx=5, pady=5, row=2, column=1)

        self.add_version_button = ctk.CTkButton(
            self.new_version_frame,
            text="Done",
            command=self.add_new_version_data,
            font=("Fire Code", 12),
        )
        self.add_version_button.grid(padx=5, pady=5, row=3, columnspan=2)

    def add_new_version_data(self):
        print("Adding new version data")

        # validate the data
        if not os.path.exists(
            os.path.join(self.spt_folder_entry_var.get(), "user\\mods")
        ):
            self.spt_folder_label.configure(text_color="red")
            return
        self.spt_folder_label.configure(text_color="white")

        if not os.path.exists(
            os.path.join(
                self.spt_folder_entry_var.get(),
                "user\\profiles",
                self.profile_id_entry_var.get(),
            )
        ):
            self.profile_id_label.configure(text_color="red")
            return
        self.profile_id_label.configure(text_color="white")

        self.cfg.selected_version = f"SPT-AKI {self.version_entry_var.get()}"
        self.cfg.server_folder = self.spt_folder_entry_var.get()
        self.cfg.profile_id = self.profile_id_entry_var.get()

        # get the list of versions from the config file
        self.parent.version_frame.versions_list.insert(1, self.cfg.selected_version)
        self.parent.version_frame.version_select_menu.configure(
            values=self.cfg.versions_list
        )
        self.parent.version_frame.version_select_menu.set(self.cfg.selected_version)
        if self.cfg.selected_version not in self.cfg.versions_list:
            self.cfg.write_config(
                "prog_data", "selected_version", self.cfg.selected_version
            )
            self.cfg.add_new_version_data(
                self.cfg.selected_version, self.cfg.server_folder, self.cfg.profile_id
            )
        self.parent.update_char_info()
        self.destroy()
        print("Done adding new version data")
