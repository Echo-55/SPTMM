import os
import typing
import customtkinter as ctk
import shutil
import py7zr
import zipfile
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import re
import json
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from spt import UI


@dataclass
class Mod:
    name: str
    author: str
    version: str

class SPTMM:
    def __init__(self, master: "UI" = None):  # type: ignore
        self.master = master

        # path to server mods folder
        self.server_mods_folder = os.path.join(
            self.master.cfg.server_folder, "user/mods"
        )
        self.server_mods_list = os.listdir(self.server_mods_folder)

        # path to client mods folder
        self.client_mods_folder = os.path.join(
            self.master.cfg.server_folder, "Bepinex/plugins"
        )
        self.client_mods_list = self.get_client_mods()

        # cprint(f"Client mods: {self.client_mods_list}", "yellow")
        # cprint(f"Server mods: {self.server_mods_list}", "green")

    def get_client_mods(self):
        """
        Get a list of the mods in the client mods folder.
        Skips over the default mods that come with SPT-AKI.
        """
        # the default mods that come with SPT-AKI
        skip = [
            "aki-core.dll",
            "aki-custom.dll",
            "aki-debugging.dll",
            "aki-singleplayer.dll",
            "ConfigurationManager.dll",
        ]
        client_mods = []
        # iterate over the files in the client mods folder
        for mod in os.listdir(self.client_mods_folder):
            # skip over the default mods
            if mod in skip:
                continue
            # check if the mod is a .dll file
            if not mod.endswith(".dll"):
                # then it's a folder, look in the folder for a .dll file
                for file in os.listdir(os.path.join(self.client_mods_folder, mod)):
                    # if the file is a .dll file and not a default mod, add it to the list
                    if file.endswith(".dll") and file not in skip:
                        client_mods.append(file)
                        break
            # if the mod is a .dll file and not a default mod, add it to the list
            else:
                client_mods.append(mod)
        return client_mods

    def install_mod_window(self):
        """
        Create the window for installing mods.
        """

        self.mod_window = TkinterDnD.Tk()
        self.mod_window.title("Install Mods")
        self.mod_window.configure(bg="#282828")

        self.mod_window.w = 600  # width for the Tk root
        self.mod_window.h = 200  # height for the Tk root
        self.mod_window.minsize(self.mod_window.w, self.mod_window.h)

        self.mod_window.wm_attributes("-toolwindow", 1)

        # # hide the main frame
        # button_frames = [f for f in self.master.main_frame.children.values()]
        # self.master.utils.hide_frames(button_frames)
        # # hide the version frame
        # info_frames = [f for f in self.master.version_frame.children.values()]
        # self.master.utils.hide_frames(info_frames)

        # # resize the window to make room for the table
        # w = self.master.w + 150
        # h = self.master.h + 170
        # self.master.geometry("%dx%d" % (w, h))

        # # create the widgets
        # self.install_mod_label = ctk.CTkLabel(
        #     self.master.main_frame,
        #     text=f"Drag and Drop to install to {self.server_mods_folder}",
        #     font=("Fira Code", 10),
        # )
        # self.install_mod_label.grid(padx=5, pady=5, row=0, column=0)

        # self.go_back_button = ctk.CTkButton(
        #     self.master.version_frame,
        #     text="Go Back",
        #     font=("Fira Code", 12),
        #     command=lambda: self.restore_window(),
        # )
        # self.go_back_button.grid(padx=5, pady=5, row=0, column=0)

        # self.file_entry_box = ctk.CTkTextbox(self.master.main_frame, height=300, width=450)
        # self.file_entry_box.bind("<<Paste>>", lambda x: self.entry_box_paste(x))
        # self.file_entry_box.grid(padx=5, pady=5, row=1, column=0)

        # # TODO: Fix this. TKinter now has dnd support..I think?
        # self.file_entry_box.drop_target_register(DND_FILES)
        # self.file_entry_box.dnd_bind("<<Drop>>", self.entry_box_drop)

        # self.install_button = ctk.CTkButton(
        #     self.master.version_frame, text="Install", command=self.install_button_cb
        # )
        # self.install_button.grid(padx=5, pady=5, row=1, column=0)

    def install_button_cb(self):
        for f in self.file_entry_box.get(1.0, "end").splitlines():
            if zipfile.is_zipfile(f) or f.endswith(".zip ") or f.endswith(".rar "):
                print("Zip")
                with zipfile.ZipFile(f, "r") as zip:
                    info = zip.infolist()[0]
                    name = info.filename.split("/")[0]
                    print(f"Name: {name}")
                    if re.search(r"Bepinex", name, flags=re.IGNORECASE):
                        info = zip.infolist()[-1]
                        name = info.filename.split("plugins/")[1]
                    if re.search(r"user", name, flags=re.IGNORECASE):
                        info = zip.infolist()[-1]
                        name = info.filename.split("mods/")[1]

                    install_path = os.path.join(self.server_mods_folder, name)
                    if os.path.exists(install_path):
                        print(f"{install_path} already exists. Deleting old")
                        shutil.rmtree(install_path)

                    zip.extractall(install_path)

            if f.endswith(".7z "):
                print("7Zip")
                with py7zr.SevenZipFile(f, "r") as zip:
                    name = zip.getnames()[0]
                    print(f"Name: {name}")
                    install_path = os.path.join(self.server_mods_folder, name)
                    if os.path.exists(install_path):
                        print(f"{install_path} already exists. Deleting old")
                        shutil.rmtree(install_path)

                    zip.extractall(install_path)
                    # zip.extractall(self.test_folder)
                print(f"{name} successfully installed")

            # TODO URLS
            if f.startswith("http"):
                # sptmm.parse_urls(f)
                pass

    def entry_box_paste(self, data):
        text = self.file_entry_box.get(1.0, "end")
        if text.strip():
            self.file_entry_box.insert("insert", "\n")

    def entry_box_drop(self, event):
        if event.data:
            # print(f'Dropped data: {event.data}')
            if event.widget == self.file_entry_box:
                files = self.file_entry_box.tk.splitlist(event.data)
                for f in files:
                    if os.path.exists(f):
                        print(f"Dropped file: {f}")
                        self.file_entry_box.insert(tk.END, f"{os.path.abspath(f)} \n")
                    else:
                        print(f"{f} does not exist")
        else:
            print("Error: reported event.widget not known")
        return event.action

    def restore_window(self, tab="Launcher"):
        """
        Restore the window to its original state and optionally switch to a different tab.

        Args:
            tab (str, optional): The tab to switch to. Defaults to "Launcher".
        """
        # resize back to og size
        self.master.geometry("%dx%d" % (self.master.w, self.master.h))
        # remove all frames
        for f in self.master.children.values():
            f.grid_forget()
        # recreate the widgets
        self.master.create_widgets()
        # set the tab
        self.master.tabs_frame.set(tab)

    def enable_disable_button(self):
        # button = widgets.ToggleButton(
        #     value=False,
        #     description="Enable" if row["enabled"] else "Disable",
        #     button_style="success" if row["enabled"] else "",
        # )
        # return button
        self.toggle_button = ctk.CTkButton(
            self.master, image=self.master.utils.images["button"], width=10, height=10
        )
        return self.toggle_button

    def get_mods_info(self):
        table_data = []
        mods = []
        self.btn = self.enable_disable_button()

        # Iterate over the mod_folders list
        for folder in self.server_mods_list:
            # Get the path to the package.json file in the current folder
            package_json_path = os.path.join(folder, "package.json")

            # Check if the file exists
            if os.path.exists(package_json_path):
                # If the file exists, open it and read the contents
                with open(package_json_path, "r") as f:
                    package_json = json.load(f)

                # Extract the name, author, and version from the package.json file
                name = package_json.get("name")
                author = package_json.get("author")
                version = package_json.get("version")

                mod = Mod(name, author, version)
                mods.append(mod)

                # Add the data to the list
                table_data.append(
                    {
                        "enable_disable": self.btn,
                        "name": name,
                        "author": author,
                        "version": version,
                    }
                )

        sorted_table_data = sorted(table_data, key=lambda d: d["name"].lower())
        # Create a Pandas DataFrame from the data list
        df = pd.DataFrame(sorted_table_data)
        return df, mods

    # TODO Broken
    def build_mods_table(self):
        # resize the window to make room for the table
        w = self.master.w + 20
        h = self.master.h + 250
        self.master.geometry(f"{w}x{h}")

        self.style = ttk.Style()
        try:
            self.style.theme_create("mystyle", parent="clam")
        except Exception:
            self.style.theme_use("mystyle")

        self.style.theme_use("mystyle")
        self.style.configure("mystyle.Treeview", font=("Fira Code", 8))
        self.style.configure(
            "mystyle.Treeview", background="#333333", foreground="white"
        )
        self.style.configure(
            "mystyle.Treeview.Heading", background="#1F6AA5", foreground="white"
        )

        headers = ["enable_disable", "Name", "Author", "Version"]
        self.mods_table = ttk.Treeview(
            self.master.tabs_frame.mods_tab,
            columns=headers,
            selectmode="extended",
            style="mystyle.Treeview",
            show=["headings"],
        )

        self.mods_table.column("enable_disable", width=100, anchor="w")
        self.mods_table.column("Name", width=100, anchor="w")
        self.mods_table.column("Author", width=100, anchor="w")
        self.mods_table.column("Version", width=100, anchor="w")
        # Set column headings
        self.mods_table.heading("enable_disable")
        self.mods_table.heading("Name", text="Name")
        self.mods_table.heading("Author", text="Author")
        self.mods_table.heading("Version", text="Version")

        self.mods_table.grid(row=3, column=0)

        # Iterate through the rows in the dataframe
        df = self.get_mods_info()[0]
        # self.btn = self.enable_disable_button()
        for index, row in df.iterrows():
            self.mods_table.insert(
                "",
                "end",
                # text="",
                values=(
                    row["enable_disable"],
                    row["name"],
                    row["author"],
                    row["version"],
                    "Enabled",
                ),
            )

            # self.mods_table.set(iid, 0, button)

        self.master.tabs_frame.mods_tab_frame.open_mod_table_btn.configure(
            text="Close Mods Table", command=lambda: self.restore_window("Mods")
        )

        self.scrollbar = ttk.Scrollbar(
            self.master.tabs_frame.mods_tab, orient=tk.VERTICAL, command=self.mods_table.yview
        )
        self.mods_table.configure(yscroll=self.scrollbar.set)  # type: ignore
        self.scrollbar.grid(row=3, rowspan=2, column=1, sticky="ns")

    def toggle_mod_enabled(self, iid):
        # Get the current value of the "Enabled" column for the mod
        current_value = self.mods_table.set(iid, "Enabled")

        # Toggle the value of the "Enabled" column
        if current_value == "Enabled":
            new_value = "Disabled"
        else:
            new_value = "Enabled"
        self.mods_table.set(iid, "Enabled", new_value)

        # Update the underlying data structure (e.g. pandas dataframe)
        df = self.get_mods_info()[0]
        df.loc[int(iid), "enabled"] = new_value == "Enabled"

    # def toggle_mod_state(self, mod_name):
    #     """
    #     Toggle the state of a mod between enabled and disabled.
    #     """
    #     current_state = self.mod_states[mod_name]
    #     new_state = not current_state
    #     self.mod_states[mod_name] = new_state

    #     # Update the text of the button to reflect the new state
    #     button = self.mods_table.set(mod_name, "action")
    #     button.config(text="Disable" if new_state else "Enable")

    #     # Move the mod to the appropriate folder based on its state
    #     source_dir = self.cfg.mods_folder
    #     dest_dir = (
    #         os.path.join(self.cfg.server_folder, "user\\mods\\mods-disabled")
    #         if new_state
    #         else self.cfg.mods_folder
    #     )
    #     shutil.move(
    #         os.path.join(source_dir, mod_name), os.path.join(dest_dir, mod_name)
    #     )

    #     # Refresh the mods table to reflect the updated state
    #     self.mods_table.delete(*self.mods_table.get_children())
    #     self.build_mods_table()
