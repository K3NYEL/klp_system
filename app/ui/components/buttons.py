"""
Botones reutilizables de KLP SYSTEM.

Todos los botones utilizan Tkinter.
No se utiliza tk.Button.
"""

from __future__ import annotations

from typing import Callable

from app.ui import tk_widgets as tkui

from app.ui import theme


# ============================================================
# TOOLTIP
# ============================================================


class ButtonTooltip:
    """Tooltip sencillo para botones de KLP SYSTEM."""

    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip_window = None

        self.widget.bind(
            "<Enter>",
            self._show,
            add="+",
        )

        self.widget.bind(
            "<Leave>",
            self._hide,
            add="+",
        )

    def _show(self, _event=None):
        if self.tip_window is not None:
            return

        if not self.text:
            return

        try:
            x = self.widget.winfo_rootx()
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

            self.tip_window = tkui.Toplevel(self.widget)

            self.tip_window.overrideredirect(True)
            self.tip_window.attributes("-topmost", True)
            self.tip_window.geometry(f"+{x}+{y}")

            label = tkui.Label(
                self.tip_window,
                text=self.text,
                fg_color=theme.color("card"),
                text_color=theme.color("text_muted"),
                corner_radius=6,
                font=theme.font("small"),
                padx=8,
                pady=5,
            )

            label.pack()

        except Exception:
            self.tip_window = None

    def _hide(self, _event=None):
        if self.tip_window is not None:
            try:
                self.tip_window.destroy()
            except Exception:
                pass

            self.tip_window = None


# ============================================================
# APP BUTTON
# ============================================================


class AppButton(tkui.Button):
    """
    Botón estándar de KLP SYSTEM.

    Variantes:
        primary
        secondary
        neutral
        success
        danger
        warning
        info
        outline
        ghost

    Tamaños:
        small
        medium
        large
        full
    """

    VARIANTS = {
        "primary",
        "secondary",
        "neutral",
        "success",
        "danger",
        "warning",
        "info",
        "outline",
        "ghost",
    }

    SIZES = {
        "small": {
            "width": 100,
            "height": 32,
            "corner_radius": 7,
        },
        "medium": {
            "width": 130,
            "height": 38,
            "corner_radius": 8,
        },
        "large": {
            "width": 160,
            "height": 44,
            "corner_radius": 9,
        },
        "full": {
            "height": 42,
            "corner_radius": 8,
        },
    }

    # ========================================================
    # VARIANT CONFIG
    # ========================================================

    @staticmethod
    def _variant_config(variant: str) -> dict:
        """
        Obtiene la configuración visual de una variante
        utilizando exclusivamente el sistema dinámico de theme.py.
        """

        if variant == "primary":
            return {
                "fg_color": theme.color("accent"),
                "hover_color": theme.color("accent_hover"),
                "text_color": theme.color("text_on_accent"),
                "border_width": 0,
                "border_color": theme.color("accent"),
            }

        if variant in {"secondary", "neutral"}:
            return {
                "fg_color": theme.color("neutral"),
                "hover_color": theme.color("neutral_dark"),
                "text_color": theme.color("text"),
                "border_width": 0,
                "border_color": theme.color("neutral"),
            }

        if variant == "success":
            return {
                "fg_color": theme.color("success"),
                "hover_color": theme.color("success_dark"),
                "text_color": theme.color("text_on_accent"),
                "border_width": 0,
                "border_color": theme.color("success"),
            }

        if variant == "danger":
            return {
                "fg_color": theme.color("danger"),
                "hover_color": theme.color("danger_dark"),
                "text_color": theme.color("text_on_accent"),
                "border_width": 0,
                "border_color": theme.color("danger"),
            }

        if variant == "warning":
            return {
                "fg_color": theme.color("warning"),
                "hover_color": theme.color("warning_dark"),
                "text_color": theme.color("text_on_accent"),
                "border_width": 0,
                "border_color": theme.color("warning"),
            }

        if variant == "info":
            return {
                "fg_color": theme.color("info"),
                "hover_color": theme.color("info_dark"),
                "text_color": theme.color("text_on_accent"),
                "border_width": 0,
                "border_color": theme.color("info"),
            }

        if variant == "outline":
            return {
                "fg_color": "transparent",
                "hover_color": theme.color("surface_alt"),
                "text_color": theme.color("text"),
                "border_width": 1,
                "border_color": theme.color("border_light"),
            }

        if variant == "ghost":
            return {
                "fg_color": "transparent",
                "hover_color": theme.color("surface_alt"),
                "text_color": theme.color("text_muted"),
                "border_width": 0,
                "border_color": theme.color("border"),
            }

        raise ValueError(
            f"Variante desconocida: '{variant}'. "
            f"Disponibles: {', '.join(sorted(AppButton.VARIANTS))}"
        )

    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(
        self,
        master,
        text: str = "",
        command: Callable | None = None,
        variant: str = "primary",
        size: str = "medium",
        icon: str | None = None,
        font_role: str | None = None,
        tooltip: str | None = None,
        padx: int | None = None,
        pady: int | None = None,
        **kwargs,
    ):
        """
        Crea un botón reutilizable de KLP SYSTEM.
        """

        # ----------------------------------------------------
        # Validar variante
        # ----------------------------------------------------

        variant = variant.lower()

        if variant not in self.VARIANTS:
            raise ValueError(
                f"Variante desconocida: '{variant}'. "
                f"Disponibles: {', '.join(sorted(self.VARIANTS))}"
            )

        # ----------------------------------------------------
        # Validar tamaño
        # ----------------------------------------------------

        size = size.lower()

        if size not in self.SIZES:
            raise ValueError(
                f"Tamaño desconocido: '{size}'. "
                f"Disponibles: {', '.join(sorted(self.SIZES))}"
            )

        size_config = self.SIZES[size]

        # ----------------------------------------------------
        # Fuente
        # ----------------------------------------------------

        if font_role:
            font = theme.font(font_role)
        else:
            font = theme.font("button")

        # ----------------------------------------------------
        # Icono
        # ----------------------------------------------------

        if icon:
            text = f"{icon}  {text}"

        # ----------------------------------------------------
        # Variante
        # ----------------------------------------------------

        variant_config = self._variant_config(variant)

        # ----------------------------------------------------
        # Configuración base
        # ----------------------------------------------------

        config = {
            "text": text,
            "command": command,

            "fg_color": variant_config["fg_color"],
            "hover_color": variant_config["hover_color"],
            "text_color": variant_config["text_color"],

            "border_width": variant_config["border_width"],
            "border_color": variant_config["border_color"],

            "font": font,

            "height": size_config["height"],
            "corner_radius": size_config["corner_radius"],

            "cursor": "hand2",
        }

        # ----------------------------------------------------
        # Width
        # ----------------------------------------------------

        if size != "full":
            config["width"] = size_config["width"]

        # ----------------------------------------------------
        # kwargs tiene prioridad
        # ----------------------------------------------------

        config.update(kwargs)

        # ----------------------------------------------------
        # Crear Button
        # ----------------------------------------------------

        super().__init__(
            master,
            **config,
        )

        # ----------------------------------------------------
        # Padding
        # ----------------------------------------------------

        self._button_padx = padx
        self._button_pady = pady

        # ----------------------------------------------------
        # Tooltip
        # ----------------------------------------------------

        self._tooltip = None

        if tooltip:
            self._tooltip = ButtonTooltip(
                self,
                tooltip,
            )

        # ----------------------------------------------------
        # Estado
        # ----------------------------------------------------

        self._normal_text = text

    # ========================================================
    # ENABLE / DISABLE
    # ========================================================

    def set_enabled(
        self,
        enabled: bool = True,
    ) -> None:
        """
        Activa o desactiva el botón.
        """

        if enabled:
            self.configure(
                state="normal",
                text_color=theme.color("text_on_accent"),
            )
        else:
            self.configure(
                state="disabled",
                text_color=theme.color("text_disabled"),
            )

    # ========================================================
    # LOADING
    # ========================================================

    def set_loading(
        self,
        loading: bool = True,
        loading_text: str = "Cargando...",
    ) -> None:
        """
        Cambia temporalmente el botón a estado de carga.
        """

        if loading:
            if not hasattr(self, "_normal_text"):
                self._normal_text = self.cget("text")

            self.configure(
                text=loading_text,
                state="disabled",
            )

        else:
            original_text = getattr(
                self,
                "_normal_text",
                self.cget("text"),
            )

            self.configure(
                text=original_text,
                state="normal",
            )