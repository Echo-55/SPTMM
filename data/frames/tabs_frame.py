# vscode-fold=2
import tkinter as tk
import typing
import webbrowser
from time import sleep

import customtkinter as ctk

if typing.TYPE_CHECKING:
    from data.frames.options_frame import OptionsFrame
    from spt import UI


class MasterTabsFrame(ctk.CTkTabview):
    """
    This is the master frame that contains all the tabs.\nParent: OptionsFrame\n

    Tabs:\n
        - Launcher
        - Mods
        - Settings

    Args:
        master (UI): The master window.
        parent (OptionsFrame): The parent frame.
    """

    width = 350
    height = 50

    def __init__(self, master: "UI", parent: "OptionsFrame", **kwargs):
        super().__init__(
            parent,
            width=self.width,
            height=self.height,
        )
        self.master = master

        self.launcher_tab = self.add("Launcher")

        self.mods_tab = self.add("Mods")
        self.mods_tab.grid_rowconfigure(0, weight=1)
        self.mods_tab.grid_columnconfigure(0, weight=1)

        self.settings_tab = self.add("Settings")
        self.settings_tab.grid_rowconfigure(0, weight=1)
        self.settings_tab.grid_columnconfigure(0, weight=1)


class LauncherTabFrame(ctk.CTkFrame):
    """
    This is the frame that contains the launcher tab.\nParent: MasterTabsFrame\n

    Args:
        master (UI): The master window.
        parent (TabsFrame): The parent frame.
    """

    def __init__(self, master: "UI", parent: MasterTabsFrame, **kwargs):
        super().__init__(parent.launcher_tab, **kwargs)
        self.auto_start_launcher = master.cfg.getboolean(
            "general", "auto_start_launcher"
        )

        self.start_server_button = ctk.CTkButton(
            self,
            width=170,
            height=28,
            text="Start Server",
            command=lambda: master.start_thread(master.start_server),
            font=("Fira Code", 12),
            hover_color="#487014",
            border_width=2,
            border_color="#487014",
        )
        self.start_server_button.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.start_launcher_button = ctk.CTkButton(
            self,
            width=170,
            height=28,
            text="Start Launcher",
            command=lambda: master.start_thread(master.start_launcher),
            font=("Fira Code", 12),
            hover_color="#487014",
            border_width=2,
            border_color="#487014",
        )
        self.start_launcher_button.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        if self.auto_start_launcher:
            self.auto_start_var = tk.StringVar(
                self, value="1", name="self.auto_start_var"
            )
        else:
            self.auto_start_var = tk.StringVar(
                self, value="0", name="self.auto_start_var"
            )

        self.auto_start_launcher_checkbox = ctk.CTkCheckBox(
            self,
            text="Auto Start Launcher",
            command=self.autostart_checkbox_event(master),
            variable=self.auto_start_var,
            onvalue=1,
            offvalue=0,
            font=("Fira Code", 10),
            width=15,
            height=15,
            checkbox_width=15,
            checkbox_height=15,
        )
        self.auto_start_launcher_checkbox.grid(padx=5, pady=5, row=1, columnspan=2)

        if self.auto_start_launcher:
            self.auto_start_launcher_checkbox.select(True)

    def autostart_checkbox_event(self, master: "UI"):
        state = self.auto_start_var.get()
        print(state)
        if state == "1":
            self.auto_start_launcher = True
            master.cfg.write_config("general", "auto_start_launcher", "True")
        else:
            self.auto_start_launcher = False
            master.cfg.write_config("general", "auto_start_launcher", "False")

    def auto_start_countdown(self, t: int):
        while t >= 0:
            mins, secs = divmod(t, 60)
            # print(secs)
            sleep(1)
            t -= 1
            self.start_launcher_button.configure(text=(str(secs)))
        self.start_launcher_button.configure(text="Starting...")


class ModsTabFrame(ctk.CTkFrame):
    """
    This is the frame that contains the mods tab.\nParent: MasterTabsFrame\n

    Args:
        master (UI): The master window.
        parent (TabsFrame): The parent frame.
    """

    def __init__(self, master: "UI", parent: MasterTabsFrame, **kwargs):
        super().__init__(parent.mods_tab, **kwargs)

        # open spt directory button
        self.open_dir_button = ctk.CTkButton(
            self,
            text="Open SPT Folder",
            command=master.utils.open_spt_dir,
            font=("Fira Code", 12),
        )
        self.open_dir_button.grid(padx=5, pady=5, row=0, column=2)

        # open mod table
        self.open_mod_table_btn = ctk.CTkButton(
            self,
            text="View Mods Table",
            # command=self.build_mods_table,
            font=("Fira Code", 12),
        )
        self.open_mod_table_btn.grid(padx=5, pady=5, row=1, column=2)

        # install mod button
        self.install_mod_button = ctk.CTkButton(
            self,
            text="Install Mods",
            # command=self.install_mod_window,
            font=("Fira Code", 12),
        )
        self.install_mod_button.grid(padx=5, pady=5, row=0, column=3)

        self.open_hub_button = ctk.CTkButton(
            self,
            text="Open SPT Hub",
            command=lambda: webbrowser.open_new_tab(
                "https://hub.sp-tarkov.com/files/"
            ),  # type: ignore
            font=("Fira Code", 12),
        )
        self.open_hub_button.grid(padx=5, pady=5, row=1, column=3)


class SettingsTabFrame(ctk.CTkFrame):
    """
    This is the frame that contains the settings tab.\nParent: MasterTabsFrame\n

    Args:
        master (UI): The master window.
        parent (TabsFrame): The parent frame.
    """

    def __init__(self, master: "UI", parent: MasterTabsFrame, **kwargs):
        super().__init__(parent.settings_tab, **kwargs)
        # self.master = master

        self.grid_columnconfigure(0, weight=1)

        self.auto_start_label = ctk.CTkLabel(
            self, text="Launcher auto-start wait time: "
        )
        self.auto_start_label.grid(padx=5, pady=5, column=0, row=0)

        self.wait_time = tk.StringVar(
            self,
            value=master.cfg.get(master.cfg.selected_version, "launcher_wait_time"),
        )
        self.auto_start_entry = ctk.CTkEntry(
            self,
            width=30,
            height=20,
            textvariable=self.wait_time,
        )
        self.auto_start_entry.grid(padx=3, pady=3, column=1, row=0)

        self.save_button = ctk.CTkButton(
            self,
            text="Save",
            command=lambda: self.save_button_cb(
                master=master, wait_time=self.wait_time.get()
            ),
        )
        self.save_button.grid(padx=5, pady=5, columnspan=2, row=1)

    def save_button_cb(self, **kwargs):
        master: "UI" = kwargs["master"]
        if kwargs["wait_time"]:
            master.cfg.write_config(
                master.cfg.selected_version, "launcher_wait_time", kwargs["wait_time"]
            )
