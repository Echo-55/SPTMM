# vscode-fold=2
import typing

import customtkinter as ctk

if typing.TYPE_CHECKING:
    from spt import UI


class OptionsFrame(ctk.CTkFrame):
    """
    Options frame within the master frame.

    Args:
        master (UI): The master window.
    """

    width = 370
    height = 50

    def __init__(self, master: "UI", **kwargs):
        super().__init__(
            master,
            width=self.width,
            height=self.height,
        )
