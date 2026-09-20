"""
Botones reutilizables de KLP SYSTEM.

Todos los botones utilizan CustomTkinter.

No se utiliza tk.Button.
"""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from app.ui.styles import Colors, Fonts, ButtonSizes

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

            self.tip_window = ctk.CTkToplevel(self.widget)

            self.tip_window.overrideredirect(True)
            self.tip_window.attributes("-topmost", True)

            self.tip_window.geometry(f"+{x}+{y}")

            label = ctk.CTkLabel(
                self.tip_window,
                text=self.text,
                fg_color=Colors.CARD,
                text_color=Colors.TEXT_SECONDARY,
                corner_radius=6,
                font=Fonts.SMALL,
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


class AppButton(ctk.CTkButton):
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

    # ========================================================
    # VARIANTES
    # ========================================================

    VARIANTS = {
        "primary": {
            "fg_color": Colors.PRIMARY,
            "hover_color": Colors.PRIMARY_HOVER,
            "text_color": Colors.TEXT,
            "border_width": 0,
            "border_color": Colors.PRIMARY,
        },
        "secondary": {
            "fg_color": Colors.SECONDARY,
            "hover_color": Colors.SECONDARY_HOVER,
            "text_color": Colors.TEXT,
            "border_width": 0,
            "border_color": Colors.SECONDARY,
        },
        # Alias visual para el código antiguo.
        "neutral": {
            "fg_color": Colors.SECONDARY,
            "hover_color": Colors.SECONDARY_HOVER,
            "text_color": Colors.TEXT,
            "border_width": 0,
            "border_color": Colors.SECONDARY,
        },
        "success": {
            "fg_color": Colors.SUCCESS,
            "hover_color": Colors.SUCCESS_HOVER,
            "text_color": Colors.TEXT,
            "border_width": 0,
            "border_color": Colors.SUCCESS,
        },
        "danger": {
            "fg_color": Colors.DANGER,
            "hover_color": Colors.DANGER_HOVER,
            "text_color": Colors.TEXT,
            "border_width": 0,
            "border_color": Colors.DANGER,
        },
        "warning": {
            "fg_color": Colors.WARNING,
            "hover_color": Colors.WARNING_HOVER,
            "text_color": "#111111",
            "border_width": 0,
            "border_color": Colors.WARNING,
        },
        "info": {
            "fg_color": Colors.INFO,
            "hover_color": Colors.INFO_HOVER,
            "text_color": Colors.TEXT,
            "border_width": 0,
            "border_color": Colors.INFO,
        },
        "outline": {
            "fg_color": Colors.TRANSPARENT,
            "hover_color": Colors.SURFACE_HOVER,
            "text_color": Colors.TEXT,
            "border_width": 1,
            "border_color": Colors.BORDER_LIGHT,
        },
        "ghost": {
            "fg_color": Colors.TRANSPARENT,
            "hover_color": Colors.SURFACE_HOVER,
            "text_color": Colors.TEXT_SECONDARY,
            "border_width": 0,
            "border_color": Colors.BORDER,
        },
    }

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

        Args:
            master:
                Widget padre.

            text:
                Texto del botón.

            command:
                Función ejecutada al pulsar.

            variant:
                primary, secondary, neutral, success,
                danger, warning, info, outline o ghost.

            size:
                small, medium, large o full.

            icon:
                Emoji o texto corto antes del texto.

            font_role:
                Nombre de una fuente definida en Fonts.

            tooltip:
                Texto mostrado al mantener el cursor sobre
                el botón.

            padx / pady:
                Compatibilidad con el código anterior.
        """

        # ----------------------------------------------------
        # Validar variante
        # ----------------------------------------------------

        variant = variant.lower()

        if variant not in self.VARIANTS:
            raise ValueError(
                f"Variante desconocida: '{variant}'. "
                f"Disponibles: {', '.join(self.VARIANTS)}"
            )

        # ----------------------------------------------------
        # Validar tamaño
        # ----------------------------------------------------

        size = size.lower()

        valid_sizes = {
            "small",
            "medium",
            "large",
            "full",
        }

        if size not in valid_sizes:
            raise ValueError(
                f"Tamaño desconocido: '{size}'. "
                f"Disponibles: {', '.join(sorted(valid_sizes))}"
            )

        # ----------------------------------------------------
        # Configuración del tamaño
        # ----------------------------------------------------

        size_config = getattr(
            ButtonSizes,
            size.upper(),
        )

        # ----------------------------------------------------
        # Fuente
        # ----------------------------------------------------

        if font_role:

            font = getattr(
                Fonts,
                font_role.upper(),
                Fonts.BUTTON,
            )

        else:

            if size == "small":
                font = Fonts.BUTTON_SMALL

            elif size == "large":
                font = Fonts.BUTTON_LARGE

            else:
                font = Fonts.BUTTON

        # ----------------------------------------------------
        # Icono
        # ----------------------------------------------------

        if icon:
            text = f"{icon}  {text}"

        # ----------------------------------------------------
        # Configuración base
        # ----------------------------------------------------

        variant_config = self.VARIANTS[variant]

        config = {
            "text": text,
            "command": command,
            # Colores
            "fg_color": variant_config["fg_color"],
            "hover_color": variant_config["hover_color"],
            "text_color": variant_config["text_color"],
            # Borde
            "border_width": variant_config["border_width"],
            "border_color": variant_config["border_color"],
            # Fuente
            "font": font,
            # Tamaño
            "height": size_config["height"],
            "corner_radius": size_config["corner_radius"],
            # Cursor
            "cursor": "hand2",
        }

        # ----------------------------------------------------
        # Width
        # ----------------------------------------------------

        if size != "full":
            config["width"] = size_config["width"]

        # ----------------------------------------------------
        # Compatibilidad con width personalizado
        # ----------------------------------------------------

        # kwargs tiene prioridad sobre el tamaño estándar.
        config.update(kwargs)

        # ----------------------------------------------------
        # Crear CTkButton
        # ----------------------------------------------------

        super().__init__(
            master,
            **config,
        )

        # ----------------------------------------------------
        # Padding
        # ----------------------------------------------------
        #
        # CTkButton no utiliza padx/pady como padding interno
        # de la misma forma que tk.Button.
        #
        # Los aceptamos para mantener compatibilidad con
        # llamadas antiguas, pero el espacio alrededor del
        # botón debe controlarse preferentemente con pack/grid.
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
                text_color=Colors.TEXT,
            )

        else:

            self.configure(
                state="disabled",
                text_color=Colors.TEXT_DISABLED,
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

            if not hasattr(
                self,
                "_normal_text",
            ):
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
