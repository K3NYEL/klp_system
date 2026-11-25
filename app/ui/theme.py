from __future__ import annotations

import os
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import ttk
from typing import Any, Dict, Optional, Tuple

from app.ui import tk_widgets as tkui

CREATOR_URL = "https://github.com/K3NYEL"
APP_NAME = "KLP SYSTEM"
APP_VERSION = "1.1"
FONT_FAMILY = "Inter"
_FONT_CANDIDATES = ("Inter", "DejaVu Sans", "Noto Sans", "Liberation Sans", "Arial", "Helvetica")
_FONT_ROOT_ID = None


def resource_path(*parts: str) -> str:
    """
    Devuelve la ruta absoluta de un recurso de la aplicación.

    Funciona tanto ejecutando Python directamente como
    ejecutando una versión empaquetada con PyInstaller.
    """
    import sys

    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", None)

        if not base:
            base = os.path.dirname(sys.executable)
    else:
        base = str(Path(__file__).resolve().parents[2])

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


# Mantiene vivas las imágenes PhotoImage mientras
# la ventana correspondiente exista.
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
    "nav": (FONT_FAMILY, 9),
    "nav_bold": (FONT_FAMILY, 9, "bold"),
    "tiny": (FONT_FAMILY, 8, "bold"),
}


# ============================================================
# TEMA FIJO
# ============================================================

DEFAULT_THEME = "claro"
_current_theme = "claro"


# ============================================================
# PALETA KLP SYSTEM
# ============================================================

THEMES = {
    "claro": {
        # ----------------------------------------------------
        # SUPERFICIES
        # ----------------------------------------------------
        "window": "#FAFAF8",
        "surface": "#FFFFFF",
        "surface_alt": "#F3F2EF",
        "card": "#FFFFFF",
        "card_hover": "#FAFAF8",
        "border": "#ECEAE6",
        "border_light": "#DDDAD4",
        "header": "#FFFFFF",
        "header_text": "#1C1C1A",
        # ----------------------------------------------------
        # ROJO KLP
        # ----------------------------------------------------
        "accent": "#C8312E",
        "accent_dark": "#A92724",
        "accent_hover": "#B52B28",
        "accent_soft": "#FBE9E8",
        "text": "#1C1C1A",
        "text_muted": "#6B6B66",
        "text_disabled": "#A5A49F",
        "text_on_accent": "#FFFFFF",
        # ----------------------------------------------------
        # ESTADOS
        # ----------------------------------------------------
        "success": "#27834A",
        "success_dark": "#1E6B3C",
        "success_soft": "#E8F4EB",
        "danger": "#C8312E",
        "danger_dark": "#A92724",
        "danger_soft": "#FBE9E8",
        "warning": "#A66B12",
        "warning_dark": "#80520D",
        "warning_soft": "#FBF2DF",
        "info": "#286C9C",
        "info_dark": "#20577F",
        "info_soft": "#EAF3F8",
        "neutral": "#F3F2EF",
        "neutral_dark": "#E8E6E1",
        "neutral_soft": "#F3F2EF",
        # ----------------------------------------------------
        # TABLAS
        # ----------------------------------------------------
        "row_alt": "#FAFAF8",
        "row_hover": "#F3F2EF",
        "selection": "#FBE9E8",
        "selection_text": "#1C1C1A",
        # ----------------------------------------------------
        # INPUTS
        # ----------------------------------------------------
        "entry_bg": "#FFFFFF",
        "entry_border": "#DDDAD4",
        "entry_focus": "#C8312E",
        "entry_disabled": "#F3F2EF",
        # ----------------------------------------------------
        # SCROLL
        # ----------------------------------------------------
        "scroll_trough": "#F3F2EF",
        "scroll_thumb": "#C9C7C1",
        "scroll_hover": "#A9A79F",
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

_REGISTRY: Dict[Any, Tuple[str, Dict[str, Any]]] = {}
_manager = None


# ============================================================
# INPUT STYLE
# ============================================================

INPUT_STYLE = {
    "fg_color": "#FFFFFF",
    "border_color": "#DDDAD4",
    "border_width": 1,
    "corner_radius": 8,
    "height": 38,
}


# ============================================================
# UTILIDADES DEL TEMA
# ============================================================


def theme_name() -> str:
    """Devuelve siempre el nombre del tema de KLP SYSTEM."""
    return "claro"


def is_dark() -> bool:
    """KLP SYSTEM utiliza siempre el tema claro."""
    return False


# Compatibilidad:
# theme.colors["accent"]
colors = THEMES["claro"]


def _refresh_colors_reference():
    global colors
    colors = THEMES["claro"]


def color(name: str) -> str:
    """
    Obtiene un color del tema claro actual.

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
            base = name[: -len(suffix)]

            if base in aliases:
                name = aliases[base] + suffix
                break

    palette = THEMES["claro"]

    return palette.get(
        name,
        name,
    )


def configure_fonts(root=None) -> str:
    """Selecciona una fuente instalada y la aplica a los widgets Tk."""
    global FONT_FAMILY, FONTS, _FONT_ROOT_ID

    root = root or getattr(tk, "_default_root", None)
    if root is None:
        return FONT_FAMILY

    try:
        available = {name.casefold(): name for name in tkfont.families(root)}
    except (tk.TclError, RuntimeError):
        available = {}

    selected = next(
        (available[name.casefold()] for name in _FONT_CANDIDATES if name.casefold() in available),
        None,
    )
    if selected is None:
        try:
            selected = tkfont.nametofont("TkDefaultFont", root=root).actual("family")
        except (tk.TclError, RuntimeError):
            selected = "DejaVu Sans"

    FONT_FAMILY = selected
    FONTS = {role: (selected, *spec[1:]) for role, spec in FONTS.items()}

    for name in (
        "TkDefaultFont", "TkTextFont", "TkFixedFont", "TkMenuFont",
        "TkHeadingFont", "TkCaptionFont", "TkSmallCaptionFont",
        "TkIconFont", "TkTooltipFont",
    ):
        try:
            tkfont.nametofont(name, root=root).configure(family=selected)
        except (tk.TclError, RuntimeError):
            pass

    _FONT_ROOT_ID = str(root)
    return selected


def font(role: str = "default"):
    root = getattr(tk, "_default_root", None)
    if root is not None and _FONT_ROOT_ID != str(root):
        configure_fonts(root)
    return FONTS.get(role, FONTS["default"])


def role_colors(
    role: str = "plain",
) -> Dict[str, str]:
    spec = ROLES.get(
        role,
        ROLES["plain"],
    )

    return {key: color(value) for key, value in spec.items()}


def button_palette(
    variant: str = "primary",
) -> Dict[str, str]:
    spec = BUTTON_VARIANTS.get(
        variant,
        BUTTON_VARIANTS["primary"],
    )

    return {key: color(value) for key, value in spec.items()}


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
    repintado global.
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


def _safe_configure(
    widget,
    **kwargs,
):
    """
    Configura propiedades individualmente para evitar
    que una propiedad no compatible rompa todo el repaint.
    """
    for key, value in kwargs.items():
        if value is None:
            continue

        try:
            widget.configure(**{key: value})
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
        window.geometry(f"{width}x{height}")

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

        window.geometry(f"{width}x{height}+{x}+{y}")

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
            return f"{int(geometry[0])}" f"x" f"{int(geometry[1])}"

    return str(geometry)


# ============================================================
# VENTANAS TOPLEVEL
# ============================================================


def prepare_toplevel(
    window,
    title="",
    geometry=None,
    base_path=None,
    resizable=(True, True),
    modal=False,
):
    """
    Configura una ventana secundaria Toplevel existente.
    """
    if title:
        window.title(title)

    normalized = _normalize_geometry(geometry)

    if normalized:
        window.geometry(normalized)

    # --------------------------------------------------------
    # Icono
    # --------------------------------------------------------

    if base_path is not None:
        try:
            set_app_icon(
                window,
                base_path,
            )
        except Exception:
            pass

    # --------------------------------------------------------
    # Redimensionamiento
    # --------------------------------------------------------

    try:
        window.resizable(
            *resizable,
        )
    except Exception:
        pass

    # --------------------------------------------------------
    # Centrar ventana
    # --------------------------------------------------------

    try:
        if (
            isinstance(
                geometry,
                (tuple, list),
            )
            and len(geometry) >= 2
        ):
            center_window(
                window,
                int(geometry[0]),
                int(geometry[1]),
            )
        else:
            center_window(window)
    except Exception:
        pass

    # --------------------------------------------------------
    # Modal
    # --------------------------------------------------------

    if modal:
        try:
            window.transient(
                window.master,
            )
        except Exception:
            pass

        try:
            window.grab_set()
        except Exception:
            pass

    # --------------------------------------------------------
    # Enfocar
    # --------------------------------------------------------

    try:
        window.lift()
        window.focus_force()
    except Exception:
        pass

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
    Crea un separador compatible con Tkinter/Tkinter.

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

    orient_value = "horizontal" if str(orient).lower().startswith("h") else "vertical"

    if orient_value == "horizontal":
        widget = tkui.Frame(
            parent,
            height=1,
            fg_color=color("border"),
            corner_radius=0,
            **kwargs,
        )

        default_fill = "x"

    else:
        widget = tkui.Frame(
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
    Reaplica el tema claro a un widget registrado.
    """

    if widget is None:
        return

    try:
        # ----------------------------------------------------
        # TKINTER - LABEL
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.Label,
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

        # ----------------------------------------------------
        # TKINTER - BUTTON
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.Button,
        ):
            variant = spec.get(
                "variant",
                "primary",
            )

            palette = button_palette(variant)

            _safe_configure(
                widget,
                fg_color=palette["bg"],
                hover_color=palette["hover"],
                text_color=palette["fg"],
            )

            return

        # ----------------------------------------------------
        # TKINTER - ENTRY
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.Entry,
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
                placeholder_text_color=color("text_muted"),
            )

            return

        # ----------------------------------------------------
        # TKINTER - COMBOBOX
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.ComboBox,
        ):
            _safe_configure(
                widget,
                fg_color=color("entry_bg"),
                border_color=color("entry_border"),
                button_color=color("accent"),
                button_hover_color=color("accent_dark"),
                text_color=color("text"),
            )

            return

        # ----------------------------------------------------
        # TKINTER - CHECKBOX
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.CheckBox,
        ):
            _safe_configure(
                widget,
                fg_color=color("accent"),
                hover_color=color("accent_hover"),
                border_color=color("entry_border"),
                text_color=color("text"),
            )

            return

        # ----------------------------------------------------
        # TKINTER - SWITCH
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.Switch,
        ):
            _safe_configure(
                widget,
                progress_color=color("accent"),
                button_color=color("surface"),
                button_hover_color=color("accent_hover"),
                text_color=color("text"),
            )

            return

        # ----------------------------------------------------
        # TKINTER - SLIDER
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.Slider,
        ):
            _safe_configure(
                widget,
                progress_color=color("accent"),
                button_color=color("accent"),
                button_hover_color=color("accent_hover"),
                fg_color=color("surface_alt"),
            )

            return

        # ----------------------------------------------------
        # TKINTER - PROGRESS BAR
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.ProgressBar,
        ):
            _safe_configure(
                widget,
                progress_color=color("accent"),
                fg_color=color("surface_alt"),
            )

            return

        # ----------------------------------------------------
        # TKINTER - SCROLLBAR
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.Scrollbar,
        ):
            _safe_configure(
                widget,
                fg_color=color("scroll_trough"),
                button_color=color("scroll_thumb"),
                button_hover_color=color("scroll_hover"),
            )

            return

        # ----------------------------------------------------
        # TKINTER - TABVIEW
        #
        # El Tabview utiliza el mismo lenguaje visual
        # que las Cards de KLP SYSTEM.
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.Tabview,
        ):
            _safe_configure(
                widget,
                fg_color=color("card"),
                border_width=1,
                border_color=color("border"),
                corner_radius=14,
                segmented_button_fg_color=color("card"),
                segmented_button_selected_color=color("accent"),
                segmented_button_selected_hover_color=color("accent_hover"),
                segmented_button_unselected_color=color("surface_alt"),
                segmented_button_unselected_hover_color=color("card_hover"),
                text_color=color("text"),
            )

            return

        # ----------------------------------------------------
        # TKINTER - SCROLLABLE FRAME
        #
        # IMPORTANTE:
        # Este bloque debe estar ANTES del Frame genérico,
        # porque ScrollableFrame hereda de Frame.
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.ScrollableFrame,
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

        # ----------------------------------------------------
        # TKINTER - FRAME
        #
        # Este debe ser el último widget Frame,
        # porque muchos componentes de Tkinter
        # heredan de Frame.
        # ----------------------------------------------------

        if isinstance(
            widget,
            tkui.Frame,
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

        # ----------------------------------------------------
        # TKINTER CLÁSICO
        # ----------------------------------------------------

        if kind == "separator":
            _safe_configure(
                widget,
                fg_color=color("border"),
            )

            return

        # ----------------------------------------------------
        # BADGE
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # CARD TKINTER
        # ----------------------------------------------------

        if kind == "card":
            _safe_configure(
                widget,
                bg=color(
                    spec.get(
                        "bg",
                        "card",
                    )
                ),
                highlightbackground=color("border"),
                highlightcolor=color("border"),
            )

            return

        # ----------------------------------------------------
        # ROLES TKINTER
        # ----------------------------------------------------

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
                bg=color(bg_name),
            )

            _safe_configure(
                widget,
                fg=color(fg_name),
            )

            if "font" in spec:
                _safe_configure(
                    widget,
                    font=font(spec["font"]),
                )

            return

        # ----------------------------------------------------
        # TREEVIEW
        # ----------------------------------------------------

        if kind == "treeview":
            _safe_configure(
                widget,
                background=color("surface"),
                foreground=color("text"),
                fieldbackground=color("surface"),
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
            style.theme_use("clam")
        except tk.TclError:
            pass

        # ----------------------------------------------------
        # TREEVIEW
        # ----------------------------------------------------

        style.configure(
            "KLP.Treeview",
            background=color("surface"),
            foreground=color("text"),
            fieldbackground=color("surface"),
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

        # ----------------------------------------------------
        # TREEVIEW HEADING
        # ----------------------------------------------------

        style.configure(
            "KLP.Treeview.Heading",
            background=color("surface_alt"),
            foreground=color("text"),
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

        # ----------------------------------------------------
        # SEPARATOR
        # ----------------------------------------------------

        style.configure(
            "KLP.TSeparator",
            background=color("border"),
        )

        # ----------------------------------------------------
        # NOTEBOOK CLÁSICO
        #
        # Se conserva por compatibilidad con cualquier parte
        # antigua de la aplicación.
        # ----------------------------------------------------

        style.configure(
            "KLP.TNotebook",
            background=color("window"),
            borderwidth=0,
        )

        style.configure(
            "KLP.TNotebook.Tab",
            background=color("surface_alt"),
            foreground=color("text_muted"),
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
                    color("text_on_accent"),
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
            "fg_color": color("entry_bg"),
            "border_color": color("entry_border"),
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

    for widget, data in list(_REGISTRY.items()):
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
    Actualiza propiedades de un widget y reaplica
    el tema claro.
    """
    if root is not None and changes:
        try:
            root.configure(**changes)
        except tk.TclError:
            for key, value in changes.items():
                try:
                    root.configure(**{key: value})
                except tk.TclError:
                    pass

    configure_app_style()
    _update_input_style()
    repaint_all()


# ============================================================
# APLICAR TEMA
# ============================================================


def apply_theme(name: str = "claro"):
    """
    Aplica el único tema disponible de KLP SYSTEM.

    El argumento ``name`` se mantiene únicamente por
    compatibilidad con código existente.

    La aplicación siempre utiliza el tema claro.
    """
    global _current_theme

    _current_theme = "claro"

    _refresh_colors_reference()
    _update_input_style()

    # Fuerza Tkinter a utilizar el estilo claro.
    tkui.set_appearance_mode("Light")

    configure_app_style()
    repaint_all()


# ============================================================
# THEME MANAGER
# ============================================================


class ThemeManager:
    """
    Administrador del tema global de KLP SYSTEM.

    KLP SYSTEM utiliza exclusivamente el tema claro.
    """

    def __init__(
        self,
        root=None,
        theme: Optional[str] = None,
    ):
        global _manager

        self.root = root
        self.theme = "claro"

        _manager = self

        apply_theme("claro")

    def set_theme(
        self,
        name: str = "claro",
    ):
        """
        Mantiene KLP SYSTEM en tema claro.

        ``name`` se acepta por compatibilidad, pero
        cualquier valor termina usando ``claro``.
        """
        self.theme = "claro"
        apply_theme("claro")

    def toggle(self):
        """
        Mantiene el tema claro.

        No existe un segundo tema para alternar.
        """
        self.theme = "claro"
        apply_theme("claro")

    def is_dark(self):
        return False

    def colors(self):
        return THEMES["claro"]


# ============================================================
# ICONO
# ============================================================


def set_app_icon(
    window,
    base_path=None,
):
    """
    Configura el icono de la aplicación.

    Primero intenta PNG para Tkinter/Tkinter
    y luego ICO.

    Las imágenes PNG quedan retenidas mientras la
    ventana existe y se liberan cuando se destruye.
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
            # ------------------------------------------------
            # PNG
            # ------------------------------------------------

            if path.lower().endswith(".png"):
                image = tk.PhotoImage(file=path)

                window_key = str(window)

                ICON_IMAGES[window_key] = image

                window.iconphoto(
                    True,
                    image,
                )

                def _release_icon(
                    key=window_key,
                ):
                    ICON_IMAGES.pop(
                        key,
                        None,
                    )

                try:
                    window.bind(
                        "<Destroy>",
                        lambda event: _release_icon(),
                        add="+",
                    )
                except (
                    tk.TclError,
                    AttributeError,
                ):
                    pass

                return

            # ------------------------------------------------
            # ICO
            # ------------------------------------------------

            if path.lower().endswith(".ico"):
                window.iconbitmap(path)
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
    Tooltip ligero para widgets Tkinter/Tkinter.
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
            self.after_id = self.widget.after(
                self.delay,
                self._show,
            )
        except tk.TclError:
            pass

    def _show(self):
        self.after_id = None

        try:
            if not self.widget.winfo_exists():
                return

            x = self.widget.winfo_rootx() + 10

            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

            self.tipwindow = tk.Toplevel(self.widget)

            self.tipwindow.wm_overrideredirect(True)

            self.tipwindow.geometry(f"+{x}+{y}")

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
                self.widget.after_cancel(self.after_id)
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
# COMPATIBILIDAD CON CÓDIGO ANTIGUO
# ============================================================


def detect_system_theme() -> str:
    """
    Compatibilidad con código anterior.

    KLP SYSTEM ya no detecta el tema del sistema.
    Siempre devuelve ``claro``.
    """
    return "claro"


def system_theme_info():
    """
    Devuelve información del tema actual.

    Se conserva por compatibilidad, pero ya no consulta
    el tema de Kali, XFCE, GTK ni ninguna configuración
    externa.
    """
    return {
        "detected": "claro",
        "current": "claro",
        "available": ["claro"],
        "is_dark": False,
    }


# ============================================================
# CONFIGURACIÓN INICIAL
# ============================================================

# Fuerza Tkinter a utilizar siempre el modo claro.
tkui.set_appearance_mode("Dark")

_refresh_colors_reference()
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
