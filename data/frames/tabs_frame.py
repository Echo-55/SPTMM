# vscode-fold=2
import tkinter as tk
import typing
import webbrowser
from time import sleep

import customtkinter as ctk

if typing.TYPE_CHECKING:
    from spt import UI, MainFrame


class MasterTabsFrame(ctk.CTkTabview):
    """
    This is the master frame that contains all the tabs.\nParent: MainFrame\n

    Tabs:\n
        - Launcher
        - Mods
        - Settings

    Args:
        master (UI): The master window.
        parent (MainFrame): The parent frame.
    """

    width = 350
    height = 50

    def __init__(self, master_window: "UI", parent: "MainFrame", **kwargs):
        super().__init__(
            parent,
            width=self.width,
            height=self.height,
        )
        self.master_window = master_window

        # add tabs
        self.launcher_tab: LauncherTabFrame = self.add("Launcher")

        self.mods_tab: ModsTabFrame = self.add("Mods")
        self.mods_tab.grid_rowconfigure(0, weight=1)
        self.mods_tab.grid_columnconfigure(0, weight=1)

        self.settings_tab: SettingsTabFrame = self.add("Settings")
        self.settings_tab.grid_rowconfigure(0, weight=1)
        self.settings_tab.grid_columnconfigure(0, weight=1)

        # add frames to tabs
        self.launcher_tab_frame = LauncherTabFrame(self.master_window, self)
        self.launcher_tab_frame.grid(padx=5, pady=5, column=0, row=2)

        self.mods_tab_frame = ModsTabFrame(self.master_window, self)
        self.mods_tab_frame.grid(padx=5, pady=5, row=0, column=0, sticky="ns")

        self.settings_tab_frame = SettingsTabFrame(self.master_window, self)
        self.settings_tab_frame.grid(padx=5, pady=5, row=0, column=0, sticky="ns")


class LauncherTabFrame(ctk.CTkFrame):
    """
    This is the frame that contains the launcher tab.\n
    
    Parent: MasterTabsFrame\n

    Args:
        master (UI): The master window.
        parent (TabsFrame): The parent frame.
    """

    def __init__(self, master_window: "UI", parent: MasterTabsFrame, **kwargs):
        super().__init__(parent.launcher_tab, **kwargs)

        self.master_window = master_window

        self.auto_start_launcher = self.master_window.cfg.getboolean(
            "general", "auto_start_launcher"
        )

        self.start_server_button = ctk.CTkButton(
            self,
            width=170,
            height=28,
            text="Start Server",
            command=lambda: self.master_window.utils.start_thread(
                self.master_window.utils.start_server
            ),
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
            command=lambda: self.master_window.utils.start_thread(
                self.master_window.utils.start_launcher
            ),
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
            command=lambda: self.autostart_checkbox_event(),
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

    def autostart_checkbox_event(self):
        """
        Called when the autostart checkbox is clicked.\n
        Changes the value of self.auto_start_launcher to the value of the checkbox.\n
        """
        state = self.auto_start_var.get()
        print(state)
        if state == "1":
            self.auto_start_launcher = True
            self.master_window.cfg.write_to_config("general", "auto_start_launcher", "True")
        else:
            self.auto_start_launcher = False
            self.master_window.cfg.write_to_config("general", "auto_start_launcher", "False")

    def auto_start_countdown(self, t: int):
        """
        Used to display the countdown to the user by changing the text inside the start_launcher_button to the countdown.\n
        Must be called in a thread.\n
        """
        while t >= 0:
            mins, secs = divmod(t, 60)
            sleep(1)
            t -= 1
            self.start_launcher_button.configure(text=str(secs))
        
        # ensure that the ui is updated
        self.master_window.after(0, self.start_launcher_button.configure(text="Starting..."))


class ModsTabFrame(ctk.CTkFrame):
    """
    This is the frame that contains the mods tab.\nParent: MasterTabsFrame\n

    Args:
        master (UI): The master window.
        parent (TabsFrame): The parent frame.
    """

    def __init__(self, master_window: "UI", parent: MasterTabsFrame, **kwargs):
        super().__init__(parent.mods_tab, **kwargs)

        self.master_window = master_window

        # open spt directory button
        self.open_dir_button = ctk.CTkButton(
            self,
            text="Open SPT Folder",
            command=self.master_window.utils.open_spt_dir,
            font=("Fira Code", 12),
        )
        self.open_dir_button.grid(padx=5, pady=5, row=0, column=2)

        # open mod table
        self.open_mod_table_btn = ctk.CTkButton(
            self,
            text="View Mods Table",
            command=self.master_window.sptmm.build_mods_table,
            font=("Fira Code", 12),
        )
        self.open_mod_table_btn.grid(padx=5, pady=5, row=1, column=2)

        # install mod button
        self.install_mod_button = ctk.CTkButton(
            self,
            text="Install Mods",
            command=self.master_window.sptmm.install_mod_window,
            font=("Fira Code", 12),
        )
        self.install_mod_button.grid(padx=5, pady=5, row=1, column=3)

        self.open_hub_button = ctk.CTkButton(
            self,
            text="SPT Hub",
            image=self.master_window.utils.images["link"],
            command=lambda: webbrowser.open_new_tab(
                "https://hub.sp-tarkov.com/files/"
            ),  # type: ignore
            font=("Fira Code", 12),
        )
        self.open_hub_button.grid(padx=5, pady=5, row=0, column=3)


class SettingsTabFrame(ctk.CTkFrame):
    """
    This is the frame that contains the settings tab.\nParent: MasterTabsFrame\n

    Args:
        master (UI): The master window.
        parent (TabsFrame): The parent frame.
    """

    def __init__(self, master_window: "UI", parent: MasterTabsFrame, **kwargs):
        super().__init__(parent.settings_tab, **kwargs)
        self.master_window = master_window

        self.grid_columnconfigure(0, weight=1)

        self.auto_start_label = ctk.CTkLabel(
            self, text="Launcher auto-start wait time: "
        )
        self.auto_start_label.grid(padx=5, pady=5, column=0, row=0)

        self.wait_time = tk.StringVar(
            self,
            value=self.master_window.cfg.get(self.master_window.cfg.selected_version, "launcher_wait_time"),
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
                master_window=self.master_window, wait_time=self.wait_time.get()
            ),
        )
        self.save_button.grid(padx=5, pady=5, columnspan=2, row=1)

    def save_button_cb(self, **kwargs):
        master_window: "UI" = kwargs["master_window"]
        if kwargs["wait_time"]:
            master_window.cfg.write_to_config(
                master_window.cfg.selected_version, "launcher_wait_time", kwargs["wait_time"]
            )
