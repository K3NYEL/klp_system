import os
import tkinter as tk
from tkinter import ttk


class Colors:
    BACKGROUND = "#090B10"
    SURFACE = "#11141B"
    SURFACE_HOVER = "#171B23"
    CARD = "#131720"
    CARD_HOVER = "#191E28"
    INPUT = "#171B23"
    BORDER = "#252B36"
    BORDER_LIGHT = "#303744"
    TEXT = "#F1F3F5"
    TEXT_SECONDARY = "#98A2B3"
    TEXT_MUTED = "#737D8C"
    TEXT_DISABLED = "#5C6470"
    PRIMARY = "#E53935"
    PRIMARY_HOVER = "#EF5350"
    PRIMARY_DARK = "#C62828"
    SUCCESS = "#35C779"
    SUCCESS_HOVER = "#249C5C"
    WARNING = "#F2B84B"
    WARNING_HOVER = "#C88B1B"
    DANGER = "#FF5C5C"
    DANGER_HOVER = "#D63D3D"
    INFO = "#5AA9FF"
    INFO_HOVER = "#337CC7"
    SECONDARY = "#202631"
    SECONDARY_HOVER = "#303744"
    NEUTRAL = SECONDARY
    NEUTRAL_HOVER = SECONDARY_HOVER
    TRANSPARENT = "transparent"


class Fonts:
    FAMILY = "Segoe UI" if os.name == "nt" else "DejaVu Sans"
    BUTTON = (FAMILY, 11, "bold")
    BUTTON_SMALL = (FAMILY, 10, "bold")
    BUTTON_LARGE = (FAMILY, 12, "bold")
    TITLE = (FAMILY, 24, "bold")
    SUBTITLE = (FAMILY, 18, "bold")
    BODY = (FAMILY, 11)
    BODY_BOLD = (FAMILY, 11, "bold")
    SMALL = (FAMILY, 10)
    SMALL_BOLD = (FAMILY, 10, "bold")


class ButtonSizes:
    SMALL = {"width": 100, "height": 34}
    MEDIUM = {"width": 132, "height": 40}
    LARGE = {"width": 164, "height": 46}
    FULL = {"height": 44}


def configure_app_style(root=None):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        ".",
        background=Colors.BACKGROUND,
        foreground=Colors.TEXT,
        font=Fonts.BODY,
    )
    style.configure(
        "TFrame",
        background=Colors.BACKGROUND,
    )
    style.configure(
        "Surface.TFrame",
        background=Colors.SURFACE,
    )
    style.configure(
        "Card.TFrame",
        background=Colors.CARD,
        borderwidth=1,
        relief="solid",
    )
    style.configure(
        "TLabel",
        background=Colors.BACKGROUND,
        foreground=Colors.TEXT,
        font=Fonts.BODY,
    )
    style.configure(
        "Title.TLabel",
        background=Colors.SURFACE,
        foreground=Colors.PRIMARY,
        font=Fonts.TITLE,
    )
    style.configure(
        "Subtitle.TLabel",
        background=Colors.SURFACE,
        foreground=Colors.TEXT_SECONDARY,
        font=Fonts.BODY,
    )
    style.configure(
        "Status.TLabel",
        background=Colors.SURFACE,
        foreground=Colors.TEXT_SECONDARY,
        font=Fonts.SMALL,
    )
    style.configure(
        "TButton",
        background=Colors.SECONDARY,
        foreground=Colors.TEXT,
        padding=(12, 8),
        borderwidth=0,
        font=Fonts.BUTTON,
    )
    style.map(
        "TButton",
        background=[("active", Colors.SECONDARY_HOVER), ("disabled", Colors.SURFACE)],
        foreground=[("disabled", Colors.TEXT_DISABLED)],
    )
    style.configure(
        "Primary.TButton",
        background=Colors.PRIMARY,
        foreground="#FFFFFF",
    )
    style.map(
        "Primary.TButton",
        background=[("active", Colors.PRIMARY_HOVER), ("disabled", Colors.PRIMARY_DARK)],
    )
    style.configure(
        "TEntry",
        fieldbackground=Colors.INPUT,
        foreground=Colors.TEXT,
        insertcolor=Colors.TEXT,
        padding=8,
    )
    style.configure(
        "TCombobox",
        fieldbackground=Colors.INPUT,
        background=Colors.INPUT,
        foreground=Colors.TEXT,
        arrowcolor=Colors.TEXT,
        padding=7,
    )
    style.configure(
        "TProgressbar",
        troughcolor=Colors.BORDER,
        background=Colors.PRIMARY,
        bordercolor=Colors.BORDER,
        lightcolor=Colors.PRIMARY,
        darkcolor=Colors.PRIMARY,
    )
    style.configure(
        "Treeview",
        background=Colors.CARD,
        fieldbackground=Colors.CARD,
        foreground=Colors.TEXT,
        rowheight=30,
        borderwidth=0,
        font=Fonts.BODY,
    )
    style.configure(
        "Treeview.Heading",
        background=Colors.SURFACE,
        foreground=Colors.TEXT,
        relief="flat",
        font=Fonts.BODY_BOLD,
    )
    style.map(
        "Treeview",
        background=[("selected", Colors.PRIMARY_DARK)],
        foreground=[("selected", "#FFFFFF")],
    )
    return style
