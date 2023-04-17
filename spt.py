# vscode-fold=2
import json
import os
import re
import shutil
import tkinter as tk
import zipfile
from tkinter import ttk

import customtkinter as ctk
import pandas as pd
import py7zr
from ahk import AHK
from ahk.directives import NoTrayIcon
from PIL import Image
from tkinterdnd2 import DND_FILES, TkinterDnD

# from data.frames import
from data.frames.options_frame import OptionsFrame
from data.frames.tabs_frame import (
    LauncherTabFrame,
    MasterTabsFrame,
    ModsTabFrame,
    SettingsTabFrame,
)
from data.frames.version_frame import VersionFrame
from data.spt_utils import Config, Mod, Utils

ahk = AHK(directives=[NoTrayIcon])


class UI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("SPT Launcher")
        self.configure(bg="#282828")

        self.center_window()

        self.cfg = Config()
        self.cfg.read_config()

        self.utils = Utils(self.cfg)

        self.settings_img = Image.open("data\\assets\\settings.png")
        self.enable_disable_btn_img = Image.open("data\\assets\\button.png")

        self.images = {
            "settings": tk.PhotoImage(file="data\\assets\\settings.png"),
            "add": tk.PhotoImage(file="data\\assets\\add.png"),
            "button": ctk.CTkImage(
                light_image=self.enable_disable_btn_img, size=(10, 10)
            ),
        }

        self.create_widgets()

        self.server_running = False
        self.launcher_running = False

    def center_window(self):
        self.w = 600  # width for the Tk root
        self.h = 200  # height for the Tk root
        self.minsize(self.w, self.h)

        # get screen width and height
        self.screen_width = self.winfo_screenwidth()  # width of the screen
        self.screen_height = self.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        self.x = (self.screen_width / 2) - (self.w / 2)
        self.y = (self.screen_height / 2) - (self.h / 2) - 200

        # set the dimensions of the screen
        # and where it is placed
        self.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x, self.y))
        # self.geometry(f'{w}x{h} + {x} + {y}')
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

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

    # events

    def show_frame(self, frames=[]):
        pass

    def hide_frame(self, frames=[]):
        for f in frames:
            f.grid_forget()

    def install_mod_window(self):
        button_frames = [f for f in self.options_frame.children.values()]
        self.hide_frame(frames=button_frames)
        info_frames = [f for f in self.version_frame.children.values()]
        self.hide_frame(frames=info_frames)
        w = self.w + 150
        h = self.h + 170
        self.geometry("%dx%d" % (w, h))

        self.install_mod_label = ctk.CTkLabel(
            self.options_frame,
            text=f"Drag and Drop to install to {self.cfg.mods_folder}",
            font=("Fira Code", 10),
        )
        self.install_mod_label.grid(padx=5, pady=5, row=0, column=0)

        self.go_back_button = ctk.CTkButton(
            self.version_frame,
            text="Go Back",
            font=("Fira Code", 12),
            command=lambda: self.restore_window(),
        )
        self.go_back_button.grid(padx=5, pady=5, row=0, column=0)

        self.file_entry_box = ctk.CTkTextbox(self.options_frame, height=300, width=450)
        self.file_entry_box.bind("<<Paste>>", lambda x: self.entry_box_paste(x))
        self.file_entry_box.grid(padx=5, pady=5, row=1, column=0)

        self.file_entry_box.drop_target_register(DND_FILES)  # type: ignore
        self.file_entry_box.dnd_bind("<<Drop>>", self.entry_box_drop)  # type: ignore

        self.install_button = ctk.CTkButton(
            self.version_frame, text="Install", command=self.install_button_cb
        )
        self.install_button.grid(padx=5, pady=5, row=1, column=0)

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

                    install_path = os.path.join(self.cfg.mods_folder, name)
                    if os.path.exists(install_path):
                        print(f"{install_path} already exists. Deleting old")
                        shutil.rmtree(install_path)

                    zip.extractall(install_path)

            if f.endswith(".7z "):
                print("7Zip")
                with py7zr.SevenZipFile(f, "r") as zip:
                    name = zip.getnames()[0]
                    print(f"Name: {name}")
                    install_path = os.path.join(self.cfg.mods_folder, name)
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
        self.geometry("%dx%d" % (self.w, self.h))
        for f in self.children.values():
            f.grid_forget()
        self.create_widgets()
        self.tab_view.set(tab)

    def enable_disable_button(self):
        # button = widgets.ToggleButton(
        #     value=False,
        #     description="Enable" if row["enabled"] else "Disable",
        #     button_style="success" if row["enabled"] else "",
        # )
        # return button
        self.toggle_button = ctk.CTkButton(
            self, image=self.images["button"], width=10, height=10
        )
        return self.toggle_button

    def get_mods_info(self):
        table_data = []
        mods = []
        self.btn = self.enable_disable_button()

        # Iterate over the mod_folders list
        for folder in self.cfg.mod_folders_list:
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
        w = self.w + 20
        h = self.h + 250
        self.geometry(f"{w}x{h}")

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
            self.mods_tab,
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

        self.open_mod_table_btn.configure(
            text="Close Mods Table", command=lambda: self.restore_window("Mods")
        )

        self.scrollbar = ttk.Scrollbar(
            self.mods_tab, orient=tk.VERTICAL, command=self.mods_table.yview
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

    def toggle_mod_state(self, mod_name):
        """
        Toggle the state of a mod between enabled and disabled.
        """
        current_state = self.mod_states[mod_name]
        new_state = not current_state
        self.mod_states[mod_name] = new_state

        # Update the text of the button to reflect the new state
        button = self.mods_table.set(mod_name, "action")
        button.config(text="Disable" if new_state else "Enable")

        # Move the mod to the appropriate folder based on its state
        source_dir = self.cfg.mods_folder
        dest_dir = (
            os.path.join(self.cfg.server_folder, "user\\mods\\mods-disabled")
            if new_state
            else self.cfg.mods_folder
        )
        shutil.move(
            os.path.join(source_dir, mod_name), os.path.join(dest_dir, mod_name)
        )

        # Refresh the mods table to reflect the updated state
        self.mods_table.delete(*self.mods_table.get_children())
        self.build_mods_table()


def main():
    main = UI()

    # mods = main.get_mods_info()[1]
    # sptmm = ModManager(cfg, mods)

    main.after(1000, main.utils.hotkeys.start, main)
    main.mainloop()


if __name__ == "__main__":
    main()
