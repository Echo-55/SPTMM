# vscode-fold=2
import json
import os
import re
import shutil
import subprocess
import threading
import tkinter as tk
import webbrowser
import zipfile
from time import sleep
from tkinter import ttk

import customtkinter as ctk
import pandas as pd
import py7zr
from ahk import AHK
from ahk.directives import NoTrayIcon
from PIL import Image
from tkinterdnd2 import DND_FILES, TkinterDnD
from win32api import GetSystemMetrics

from spt_utils import Config, Mod, Utils

ahk = AHK(directives=[NoTrayIcon])


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

        # set the dimensions of the screen
        # and where it is placed
        self.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x, self.y))
        # self.geometry(f'{w}x{h} + {x} + {y}')
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.cfg = Config()
        self.cfg.read_config()
        self.auto_start_launcher = self.cfg.getboolean("general", "auto_start_launcher")

        self.utils = Utils(self.cfg)

        self.settings_img = Image.open("data\\settings.png")
        self.enable_disable_btn_img = Image.open("data\\button.png")

        self.images = {
            "settings": tk.PhotoImage(file="data\\settings.png"),
            "add": tk.PhotoImage(file="data\\add.png"),
            # "button": tk.PhotoImage(file="data\\button.png"),
            "button": ctk.CTkImage(
                light_image=self.enable_disable_btn_img, size=(10, 10)
            ),
        }

        self.cfg.read_config()
        self.auto_start_launcher = self.cfg.getboolean("general", "auto_start_launcher")

        self.create_widgets()

        self.server_running = False
        self.launcher_running = False

    def create_widgets(self):
        # @ Options frame
        self.options_frame = ctk.CTkFrame(self, height=50, width=370)
        # Using pack makes the frames dynamcially resize
        # self.options_frame.pack(padx=10, pady=10, side='left', fill='both', expand=True)
        self.options_frame.grid(padx=5, pady=5, column=0, sticky=tk.NSEW)

        # @ Tabview
        self.tab_view = ctk.CTkTabview(self.options_frame, height=50, width=350)
        self.tab_view.grid(padx=5, pady=5, column=0, row=0)

        self.launcher_tab = self.tab_view.add("Launcher")

        self.mods_tab = self.tab_view.add("Mods")
        self.mods_tab.grid_columnconfigure(0, weight=2)

        self.settings_tab = self.tab_view.add("Settings")
        self.settings_tab.grid_columnconfigure(0, weight=2)

        # @ Launcher tab
        self.launcher_tab_frame = ctk.CTkFrame(self.launcher_tab)
        # self.start_buttons_frame.pack(padx=10, pady=10, side='right', fill='both', expand=True)
        self.launcher_tab_frame.grid(padx=5, pady=5, column=0, row=2)
        self.start_server_button = ctk.CTkButton(
            self.launcher_tab_frame,
            width=170,
            height=28,
            text="Start Server",
            command=lambda: self.start_thread(self.start_server),
            font=("Fira Code", 12),
            hover_color="#487014",
            border_width=2,
            border_color="#487014",
        )
        self.start_server_button.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.start_launcher_button = ctk.CTkButton(
            self.launcher_tab_frame,
            width=170,
            height=28,
            text="Start Launcher",
            command=lambda: self.start_thread(self.start_launcher),
            font=("Fira Code", 12),
            hover_color="#487014",
            border_width=2,
            border_color="#487014",
        )
        self.start_launcher_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        if self.auto_start_launcher:
            self.auto_start_var = tk.StringVar(
                self, value="1", name="self.auto_start_var"
            )
        else:
            self.auto_start_var = tk.StringVar(
                self, value="0", name="self.auto_start_var"
            )

        self.auto_start_launcher_checkbox = ctk.CTkCheckBox(
            self.launcher_tab,
            text="Auto Start Launcher",
            command=self.autostart_checkbox_event,
            variable=self.auto_start_var,
            onvalue=1,
            offvalue=0,
            font=("Fira Code", 10),
            width=15,
            height=15,
            checkbox_width=15,
            checkbox_height=15,
        )
        self.auto_start_launcher_checkbox.grid(padx=5, pady=5, row=3, column=0)

        if self.auto_start_launcher:
            self.auto_start_launcher_checkbox.select(True)

        # @ Mods tab
        # @ Open dir and mod table inside options_frame
        self.mods_tab_frame = ctk.CTkFrame(self.mods_tab, height=50, width=370)
        self.mods_tab_frame.grid(padx=5, pady=5, row=0, column=0, sticky=tk.NS)

        # open spt directory button
        self.open_dir_button = ctk.CTkButton(
            self.mods_tab_frame,
            text="Open SPT Folder",
            command=self.utils.open_spt_dir,
            font=("Fira Code", 12),
        )
        self.open_dir_button.grid(padx=5, pady=5, row=0, column=2)

        # open mod table
        self.open_mod_table_btn = ctk.CTkButton(
            self.mods_tab_frame,
            text="View Mods Table",
            command=self.build_mods_table,
            font=("Fira Code", 12),
        )
        self.open_mod_table_btn.grid(padx=5, pady=5, row=1, column=2)

        # install mod button
        self.install_mod_button = ctk.CTkButton(
            self.mods_tab_frame,
            text="Install Mods",
            # command=self.install_mod_window,
            command=self.install_mod_window,
            font=("Fira Code", 12),
        )
        self.install_mod_button.grid(padx=5, pady=5, row=0, column=3)

        self.open_hub_button = ctk.CTkButton(
            self.mods_tab_frame,
            text="Open SPT Hub",
            command=lambda: webbrowser.open_new_tab("https://hub.sp-tarkov.com/files/"),  # type: ignore
            font=("Fira Code", 12),
        )
        self.open_hub_button.grid(padx=5, pady=5, row=1, column=3)

        # @ Settings tab
        self.settings_tab_frame = ctk.CTkFrame(self.settings_tab, height=50, width=370)
        self.settings_tab_frame.grid(padx=5, pady=5, row=0, column=0, sticky=tk.NS)

        self.auto_start_label = ctk.CTkLabel(
            self.settings_tab_frame, text="Launcher auto-start wait time: "
        )
        self.auto_start_label.grid(padx=5, pady=5, column=0, row=0)

        self.wait_time = tk.StringVar(
            self, value=self.cfg.get(self.cfg.selected_version, "launcher_wait_time")
        )
        self.auto_start_entry = ctk.CTkEntry(
            self.settings_tab_frame,
            width=30,
            height=20,
            textvariable=self.wait_time,
        )
        self.auto_start_entry.grid(padx=3, pady=3, column=1, row=0)

        self.save_button = ctk.CTkButton(
            self.settings_tab_frame,
            text="Save",
            command=lambda: self.save_button_cb(wait_time=self.wait_time.get()),
        )
        self.save_button.grid(padx=5, pady=5, columnspan=2, row=1)

        # @ Version Frame
        self.version_frame = ctk.CTkFrame(self, height=30, width=500)
        # Using pack makes the frames dynamcially resize
        # self.version_frame.pack(padx=10, pady=10, side='right', fill='both', expand=True)
        self.version_frame.grid(padx=5, pady=5, column=1, row=0, sticky=tk.NSEW)
        versions = self.get_versions()
        versions.append("Add New Version")
        self.version_select = ctk.CTkOptionMenu(
            self.version_frame,
            values=versions,
            command=self.select_version,
            font=("Fira Code", 12),
        )
        self.version_select.grid(padx=5, pady=5, columnspan=2, row=0)
        self.version_select.set(self.cfg.selected_version)

        # @ Character Info inside Version Frame
        # name
        self.character_name_label = ctk.CTkLabel(
            self.version_frame, anchor="w", text="Name: ", font=("Fira Code", 10)
        )
        self.character_name_label.grid(padx=1, pady=1, column=0, row=1)
        self.char_name = tk.StringVar(
            self.version_frame, value=self.get_char_info()["name"]
        )
        self.character_name = ctk.CTkLabel(
            self.version_frame, textvariable=self.char_name, font=("Fira Code", 12)
        )
        self.character_name.grid(padx=1, pady=1, column=1, row=1)

        # level
        self.character_level_label = ctk.CTkLabel(
            self.version_frame, anchor="w", text="Level: ", font=("Fira Code", 10)
        )
        self.character_level_label.grid(padx=1, pady=1, column=0, row=2)
        self.char_level = tk.StringVar(
            self.version_frame, value=self.get_char_info()["level"]
        )
        self.character_level = ctk.CTkLabel(
            self.version_frame, textvariable=self.char_level, font=("Fira Code", 12)
        )
        self.character_level.grid(padx=1, pady=1, column=1, row=2)

        # edition
        self.character_edition_label = ctk.CTkLabel(
            self.version_frame, anchor="w", text="Edition: ", font=("Fira Code", 10)
        )
        self.character_edition_label.grid(padx=1, pady=1, column=0, row=3)
        self.char_edition = tk.StringVar(
            self.version_frame, value=self.get_char_info()["edition"]
        )
        self.character_edition = ctk.CTkLabel(
            self.version_frame, textvariable=self.char_edition, font=("Fira Code", 12)
        )
        self.character_edition.grid(padx=1, pady=1, column=1, row=3)

    # callbacks
    def start_thread(self, func):
        thread = threading.Thread(target=func)
        thread.start()

    def start_server(self):
        # start server
        width, height = GetSystemMetrics(0), GetSystemMetrics(1)
        server_win = ahk.win_get(title=self.cfg.selected_version)
        if server_win:
            server_win.move(x="-5", y="0", width=width / 2, height=height)
        else:
            args = ["wt", "-d", self.cfg.server_folder, self.cfg.server_exe]
            proc = subprocess.Popen(args, stdout=subprocess.PIPE)
            # while True:
            #     for line in proc.stdout.readline():
            #         if line:
            #             print(line)
            #         if not line:
            #             break

        auto_start = self.cfg.getboolean("general", "auto_start_launcher")
        if auto_start:
            server_win = ahk.win_wait(title=self.cfg.selected_version, timeout=5)
            server_win.move(x="-5", y="0", width=width / 2, height=height)
            self.auto_start_countdown(self.cfg.wait_time)
            self.start_thread(self.start_launcher)
        self.start_launcher_button.configure(text="Start Launcher")
        self.server_running = True
        # utils.hide_window("SPT Launcher")

    def start_launcher(self):
        win = ahk.win_get(title="Aki.Launcher")
        if win:
            win.activate()
        else:
            subprocess.Popen(rf"{self.cfg.launcher_exe}", cwd=self.cfg.server_folder)
        self.launcher_running = True

    # events
    def autostart_checkbox_event(self):
        state = self.auto_start_var.get()
        print(state)
        if state == "1":
            self.auto_start_launcher = True
            self.cfg.write_config("general", "auto_start_launcher", "True")
        else:
            self.auto_start_launcher = False
            self.cfg.write_config("general", "auto_start_launcher", "False")

    def get_versions(self):
        versions = []
        for vers in self.cfg.sections():
            if vers.startswith("SPT-AKI"):
                versions.append(vers)
        return versions

    def select_version(self, choice: str):
        if choice == "Add New Version":
            self.new_version_window()
        else:
            self.cfg.selected_version = choice
            self.cfg.write_config("prog_data", "selected_version", choice)
            self.update_char_info()

    def new_version_window(self):
        self.add_new_version_window = ctk.CTkToplevel(self)
        self.add_new_version_window.title("Add New Version")
        self.add_version_frame = ctk.CTkFrame(self.add_new_version_window)
        self.add_version_frame.grid()

        self.version_entry_label = ctk.CTkLabel(
            self.add_version_frame, text="Version: SPT-AKI", font=("Fire Code", 12)
        )
        self.version_entry_label.grid(padx=5, pady=5, row=0, column=0)
        self.version_entry_var = tk.StringVar(self, value="x.x.x")
        self.version_entry = ctk.CTkEntry(
            self.add_version_frame,
            placeholder_text=self.version_entry_var.get(),
            textvariable=self.version_entry_var,
            font=("Fire Code", 12),
        )
        self.version_entry.grid(padx=5, pady=5, row=0, column=1)

        self.spt_folder_label = ctk.CTkLabel(
            self.add_version_frame, text="SPT Folder:", font=("Fire Code", 12)
        )
        self.spt_folder_label.grid(padx=5, pady=5, row=1, column=0)
        self.spt_folder_entry_var = tk.StringVar(self, value="path/to/SPTFolder")
        self.spt_folder_entry = ctk.CTkEntry(
            self.add_version_frame,
            placeholder_text=self.spt_folder_entry_var.get(),
            textvariable=self.spt_folder_entry_var,
            font=("Fire Code", 12),
        )
        self.spt_folder_entry.grid(padx=5, pady=5, row=1, column=1)

        self.profile_id_label = ctk.CTkLabel(
            self.add_version_frame, text="Profile ID: ", font=("Fire Code", 12)
        )
        self.profile_id_label.grid(padx=5, pady=5, row=2, column=0)
        self.profile_id_entry_var = tk.StringVar(
            self, value="5779936a22cb6908c7eb84f2.json"
        )
        self.profile_id_entry = ctk.CTkEntry(
            self.add_version_frame,
            placeholder_text=self.profile_id_entry_var.get(),
            textvariable=self.profile_id_entry_var,
            font=("Fire Code", 12),
        )
        self.profile_id_entry.grid(padx=5, pady=5, row=2, column=1)

        self.add_version_button = ctk.CTkButton(
            self.add_version_frame,
            text="Done",
            command=self.add_new_version,
            font=("Fire Code", 12),
        )
        self.add_version_button.grid(padx=5, pady=5, row=3, columnspan=2)

    def add_new_version(self):
        self.add_new_version_window.destroy()
        self.cfg.selected_version = "SPT-AKI " + self.version_entry_var.get()
        self.cfg.server_folder = self.spt_folder_entry_var.get()
        self.cfg.profile_id = self.profile_id_entry_var.get()
        versions: list = self.version_select.cget("values")
        versions.insert(1, self.cfg.selected_version)
        self.version_select.configure(values=versions)
        self.version_select.set(self.cfg.selected_version)
        if self.cfg.selected_version not in self.cfg.sections():
            print("not in cfg")
            self.cfg.write_config(
                "prog_data", "selected_version", self.cfg.selected_version
            )
            self.cfg.add_new_version_data(
                self.cfg.selected_version, self.cfg.server_folder, self.cfg.profile_id
            )
        else:
            print("in cfg")
        self.update_char_info()

    def save_button_cb(self, **kwargs):
        print(kwargs["wait_time"])
        if kwargs["wait_time"]:
            self.cfg.write_config(
                self.cfg.selected_version, "launcher_wait_time", kwargs["wait_time"]
            )

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
                sptmm.parse_urls(f)

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
        for folder in self.cfg.mods_folders:
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

    # utils
    def get_char_info(self):
        self.cfg.read_config()
        profile_json = os.path.join(
            self.cfg.server_folder, "user\\profiles\\", self.cfg.profile_id + ".json"
        )
        with open(profile_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        name = data["characters"]["pmc"]["Info"]["Nickname"]
        level = data["characters"]["pmc"]["Info"]["Level"]
        edition = data["info"]["edition"]
        char_info = {"name": name, "level": level, "edition": edition}
        return char_info

    def update_char_info(self):
        data = self.get_char_info()
        self.char_name.set(data["name"])
        self.char_level.set(data["level"])
        self.char_edition.set(data["edition"])

    def auto_start_countdown(self, t: int):
        while t >= 0:
            mins, secs = divmod(t, 60)
            # print(secs)
            sleep(1)
            t -= 1
            self.start_launcher_button.configure(text=(str(secs)))
        self.start_launcher_button.configure(text="Starting...")


def main():
    main = UI()

    # mods = main.get_mods_info()[1]
    # sptmm = ModManager(cfg, mods)

    main.after(1000, main.utils.hotkeys.start, main)
    main.mainloop()


if __name__ == "__main__":
    main()
