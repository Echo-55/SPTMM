import os
import tkinter as tk
import typing

import customtkinter as ctk

from data.spt_utils import Config

if typing.TYPE_CHECKING:
    from spt import UI


class ErrorWindow(ctk.CTkToplevel):
    def __init__(self, master_window: "UI", cfg: Config):
        super().__init__(master_window)
        self.master_window = master_window
        self.cfg = cfg


class NewVersionWindow(ctk.CTkToplevel):
    def __init__(self, master_window: "UI", cfg: Config):

        # make a new top level window with the parent being the master window
        super().__init__(master_window)
        
        # set ref to the master window and config
        self.master_window: "UI" = master_window
        self.cfg = cfg

        # set the title, size, and position of the window
        self.title("Add New Version")
        self.geometry("%dx%d+%d+%d" % (269, 191, self.master_window.x + 20, self.master_window.y - 20))

        # make the frame
        self.new_version_frame = ctk.CTkFrame(self)
        self.new_version_frame.grid(row=0, column=0, sticky="nsew")

        # make the widgets within the frame
        # new version entry label
        self.version_entry_label = ctk.CTkLabel(
            self.new_version_frame, text="Version: SPT-AKI", font=("Fire Code", 12)
        )
        self.version_entry_label.grid(padx=5, pady=5, row=0, column=0)
        # string variable to hold the version entry | this is necessary for ctk and I think normal tkinter as well
        self.version_entry_var = tk.StringVar(self, value="x.x.x")
        # make the version entry widget
        self.version_entry = ctk.CTkEntry(
            self.new_version_frame,
            placeholder_text=self.version_entry_var.get(),
            textvariable=self.version_entry_var,
            font=("Fire Code", 12),
        )
        self.version_entry.grid(padx=5, pady=5, row=0, column=1)

        # make the spt folder entry label
        self.spt_folder_label = ctk.CTkLabel(
            self.new_version_frame, text="SPT Folder:", font=("Fire Code", 12)
        )
        self.spt_folder_label.grid(padx=5, pady=5, row=1, column=0)
        # string variable to hold the spt folder entry
        self.spt_folder_entry_var = tk.StringVar(self, value="path/to/SPTFolder")
        # make the spt folder entry widget
        self.spt_folder_entry = ctk.CTkEntry(
            self.new_version_frame,
            placeholder_text=self.spt_folder_entry_var.get(),
            textvariable=self.spt_folder_entry_var,
            font=("Fire Code", 12),
        )
        self.spt_folder_entry.grid(padx=5, pady=5, row=1, column=1)

        # make the profile id entry label
        self.profile_id_label = ctk.CTkLabel(
            self.new_version_frame, text="Profile ID: ", font=("Fire Code", 12)
        )
        self.profile_id_label.grid(padx=5, pady=5, row=2, column=0)
        # string variable to hold the profile id entry
        self.profile_id_entry_var = tk.StringVar(
            self.new_version_frame, value="5779936a22cb6908c7eb84f2.json"
        )
        # make the profile id entry widget
        self.profile_id_entry = ctk.CTkEntry(
            self.new_version_frame,
            placeholder_text=self.profile_id_entry_var.get(),
            textvariable=self.profile_id_entry_var,
            font=("Fire Code", 12),
        )
        self.profile_id_entry.grid(padx=5, pady=5, row=2, column=1)

        # make the add version button
        self.add_version_button = ctk.CTkButton(
            self.new_version_frame,
            text="Done",
            command=self.add_new_version_data,
            font=("Fire Code", 12),
        )
        self.add_version_button.grid(padx=5, pady=5, row=3, columnspan=2)

    def add_new_version_data(self):
        """
        This function adds the new version data to the config file and the versions list.

        Args:
            None
        """
        print("Adding new version data")

        # validate the data
        # check if the version is already in the config file
        if self.version_entry_var.get() in self.cfg.versions_list:
            self.version_entry_label.configure(text_color="red")
            return

        # check if the spt folder exists
        if not os.path.exists(self.spt_folder_entry_var.get()):
            self.spt_folder_label.configure(text_color="red")
            return
        
        # check if the profile id exists
        profile_json = os.path.join(
            self.spt_folder_entry_var.get(),
            "user\\profiles\\",
            self.profile_id_entry_var.get(),
        )
        if not os.path.exists(profile_json):
            self.profile_id_label.configure(text_color="red")
            return
        
        # if the data is valid, set the text color back to white
        self.profile_id_label.configure(text_color="white")

        # set the config data to the new data
        self.cfg.selected_version = f"SPT-AKI {self.version_entry_var.get()}"
        self.cfg.server_folder = self.spt_folder_entry_var.get()
        self.cfg.profile_id = self.profile_id_entry_var.get()

        # write the new data to the config file
        self.cfg.add_new_version_data_to_config(
            self.cfg.selected_version, self.cfg.server_folder, self.cfg.profile_id
        )


        # insert the new version into the versions list
        self.master_window.version_frame.versions_list.insert(1, self.cfg.selected_version)
        # set the version select menu values to the new versions list
        self.master_window.version_frame.version_select_menu.configure(
            values=self.cfg.versions_list
        )
        # set the selected version to the new version
        self.master_window.version_frame.version_select_menu.set(self.cfg.selected_version)

        
        
        # update the character info
        self.master_window.update_char_info()
        # destroy this window
        self.destroy()
        print("Done adding new version data")
