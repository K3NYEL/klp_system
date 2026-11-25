from __future__ import annotations

from typing import Callable, Optional

from app.ui import tk_compat as ctk

from app.ui import theme


# ============================================================
# CONFIGURACIÓN VISUAL
# ============================================================

CARD_RADIUS = 12
CARD_BORDER_WIDTH = 1
DEFAULT_PADDING = 16


# ============================================================
# LABEL
# ============================================================


def label(
    parent,
    text="",
    font_role="body",
    text_color=None,
    background=None,
    tone=None,
    **kwargs,
):
    """
    Crea un CTkLabel compatible con las llamadas antiguas del proyecto.

    Soporta:
        - font_role="body"
        - text_color="text"
        - background="surface"
        - tone="warning", "danger", "success", etc.
    """

    # ---------------------------------------------------------
    # Resolver tone
    # ---------------------------------------------------------

    if tone is not None:
        resolved_tone = theme.TONE_ALIASES.get(tone, tone)

        # tone solo establece el color si no se especificó
        # text_color explícitamente.
        if text_color is None:
            text_color = resolved_tone

    if text_color is None:
        text_color = "text"

    if background is None:
        background = "transparent"

    # ---------------------------------------------------------
    # Resolver colores
    # ---------------------------------------------------------

    if background == "transparent":
        fg_color = "transparent"
    else:
        fg_color = theme.color(background)

    # ---------------------------------------------------------
    # Compatibilidad con Tkinter clásico
    # ---------------------------------------------------------

    kwargs.pop("padx", None)
    kwargs.pop("pady", None)

    # Algunos lugares antiguos pueden pasar "anchor".
    # CTkLabel sí lo soporta, así que lo dejamos.

    widget = ctk.CTkLabel(
        parent,
        text=text,
        font=theme.font(font_role),
        text_color=theme.color(text_color),
        fg_color=fg_color,
        **kwargs,
    )

    # ---------------------------------------------------------
    # Registrar para que el tema pueda actualizarlo
    # ---------------------------------------------------------

    theme.remember(
        widget,
        "label",
        fg=text_color,
        bg=background,
        font=font_role,
    )

    return widget


# ============================================================
# CARD
# ============================================================


class Card(ctk.CTkFrame):
    """
    Card reutilizable para KLP SYSTEM.

    Soporta:

        Card(
            parent,
            title="Ventas",
            subtitle="Resumen del día",
        )
    """

    def __init__(
        self,
        parent,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        padding: int = DEFAULT_PADDING,
        background: str = "card",
        **kwargs,
    ):
        kwargs.setdefault(
            "fg_color",
            theme.color(background),
        )

        kwargs.setdefault(
            "corner_radius",
            CARD_RADIUS,
        )

        kwargs.setdefault(
            "border_width",
            CARD_BORDER_WIDTH,
        )

        kwargs.setdefault(
            "border_color",
            theme.color("border"),
        )

        super().__init__(
            parent,
            **kwargs,
        )

        self.padding = padding
        self.background = background

        theme.remember(
            self,
            "card",
            bg=background,
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        if title or subtitle:
            header = ctk.CTkFrame(
                self,
                fg_color="transparent",
            )

            header.pack(
                fill="x",
                padx=padding,
                pady=(
                    padding,
                    8,
                ),
            )

            if title:
                title_label = label(
                    header,
                    title,
                    font_role="heading",
                    background="transparent",
                )

                title_label.pack(
                    anchor="w",
                )

            if subtitle:
                subtitle_label = label(
                    header,
                    subtitle,
                    font_role="small",
                    text_color="text_muted",
                    background="transparent",
                )

                subtitle_label.pack(
                    anchor="w",
                    pady=(3, 0),
                )

            theme.remember(
                header,
                "surface",
                bg="transparent",
            )

        # ----------------------------------------------------
        # BODY
        # ----------------------------------------------------

        self.body = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        self.body.pack(
            fill="both",
            expand=True,
            padx=padding,
            pady=(
                0 if title or subtitle else padding,
                padding,
            ),
        )

        theme.remember(
            self.body,
            "surface",
            bg="transparent",
        )


# ============================================================
# METRIC CARD
# ============================================================


class MetricCard(Card):
    """
    Card para mostrar una métrica.

    Ejemplo:

        MetricCard(
            parent,
            title="Ventas",
            value="$12,450",
            subtitle="+12.4% este mes",
        )
    """

    def __init__(
        self,
        parent,
        title,
        value="—",
        subtitle=None,
        icon=None,
        tone="accent",
        **kwargs,
    ):
        super().__init__(
            parent,
            padding=18,
            **kwargs,
        )

        # Siempre existe para que set_hint() pueda usarlo.
        self.subtitle_label = None

        # Resolver alias del tono.
        resolved_tone = theme.TONE_ALIASES.get(
            tone,
            tone,
        )

        top = ctk.CTkFrame(
            self.body,
            fg_color="transparent",
        )

        top.pack(
            fill="x",
        )

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        title_label = label(
            top,
            title.upper(),
            font_role="label",
            text_color="text_muted",
            background="transparent",
        )

        title_label.pack(
            side="left",
            anchor="w",
        )

        # ----------------------------------------------------
        # ICONO
        # ----------------------------------------------------

        if icon:
            icon_label = ctk.CTkLabel(
                top,
                text=icon,
                font=(
                    theme.FONT_FAMILY,
                    18,
                ),
                text_color=theme.color(resolved_tone),
                fg_color=theme.color(
                    f"{resolved_tone}_soft"
                ),
                corner_radius=8,
                width=34,
                height=34,
            )

            icon_label.pack(
                side="right",
            )

        # ----------------------------------------------------
        # VALOR
        # ----------------------------------------------------

        value_label = ctk.CTkLabel(
            self.body,
            text=value,
            font=theme.font("metric"),
            text_color=theme.color("text"),
            fg_color="transparent",
            anchor="w",
        )

        value_label.pack(
            fill="x",
            pady=(
                12,
                2,
            ),
        )

        self.value_label = value_label

        # ----------------------------------------------------
        # SUBTÍTULO
        # ----------------------------------------------------

        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self.body,
                text=subtitle,
                font=theme.font("small"),
                text_color=theme.color("text_muted"),
                fg_color="transparent",
                anchor="w",
            )

            self.subtitle_label.pack(
                fill="x",
                pady=(2, 0),
            )

        # ----------------------------------------------------
        # TEMA
        # ----------------------------------------------------

        theme.remember(
            self,
            "card",
            bg="card",
        )

        theme.remember(
            value_label,
            "label",
            fg="text",
            bg="transparent",
            font="metric",
        )

        if self.subtitle_label is not None:
            theme.remember(
                self.subtitle_label,
                "label",
                fg="text_muted",
                bg="transparent",
                font="small",
            )

    # --------------------------------------------------------
    # ACTUALIZAR VALOR
    # --------------------------------------------------------

    def set_value(self, value):
        self.value_label.configure(
            text=value,
        )

    # --------------------------------------------------------
    # ACTUALIZAR HINT / SUBTÍTULO
    # --------------------------------------------------------

    def set_hint(self, hint):
        """
        Actualiza o crea el texto secundario de la métrica.
        """

        if self.subtitle_label is None:
            self.subtitle_label = ctk.CTkLabel(
                self.body,
                text=hint,
                font=theme.font("small"),
                text_color=theme.color("text_muted"),
                fg_color="transparent",
                anchor="w",
            )

            self.subtitle_label.pack(
                fill="x",
                pady=(2, 0),
            )

            theme.remember(
                self.subtitle_label,
                "label",
                fg="text_muted",
                bg="transparent",
                font="small",
            )

        else:
            self.subtitle_label.configure(
                text=hint,
            )


# ============================================================
# BADGE
# ============================================================


class Badge(ctk.CTkLabel):
    """
    Badge de estado.

    Ejemplo:

        Badge(
            parent,
            text="CAJA ABIERTA",
            tone="success",
        )
    """

    def __init__(
        self,
        parent,
        text: str = "",
        tone: str = "neutral",
        **kwargs,
    ):
        self.tone = tone

        resolved = theme.TONE_ALIASES.get(
            tone,
            tone,
        )

        # CTkLabel no necesita padx/pady como argumentos
        # del constructor.
        kwargs.pop("padx", None)
        kwargs.pop("pady", None)

        super().__init__(
            parent,
            text=text,
            font=theme.font("badge"),
            text_color=theme.color(resolved),
            fg_color=theme.color(
                f"{resolved}_soft"
            ),
            corner_radius=7,
            height=28,
            **kwargs,
        )

        self._theme_spec = {
            "fg": resolved,
            "bg": f"{resolved}_soft",
            "font": "badge",
        }

        theme.remember(
            self,
            "badge",
            **self._theme_spec,
        )

    def set(
        self,
        text: str,
        tone: str = "neutral",
    ):
        """
        Cambia texto y estado del Badge.
        """

        resolved = theme.TONE_ALIASES.get(
            tone,
            tone,
        )

        self.tone = tone

        self.configure(
            text=text,
            text_color=theme.color(resolved),
            fg_color=theme.color(
                f"{resolved}_soft"
            ),
        )

        self._theme_spec = {
            "fg": resolved,
            "bg": f"{resolved}_soft",
            "font": "badge",
        }

        theme.remember(
            self,
            "badge",
            **self._theme_spec,
        )


# ============================================================
# TOOLBAR
# ============================================================


class Toolbar(ctk.CTkFrame):
    """
    Barra superior reutilizable y compatible
    con las vistas antiguas.
    """

    def __init__(
        self,
        parent,
        title="",
        subtitle="",
        padding=DEFAULT_PADDING,
        **kwargs,
    ):
        self.padding = padding

        # Evitar que padding llegue a CTkFrame.
        kwargs.pop(
            "padding",
            None,
        )

        super().__init__(
            parent,
            fg_color="transparent",
            corner_radius=0,
            **kwargs,
        )

        self.columnconfigure(
            0,
            weight=1,
        )

        # -------------------------------------------------
        # CONTENIDO
        # -------------------------------------------------

        self.content = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )

        self.content.pack(
            fill="x",
            padx=self.padding,
            pady=self.padding,
        )

        self.content.columnconfigure(
            0,
            weight=1,
        )

        # -------------------------------------------------
        # CONTENEDOR IZQUIERDO
        # -------------------------------------------------

        self.left = ctk.CTkFrame(
            self.content,
            fg_color="transparent",
            corner_radius=0,
        )

        self.left.grid(
            row=0,
            column=0,
            sticky="w",
        )

        # -------------------------------------------------
        # CONTENEDOR DERECHO
        # -------------------------------------------------

        self.right = ctk.CTkFrame(
            self.content,
            fg_color="transparent",
            corner_radius=0,
        )

        self.right.grid(
            row=0,
            column=1,
            sticky="e",
            padx=(12, 0),
        )

        # Alias para código nuevo.
        self.actions = self.right

        # -------------------------------------------------
        # TÍTULO
        # -------------------------------------------------

        self.title_label = None
        self.subtitle_label = None

        if title:
            self.title_label = label(
                self.left,
                title,
                font_role="heading",
            )

            self.title_label.pack(
                anchor="w",
            )

        if subtitle:
            self.subtitle_label = label(
                self.left,
                subtitle,
                font_role="body",
                text_color="text_muted",
            )

            self.subtitle_label.pack(
                anchor="w",
                pady=(3, 0),
            )

    def add_button(
        self,
        text,
        command: Optional[Callable] = None,
        variant="primary",
        **kwargs,
    ):
        palette = theme.button_palette(
            variant
        )

        # Compatibilidad para evitar
        # argumentos duplicados.
        kwargs.pop("font", None)
        kwargs.pop("fg_color", None)
        kwargs.pop("hover_color", None)
        kwargs.pop("text_color", None)
        kwargs.pop("corner_radius", None)
        kwargs.pop("height", None)

        button = ctk.CTkButton(
            self.right,
            text=text,
            command=command,
            font=theme.font("button"),
            fg_color=palette["bg"],
            hover_color=palette["hover"],
            text_color=palette["fg"],
            corner_radius=8,
            height=36,
            **kwargs,
        )

        button.pack(
            side="left",
            padx=4,
        )

        theme.remember(
            button,
            "button",
            variant=variant,
        )

        return button


# ============================================================
# BOTÓN REUTILIZABLE
# ============================================================


class Button(ctk.CTkButton):
    """
    Botón estándar de KLP SYSTEM.

    Ejemplo:

        Button(
            parent,
            text="Guardar",
            variant="primary",
            command=guardar,
        )
    """

    def __init__(
        self,
        parent,
        text="",
        variant="primary",
        command=None,
        **kwargs,
    ):
        palette = theme.button_palette(
            variant
        )

        # Evitar argumentos duplicados.
        kwargs.pop("font", None)
        kwargs.pop("fg_color", None)
        kwargs.pop("hover_color", None)
        kwargs.pop("text_color", None)
        kwargs.pop("corner_radius", None)
        kwargs.pop("height", None)

        super().__init__(
            parent,
            text=text,
            command=command,
            font=theme.font("button"),
            fg_color=palette["bg"],
            hover_color=palette["hover"],
            text_color=palette["fg"],
            corner_radius=8,
            height=38,
            **kwargs,
        )

        self.variant = variant

        theme.remember(
            self,
            "button",
            variant=variant,
        )