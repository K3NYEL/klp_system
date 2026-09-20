from __future__ import annotations

import os
import subprocess
import tkinter as tk
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import customtkinter as ctk
from tkinter import ttk


# ============================================================
# KLP SYSTEM
# Sistema de tema global basado en CustomTkinter
# ============================================================


# ============================================================
# INFORMACIÓN DE LA APLICACIÓN
# ============================================================

CREATOR_URL = "https://github.com/K3NYEL"
APP_NAME = "KLP SYSTEM"
APP_VERSION = "1.1"

FONT_FAMILY = "Arial"


# ============================================================
# RUTAS
# ============================================================

def resource_path(*parts: str) -> str:
    """
    Devuelve la ruta absoluta de un recurso de la aplicación.

    Funciona tanto ejecutando Python directamente como
    ejecutando una versión empaquetada con PyInstaller.
    """

    if getattr(__import__("sys"), "frozen", False):
        base = getattr(__import__("sys"), "_MEIPASS", None)

        if not base:
            base = os.path.dirname(
                __import__("sys").executable
            )
    else:
        base = str(
            Path(__file__).resolve().parents[2]
        )

    return os.path.join(base, *parts)


ICON_FILES = {
    "app": resource_path(
        "app",
        "ui",
        "assets",
        "icon.ico",
    ),
    "app_png": resource_path(
        "app",
        "ui",
        "assets",
        "icon.png",
    ),
    "logo": resource_path(
        "app",
        "ui",
        "assets",
        "logo.png",
    ),
}


ICON_IMAGES: Dict[str, Any] = {}


# ============================================================
# FUENTES
# ============================================================

FONTS = {
    "default": (
        FONT_FAMILY,
        11,
    ),
    "small": (
        FONT_FAMILY,
        10,
    ),
    "body": (
        FONT_FAMILY,
        11,
    ),
    "body_bold": (
        FONT_FAMILY,
        11,
        "bold",
    ),
    "label": (
        FONT_FAMILY,
        10,
        "bold",
    ),
    "heading": (
        FONT_FAMILY,
        18,
        "bold",
    ),
    "title": (
        FONT_FAMILY,
        24,
        "bold",
    ),
    "subtitle": (
        FONT_FAMILY,
        13,
    ),
    "metric": (
        FONT_FAMILY,
        25,
        "bold",
    ),
    "button": (
        FONT_FAMILY,
        11,
        "bold",
    ),
    "badge": (
        FONT_FAMILY,
        10,
        "bold",
    ),
}


# ============================================================
# DETECCIÓN DEL TEMA DEL SISTEMA
# ============================================================

def _detect_from_gsettings() -> Optional[str]:
    """
    Intenta detectar el tema mediante gsettings.
    """

    try:
        result = subprocess.run(
            [
                "gsettings",
                "get",
                "org.gnome.desktop.interface",
                "color-scheme",
            ],
            capture_output=True,
            text=True,
            timeout=1,
            check=False,
        )

        value = result.stdout.strip().lower()

        if "prefer-dark" in value:
            return "oscuro"

        if "prefer-light" in value:
            return "claro"

    except Exception:
        pass

    return None


def _detect_from_xfconf() -> Optional[str]:
    """
    Intenta detectar el tema desde XFCE.
    """

    try:
        result = subprocess.run(
            [
                "xfconf-query",
                "-c",
                "xsettings",
                "-p",
                "/Net/ThemeName",
            ],
            capture_output=True,
            text=True,
            timeout=1,
            check=False,
        )

        theme = result.stdout.strip().lower()

        if any(
            word in theme
            for word in (
                "dark",
                "black",
                "night",
            )
        ):
            return "oscuro"

        if any(
            word in theme
            for word in (
                "light",
                "white",
            )
        ):
            return "claro"

    except Exception:
        pass

    return None


def detect_system_theme() -> str:
    """
    Detecta automáticamente claro u oscuro.

    Prioridad:
        1. gsettings
        2. xfconf
        3. GTK_THEME
        4. claro
    """

    detected = _detect_from_gsettings()

    if detected:
        return detected

    detected = _detect_from_xfconf()

    if detected:
        return detected

    gtk_theme = os.environ.get(
        "GTK_THEME",
        "",
    ).lower()

    if "dark" in gtk_theme:
        return "oscuro"

    if "light" in gtk_theme:
        return "claro"

    return "claro"


DEFAULT_THEME = detect_system_theme()


# ============================================================
# PALETAS KLP SYSTEM
# ============================================================

THEMES = {

    # ========================================================
    # TEMA OSCURO
    # ========================================================

    "oscuro": {

        "window": "#090B10",
        "surface": "#11141B",
        "surface_alt": "#171B23",

        "card": "#131720",
        "card_hover": "#191E28",

        "border": "#252B36",
        "border_light": "#303744",

        "header": "#0D1016",
        "header_text": "#F5F7FA",

        # --------------------------------------------
        # ROJO KLP
        # --------------------------------------------

        "accent": "#E53935",
        "accent_dark": "#C62828",
        "accent_hover": "#EF5350",
        "accent_soft": "#321719",

        "text": "#F1F3F5",
        "text_muted": "#98A2B3",
        "text_disabled": "#5C6470",
        "text_on_accent": "#FFFFFF",

        # --------------------------------------------
        # ESTADOS
        # --------------------------------------------

        "success": "#35C779",
        "success_dark": "#249C5C",
        "success_soft": "#13281D",

        "danger": "#FF5C5C",
        "danger_dark": "#D63D3D",
        "danger_soft": "#321819",

        "warning": "#F2B84B",
        "warning_dark": "#C88B1B",
        "warning_soft": "#302511",

        "info": "#5AA9FF",
        "info_dark": "#337CC7",
        "info_soft": "#14263A",

        "neutral": "#8E99A8",
        "neutral_dark": "#697482",
        "neutral_soft": "#202631",

        # --------------------------------------------
        # TABLAS
        # --------------------------------------------

        "row_alt": "#151A22",
        "row_hover": "#202632",
        "selection": "#B72D2A",
        "selection_text": "#FFFFFF",

        # --------------------------------------------
        # INPUTS
        # --------------------------------------------

        "entry_bg": "#151922",
        "entry_border": "#303744",
        "entry_focus": "#E53935",
        "entry_disabled": "#10131A",

        # --------------------------------------------
        # SCROLL
        # --------------------------------------------

        "scroll_trough": "#10131A",
        "scroll_thumb": "#343B48",
        "scroll_hover": "#454E5D",
    },


    # ========================================================
    # TEMA CLARO
    # ========================================================

    "claro": {

        "window": "#F4F5F7",
        "surface": "#FFFFFF",
        "surface_alt": "#F8F9FB",

        "card": "#FFFFFF",
        "card_hover": "#F9FAFB",

        "border": "#E1E5EA",
        "border_light": "#EDF0F3",

        "header": "#FFFFFF",
        "header_text": "#171A1F",

        # --------------------------------------------
        # ROJO KLP
        # --------------------------------------------

        "accent": "#D9342B",
        "accent_dark": "#B72822",
        "accent_hover": "#E54840",
        "accent_soft": "#FDEDEC",

        "text": "#20242A",
        "text_muted": "#68717D",
        "text_disabled": "#A0A7B0",
        "text_on_accent": "#FFFFFF",

        # --------------------------------------------
        # ESTADOS
        # --------------------------------------------

        "success": "#229A5B",
        "success_dark": "#177644",
        "success_soft": "#E7F6EE",

        "danger": "#D93636",
        "danger_dark": "#AE2727",
        "danger_soft": "#FDECEC",

        "warning": "#C98500",
        "warning_dark": "#A56800",
        "warning_soft": "#FFF5DD",

        "info": "#2679D8",
        "info_dark": "#1D5EA8",
        "info_soft": "#EAF3FF",

        "neutral": "#737D89",
        "neutral_dark": "#59636E",
        "neutral_soft": "#EEF1F4",

        # --------------------------------------------
        # TABLAS
        # --------------------------------------------

        "row_alt": "#F8F9FA",
        "row_hover": "#F2F4F7",
        "selection": "#D9342B",
        "selection_text": "#FFFFFF",

        # --------------------------------------------
        # INPUTS
        # --------------------------------------------

        "entry_bg": "#FFFFFF",
        "entry_border": "#D6DBE1",
        "entry_focus": "#D9342B",
        "entry_disabled": "#F0F2F4",

        # --------------------------------------------
        # SCROLL
        # --------------------------------------------

        "scroll_trough": "#F0F2F4",
        "scroll_thumb": "#C8CED6",
        "scroll_hover": "#B3BBC5",
    },
}


# ============================================================
# ROLES
# ============================================================

ROLES = {
    "plain": {
        "fg": "text",
        "bg": "window",
    },

    "surface": {
        "fg": "text",
        "bg": "surface",
    },

    "card": {
        "fg": "text",
        "bg": "card",
    },

    "muted": {
        "fg": "text_muted",
        "bg": "window",
    },

    "header": {
        "fg": "header_text",
        "bg": "header",
    },

    "accent": {
        "fg": "text_on_accent",
        "bg": "accent",
    },

    "success": {
        "fg": "success",
        "bg": "success_soft",
    },

    "danger": {
        "fg": "danger",
        "bg": "danger_soft",
    },

    "warning": {
        "fg": "warning",
        "bg": "warning_soft",
    },

    "info": {
        "fg": "info",
        "bg": "info_soft",
    },

    "neutral": {
        "fg": "neutral",
        "bg": "neutral_soft",
    },
}


# ============================================================
# BOTONES
# ============================================================

BUTTON_VARIANTS = {

    "primary": {
        "fg": "text_on_accent",
        "bg": "accent",
        "hover": "accent_hover",
    },

    "secondary": {
        "fg": "text",
        "bg": "surface_alt",
        "hover": "card_hover",
    },

    "success": {
        "fg": "text_on_accent",
        "bg": "success",
        "hover": "success_dark",
    },

    "danger": {
        "fg": "text_on_accent",
        "bg": "danger",
        "hover": "danger_dark",
    },

    "warning": {
        "fg": "text_on_accent",
        "bg": "warning",
        "hover": "warning_dark",
    },

    "ghost": {
        "fg": "text",
        "bg": "transparent",
        "hover": "surface_alt",
    },

    "outline": {
        "fg": "accent",
        "bg": "transparent",
        "hover": "accent_soft",
    },
}


# ============================================================
# ALIAS DE TONOS
# ============================================================

TONE_ALIASES = {
    "ok": "success",
    "success": "success",

    "error": "danger",
    "danger": "danger",

    "info": "info",

    "accent": "accent",

    "warning": "warning",
    "warn": "warning",

    "neutral": "neutral",
    "muted": "neutral",
}


# ============================================================
# ESTADO GLOBAL
# ============================================================

_current_theme = DEFAULT_THEME

_REGISTRY: Dict[Any, Tuple[str, Dict[str, Any]]] = {}

_manager = None


# ============================================================
# INPUT STYLE
# ============================================================

INPUT_STYLE = {
    "fg_color": "#FFFFFF",
    "border_color": "#D6DBE1",
    "border_width": 1,
    "corner_radius": 8,
    "height": 38,
}


# ============================================================
# UTILIDADES DEL TEMA
# ============================================================

def theme_name() -> str:
    return _current_theme


def is_dark() -> bool:
    return _current_theme == "oscuro"


@property
def colors():
    return THEMES[_current_theme]


# Compatibilidad:
# theme.colors["accent"]
colors = THEMES[_current_theme]


def _refresh_colors_reference():
    global colors
    colors = THEMES[_current_theme]


def color(name: str) -> str:
    """
    Obtiene un color del tema actual.

    Soporta:
        accent
        success
        ok
        ok_soft
        success_soft
        etc.
    """

    if not isinstance(name, str):
        return name

    if name == "transparent":
        return "transparent"

    aliases = TONE_ALIASES

    # Alias directo
    if name in aliases:
        name = aliases[name]

    # Alias con sufijo
    for suffix in (
        "_soft",
        "_dark",
        "_hover",
    ):
        if name.endswith(suffix):
            base = name[:-len(suffix)]

            if base in aliases:
                name = (
                    aliases[base]
                    + suffix
                )

            break

    palette = THEMES[_current_theme]

    return palette.get(
        name,
        name,
    )


def font(role: str = "default"):
    return FONTS.get(
        role,
        FONTS["default"],
    )


def role_colors(role: str = "plain") -> Dict[str, str]:
    spec = ROLES.get(
        role,
        ROLES["plain"],
    )

    return {
        key: color(value)
        for key, value in spec.items()
    }


def button_palette(
    variant: str = "primary",
) -> Dict[str, str]:

    spec = BUTTON_VARIANTS.get(
        variant,
        BUTTON_VARIANTS["primary"],
    )

    return {
        key: color(value)
        for key, value in spec.items()
    }


# ============================================================
# REGISTRO DE WIDGETS
# ============================================================

def remember(
    widget,
    kind: str = "plain",
    **spec,
):
    """
    Registra un widget para que pueda recibir
    cambios globales de tema.
    """

    if widget is None:
        return widget

    _REGISTRY[widget] = (
        kind,
        dict(spec),
    )

    return widget


def forget(widget):
    _REGISTRY.pop(
        widget,
        None,
    )


# ============================================================
# APLICAR CONFIGURACIÓN SEGURA
# ============================================================

def _safe_configure(widget, **kwargs):
    """
    Configura propiedades individualmente para evitar
    que una propiedad no compatible rompa todo el repaint.
    """

    for key, value in kwargs.items():

        if value is None:
            continue

        try:
            widget.configure(
                **{key: value}
            )
        except (
            tk.TclError,
            AttributeError,
        ):
            pass


# ============================================================
# CENTRAR VENTANAS
# ============================================================

def center_window(
    window,
    width: Optional[int] = None,
    height: Optional[int] = None,
):
    """
    Centra una ventana en la pantalla.
    """

    if width is not None and height is not None:
        window.geometry(
            f"{width}x{height}"
        )

    window.update_idletasks()

    try:
        width = window.winfo_width()
        height = window.winfo_height()

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = max(
            0,
            (screen_width - width) // 2,
        )

        y = max(
            0,
            (screen_height - height) // 2,
        )

        window.geometry(
            f"{width}x{height}+{x}+{y}"
        )

    except tk.TclError:
        pass


# ============================================================
# GEOMETRÍA
# ============================================================

def _normalize_geometry(
    geometry,
) -> Optional[str]:

    if geometry is None:
        return None

    if isinstance(
        geometry,
        (tuple, list),
    ):
        if len(geometry) >= 2:
            return (
                f"{int(geometry[0])}"
                f"x"
                f"{int(geometry[1])}"
            )

    return str(geometry)


# ============================================================
# VENTANAS TOPLEVEL
# ============================================================

def prepare_toplevel(
    parent,
    title="",
    geometry=None,
    base_path=None,
    resizable=(True, True),
    modal=False,
):
    """
    Crea y configura una ventana secundaria.

    Compatible con:

        prepare_toplevel(
            parent,
            "Mi empresa",
            (640, 470),
            base_path,
            modal=True,
        )
    """

    window = ctk.CTkToplevel(
        parent,
    )

    if title:
        window.title(title)

    normalized = _normalize_geometry(
        geometry
    )

    if normalized:
        window.geometry(
            normalized
        )

    # Compatibilidad con llamadas existentes
    if base_path is not None:
        try:
            set_app_icon(
                window,
                base_path,
            )
        except Exception:
            pass

    if isinstance(
        resizable,
        tuple,
    ):
        window.resizable(
            *resizable
        )

    elif isinstance(
        resizable,
        bool,
    ):
        window.resizable(
            resizable,
            resizable,
        )

    if modal:
        try:
            window.transient(parent)
            window.grab_set()
        except tk.TclError:
            pass

    center_window(window)

    return window


def release_modal(window):
    try:
        window.grab_release()
    except tk.TclError:
        pass


# ============================================================
# SEPARADOR
# ============================================================

def separator(
    parent,
    orient="horizontal",
    **kwargs,
):
    """
    Crea un separador compatible con Tkinter/CustomTkinter.

    Los parámetros de geometría como padx, pady, fill,
    side y expand se consumen antes de crear el widget.
    """

    padx = kwargs.pop(
        "padx",
        0,
    )

    pady = kwargs.pop(
        "pady",
        0,
    )

    fill = kwargs.pop(
        "fill",
        None,
    )

    side = kwargs.pop(
        "side",
        None,
    )

    expand = kwargs.pop(
        "expand",
        False,
    )

    orient_value = (
        "horizontal"
        if str(orient).lower().startswith("h")
        else "vertical"
    )

    if orient_value == "horizontal":

        widget = ctk.CTkFrame(
            parent,
            height=1,
            fg_color=color("border"),
            corner_radius=0,
            **kwargs,
        )

        default_fill = "x"

    else:

        widget = ctk.CTkFrame(
            parent,
            width=1,
            fg_color=color("border"),
            corner_radius=0,
            **kwargs,
        )

        default_fill = "y"

    widget.pack(
        fill=fill or default_fill,
        side=side or "top",
        expand=expand,
        padx=padx,
        pady=pady,
    )

    remember(
        widget,
        "separator",
        orient=orient_value,
    )

    return widget


# ============================================================
# PINTADO DE WIDGETS
# ============================================================

def paint(
    widget,
    kind: str,
    spec: Dict[str, Any],
):
    """
    Reaplica el tema a un widget registrado.
    """

    if widget is None:
        return

    try:

        # ----------------------------------------------------
        # CUSTOMTKINTER
        # ----------------------------------------------------

        if isinstance(
            widget,
            ctk.CTkFrame,
        ):

            bg = spec.get(
                "bg",
                "surface",
            )

            if bg == "transparent":
                fg = "transparent"
            else:
                fg = color(bg)

            _safe_configure(
                widget,
                fg_color=fg,
            )

            return

        if isinstance(
            widget,
            ctk.CTkLabel,
        ):

            bg = spec.get(
                "bg",
                "surface",
            )

            if bg == "transparent":
                fg = "transparent"
            else:
                fg = color(bg)

            _safe_configure(
                widget,
                fg_color=fg,
                text_color=color(
                    spec.get(
                        "fg",
                        "text",
                    )
                ),
            )

            return

        if isinstance(
            widget,
            ctk.CTkButton,
        ):

            variant = spec.get(
                "variant",
                "primary",
            )

            palette = button_palette(
                variant
            )

            _safe_configure(
                widget,
                fg_color=palette["bg"],
                hover_color=palette["hover"],
                text_color=palette["fg"],
            )

            return

        if isinstance(
            widget,
            ctk.CTkEntry,
        ):

            _safe_configure(
                widget,
                fg_color=color(
                    spec.get(
                        "bg",
                        "entry_bg",
                    )
                ),
                border_color=color(
                    spec.get(
                        "border",
                        "entry_border",
                    )
                ),
                text_color=color(
                    spec.get(
                        "fg",
                        "text",
                    )
                ),
                placeholder_text_color=color(
                    "text_muted"
                ),
            )

            return

        if isinstance(
            widget,
            ctk.CTkComboBox,
        ):

            _safe_configure(
                widget,
                fg_color=color(
                    "entry_bg"
                ),
                border_color=color(
                    "entry_border"
                ),
                button_color=color(
                    "accent"
                ),
                button_hover_color=color(
                    "accent_dark"
                ),
                text_color=color(
                    "text"
                ),
            )

            return

        if isinstance(
            widget,
            ctk.CTkCheckBox,
        ):

            _safe_configure(
                widget,
                fg_color=color(
                    "accent"
                ),
                hover_color=color(
                    "accent_hover"
                ),
                border_color=color(
                    "entry_border"
                ),
                text_color=color(
                    "text"
                ),
            )

            return

        if isinstance(
            widget,
            ctk.CTkSwitch,
        ):

            _safe_configure(
                widget,
                progress_color=color(
                    "accent"
                ),
                button_color=color(
                    "surface"
                ),
                button_hover_color=color(
                    "accent_hover"
                ),
                text_color=color(
                    "text"
                ),
            )

            return

        if isinstance(
            widget,
            ctk.CTkSlider,
        ):

            _safe_configure(
                widget,
                progress_color=color(
                    "accent"
                ),
                button_color=color(
                    "accent"
                ),
                button_hover_color=color(
                    "accent_hover"
                ),
                fg_color=color(
                    "surface_alt"
                ),
            )

            return

        if isinstance(
            widget,
            ctk.CTkProgressBar,
        ):

            _safe_configure(
                widget,
                progress_color=color(
                    "accent"
                ),
                fg_color=color(
                    "surface_alt"
                ),
            )

            return

        if isinstance(
            widget,
            ctk.CTkScrollbar,
        ):

            _safe_configure(
                widget,
                fg_color=color(
                    "scroll_trough"
                ),
                button_color=color(
                    "scroll_thumb"
                ),
                button_hover_color=color(
                    "scroll_hover"
                ),
            )

            return

        if isinstance(
            widget,
            ctk.CTkTabview,
        ):

            _safe_configure(
                widget,
                fg_color=color(
                    "surface"
                ),
                segmented_button_fg_color=color(
                    "surface_alt"
                ),
                segmented_button_selected_color=color(
                    "accent"
                ),
                segmented_button_selected_hover_color=color(
                    "accent_hover"
                ),
                segmented_button_unselected_color=color(
                    "surface_alt"
                ),
                segmented_button_unselected_hover_color=color(
                    "card_hover"
                ),
                text_color=color(
                    "text"
                ),
            )

            return

        if isinstance(
            widget,
            ctk.CTkScrollableFrame,
        ):

            _safe_configure(
                widget,
                fg_color=color(
                    "surface"
                ),
            )

            return

        # ----------------------------------------------------
        # TKINTER CLÁSICO
        # ----------------------------------------------------

        if kind == "separator":

            _safe_configure(
                widget,
                fg_color=color(
                    "border"
                ),
            )

            return

        if kind == "badge":

            _safe_configure(
                widget,
                bg=color(
                    spec.get(
                        "bg",
                        "success_soft",
                    )
                ),
                fg=color(
                    spec.get(
                        "fg",
                        "success",
                    )
                ),
                font=font(
                    spec.get(
                        "font",
                        "badge",
                    )
                ),
            )

            return

        if kind == "card":

            _safe_configure(
                widget,
                bg=color(
                    spec.get(
                        "bg",
                        "card",
                    )
                ),
                highlightbackground=color(
                    "border"
                ),
                highlightcolor=color(
                    "border"
                ),
            )

            return

        if kind in {
            "plain",
            "surface",
            "surface_alt",
            "muted",
            "header",
            "accent",
            "success",
            "danger",
            "warning",
            "info",
            "neutral",
        }:

            bg_name = spec.get(
                "bg",
                kind,
            )

            fg_name = spec.get(
                "fg",
                "text",
            )

            _safe_configure(
                widget,
                bg=color(
                    bg_name
                ),
            )

            _safe_configure(
                widget,
                fg=color(
                    fg_name
                ),
            )

            if "font" in spec:
                _safe_configure(
                    widget,
                    font=font(
                        spec["font"]
                    ),
                )

            return

        if kind == "treeview":

            _safe_configure(
                widget,
                background=color(
                    "surface"
                ),
                foreground=color(
                    "text"
                ),
                fieldbackground=color(
                    "surface"
                ),
            )

            return

    except (
        tk.TclError,
        AttributeError,
    ):
        pass


# ============================================================
# CONFIGURACIÓN TTK
# ============================================================

def configure_app_style():
    """
    Configura estilos TTK para las partes de la aplicación
    que todavía utilizan widgets Tkinter clásicos.
    """

    try:

        style = ttk.Style()

        try:
            style.theme_use(
                "clam"
            )
        except tk.TclError:
            pass

        style.configure(
            "KLP.Treeview",
            background=color(
                "surface"
            ),
            foreground=color(
                "text"
            ),
            fieldbackground=color(
                "surface"
            ),
            borderwidth=0,
            relief="flat",
            rowheight=34,
            font=font("body"),
        )

        style.map(
            "KLP.Treeview",
            background=[
                (
                    "selected",
                    color("selection"),
                )
            ],
            foreground=[
                (
                    "selected",
                    color("selection_text"),
                )
            ],
        )

        style.configure(
            "KLP.Treeview.Heading",
            background=color(
                "surface_alt"
            ),
            foreground=color(
                "text"
            ),
            borderwidth=0,
            relief="flat",
            font=font("label"),
        )

        style.map(
            "KLP.Treeview.Heading",
            background=[
                (
                    "active",
                    color("card_hover"),
                )
            ],
        )

        style.configure(
            "KLP.TSeparator",
            background=color(
                "border"
            ),
        )

        style.configure(
            "KLP.TNotebook",
            background=color(
                "window"
            ),
            borderwidth=0,
        )

        style.configure(
            "KLP.TNotebook.Tab",
            background=color(
                "surface_alt"
            ),
            foreground=color(
                "text_muted"
            ),
            padding=(
                14,
                8,
            ),
            font=font("label"),
        )

        style.map(
            "KLP.TNotebook.Tab",
            background=[
                (
                    "selected",
                    color("accent"),
                )
            ],
            foreground=[
                (
                    "selected",
                    color(
                        "text_on_accent"
                    ),
                )
            ],
        )

    except tk.TclError:
        pass


# ============================================================
# INPUT STYLE
# ============================================================

def _update_input_style():

    INPUT_STYLE.update(
        {
            "fg_color": color(
                "entry_bg"
            ),
            "border_color": color(
                "entry_border"
            ),
            "border_width": 1,
            "corner_radius": 8,
            "height": 38,
        }
    )


# ============================================================
# REPAINT
# ============================================================

def repaint_all():

    dead = []

    for widget, data in list(
        _REGISTRY.items()
    ):

        try:
            if not widget.winfo_exists():
                dead.append(widget)
                continue

            kind, spec = data

            paint(
                widget,
                kind,
                spec,
            )

        except (
            tk.TclError,
            AttributeError,
        ):
            dead.append(widget)

    for widget in dead:
        _REGISTRY.pop(
            widget,
            None,
        )


# ============================================================
# RESTYLE
# ============================================================

def restyle(
    root: Optional[tk.Misc] = None,
    **changes,
) -> None:
    """
    Actualiza propiedades de un widget y reaplica el tema.

    Ejemplo:

        theme.restyle(
            badge,
            text="CAJA ABIERTA",
        )
    """

    if root is not None and changes:

        try:
            root.configure(
                **changes
            )

        except tk.TclError:

            for key, value in changes.items():

                try:
                    root.configure(
                        **{
                            key: value
                        }
                    )

                except tk.TclError:
                    pass

    configure_app_style()
    _update_input_style()
    repaint_all()


# ============================================================
# CAMBIAR TEMA
# ============================================================

def apply_theme(
    name: str,
):
    """
    Cambia entre claro y oscuro.
    """

    global _current_theme

    if name not in THEMES:
        name = DEFAULT_THEME

    _current_theme = name

    _refresh_colors_reference()

    _update_input_style()

    # CustomTkinter
    if name == "oscuro":
        ctk.set_appearance_mode(
            "Dark"
        )
    else:
        ctk.set_appearance_mode(
            "Light"
        )

    configure_app_style()
    repaint_all()


# ============================================================
# THEME MANAGER
# ============================================================

class ThemeManager:
    """
    Administrador sencillo del tema global.
    """

    def __init__(
        self,
        root=None,
        theme: Optional[str] = None,
    ):

        global _manager

        self.root = root

        self.theme = (
            theme
            or DEFAULT_THEME
        )

        _manager = self

        apply_theme(
            self.theme
        )

    def set_theme(
        self,
        name: str,
    ):
        if name not in THEMES:
            return

        self.theme = name

        apply_theme(
            name
        )

    def toggle(self):
        self.set_theme(
            "claro"
            if self.theme == "oscuro"
            else "oscuro"
        )

    def is_dark(self):
        return self.theme == "oscuro"

    def colors(self):
        return THEMES[
            self.theme
        ]


# ============================================================
# ICONO
# ============================================================

def set_app_icon(
    window,
    base_path=None,
):
    """
    Configura el icono de la aplicación.

    Primero intenta PNG para CustomTkinter/Tkinter
    y luego ICO.
    """

    candidates = []

    if base_path:

        candidates.extend(
            [
                os.path.join(
                    base_path,
                    "app",
                    "ui",
                    "assets",
                    "icon.png",
                ),
                os.path.join(
                    base_path,
                    "app",
                    "ui",
                    "assets",
                    "icon.ico",
                ),
            ]
        )

    candidates.extend(
        [
            ICON_FILES["app_png"],
            ICON_FILES["app"],
        ]
    )

    for path in candidates:

        if not os.path.exists(path):
            continue

        try:

            if path.lower().endswith(
                ".png"
            ):

                image = tk.PhotoImage(
                    file=path
                )

                ICON_IMAGES[
                    str(window)
                ] = image

                window.iconphoto(
                    True,
                    image,
                )

                return

            if path.lower().endswith(
                ".ico"
            ):

                window.iconbitmap(
                    path
                )

                return

        except (
            tk.TclError,
            OSError,
        ):
            continue


# ============================================================
# TOOLTIP
# ============================================================

class Tooltip:
    """
    Tooltip ligero para widgets Tkinter/CustomTkinter.
    """

    def __init__(
        self,
        widget,
        text,
        delay=500,
    ):

        self.widget = widget
        self.text = text
        self.delay = delay

        self.tipwindow = None
        self.after_id = None

        self._enter_id = widget.bind(
            "<Enter>",
            self._schedule,
            add="+",
        )

        self._leave_id = widget.bind(
            "<Leave>",
            self._hide,
            add="+",
        )

        self._button_id = widget.bind(
            "<ButtonPress>",
            self._hide,
            add="+",
        )

    def _schedule(self, _event=None):

        self._hide()

        try:
            self.after_id = (
                self.widget.after(
                    self.delay,
                    self._show,
                )
            )

        except tk.TclError:
            pass

    def _show(self):

        self.after_id = None

        try:

            if not self.widget.winfo_exists():
                return

            x = (
                self.widget.winfo_rootx()
                + 10
            )

            y = (
                self.widget.winfo_rooty()
                + self.widget.winfo_height()
                + 5
            )

            self.tipwindow = tk.Toplevel(
                self.widget
            )

            self.tipwindow.wm_overrideredirect(
                True
            )

            self.tipwindow.geometry(
                f"+{x}+{y}"
            )

            label = tk.Label(
                self.tipwindow,
                text=self.text,
                bg=color("surface"),
                fg=color("text"),
                relief="solid",
                borderwidth=1,
                padx=8,
                pady=5,
                font=font("small"),
            )

            label.pack()

        except tk.TclError:
            self.tipwindow = None

    def _hide(self, _event=None):

        if self.after_id:

            try:
                self.widget.after_cancel(
                    self.after_id
                )
            except tk.TclError:
                pass

            self.after_id = None

        if self.tipwindow:

            try:
                self.tipwindow.destroy()
            except tk.TclError:
                pass

            self.tipwindow = None

    def destroy(self):

        self._hide()

        try:
            self.widget.unbind(
                "<Enter>",
                self._enter_id,
            )
        except tk.TclError:
            pass

        try:
            self.widget.unbind(
                "<Leave>",
                self._leave_id,
            )
        except tk.TclError:
            pass

        try:
            self.widget.unbind(
                "<ButtonPress>",
                self._button_id,
            )
        except tk.TclError:
            pass


# ============================================================
# INFORMACIÓN DEL TEMA
# ============================================================

def system_theme_info():

    detected = detect_system_theme()

    return {
        "detected": detected,
        "current": _current_theme,
        "available": list(
            THEMES.keys()
        ),
        "is_dark": (
            _current_theme
            == "oscuro"
        ),
    }


# ============================================================
# CONFIGURACIÓN INICIAL
# ============================================================

_update_input_style()


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "CREATOR_URL",

    "FONTS",
    "FONT_FAMILY",

    "ICON_FILES",
    "ICON_IMAGES",

    "INPUT_STYLE",

    "THEMES",
    "ROLES",
    "BUTTON_VARIANTS",
    "TONE_ALIASES",

    "ThemeManager",
    "Tooltip",

    "apply_theme",
    "button_palette",
    "center_window",
    "color",
    "colors",
    "configure_app_style",
    "detect_system_theme",
    "font",
    "is_dark",
    "paint",
    "prepare_toplevel",
    "repaint_all",
    "remember",
    "forget",
    "release_modal",
    "resource_path",
    "restyle",
    "role_colors",
    "separator",
    "set_app_icon",
    "system_theme_info",
    "theme_name",
]