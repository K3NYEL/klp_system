import os

import customtkinter as ctk


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
    SMALL = {"width": 100, "height": 34, "corner_radius": 8}
    MEDIUM = {"width": 132, "height": 40, "corner_radius": 9}
    LARGE = {"width": 164, "height": 46, "corner_radius": 10}
    FULL = {"height": 44, "corner_radius": 9}


def configure_app_style() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
