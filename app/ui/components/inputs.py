"""
Campos de entrada de KLP SYSTEM.

Componentes reutilizables construidos con CustomTkinter:
- CTkEntry
- CTkLabel
- CTkComboBox
- CTkCheckBox
- CTkFrame
- AppButton

Se mantiene el nombre histórico ``inputs.py`` para evitar tener que modificar
todos los imports existentes del proyecto.
"""

from __future__ import annotations

import tkinter as tk
from typing import Any, Callable, Optional, Sequence, Tuple

from app.ui import tk_compat as ctk

from app.ui import theme
from app.ui.components.buttons import AppButton
from app.ui.styles import Colors, Fonts


# ============================================================================
# ENTRY
# ============================================================================

def make_entry(
    parent: Any,
    textvariable: Optional[tk.Variable] = None,
    width: Optional[int] = None,
    show: Optional[str] = None,
    justify: str = "left",
    state: str = "normal",
    font_role: str = "body",
    tooltip: Optional[str] = None,
    expand: bool = False,
    **kwargs: Any,
) -> ctk.CTkEntry:
    """
    Crea un campo de entrada CustomTkinter.

    Args:
        width:
            Ancho inicial/preferido del campo.

        expand:
            Indica que el campo está pensado para expandirse dentro
            de su contenedor mediante grid sticky="ew".
    """
    if "placeholder" in kwargs and "placeholder_text" not in kwargs:
        kwargs["placeholder_text"] = kwargs.pop("placeholder")

    entry_kwargs: dict[str, Any] = {
        "height": kwargs.pop("height", 36),
        "corner_radius": kwargs.pop("corner_radius", 7),
        "border_width": kwargs.pop("border_width", 1),
        "fg_color": kwargs.pop("fg_color", Colors.INPUT),
        "border_color": kwargs.pop("border_color", Colors.BORDER),
        "text_color": kwargs.pop("text_color", Colors.TEXT),
        "placeholder_text": kwargs.pop("placeholder_text", None),
        "justify": justify,
        "font": theme.font(font_role),
    }

    if width is not None:
        entry_kwargs["width"] = width

    if show is not None:
        entry_kwargs["show"] = show

    if state == "disabled":
        entry_kwargs["state"] = "disabled"
    elif state == "readonly":
        entry_kwargs["state"] = "disabled"
    else:
        entry_kwargs["state"] = state

    entry_kwargs.update(kwargs)

    entry = ctk.CTkEntry(
        parent,
        **entry_kwargs,
    )

    if textvariable is not None:
        try:
            entry.configure(
                textvariable=textvariable,
            )
        except Exception:
            entry._textvariable = textvariable  # type: ignore[attr-defined]

    theme.remember(
        entry,
        "entry",
        font=theme.font(font_role),
    )

    if tooltip:
        theme.Tooltip(entry, tooltip)

    return entry

# ============================================================================
# SEARCH ENTRY
# ============================================================================

def make_search_entry(
    parent: Any,
    textvariable: Optional[tk.Variable] = None,
    placeholder_text: Optional[str] = "Buscar...",
    row: Optional[int] = None,
    column: Optional[int] = None,
    width: Optional[int] = None,
    padx: int = 0,
    pady: int = 0,
    **kwargs: Any,
) -> ctk.CTkEntry:
    """
    Crea un campo de búsqueda adaptable.

    Está pensado para barras de búsqueda y filtros que deben
    aprovechar el espacio disponible del contenedor.
    """

    entry = make_entry(
        parent,
        textvariable=textvariable,
        width=width,
        placeholder_text=placeholder_text,
        **kwargs,
    )

    if row is not None and column is not None:

        try:
            parent.grid_columnconfigure(
                column,
                weight=1,
            )
        except (AttributeError, tk.TclError):
            pass

        entry.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=padx,
            pady=pady,
        )

    return entry

# ============================================================================
# LABEL
# ============================================================================

def _caption(
    parent: Any,
    text: str,
    row: int,
    column: int,
    background: str,
    sticky: str,
    padx: int,
    pady: int,
) -> ctk.CTkLabel:
    """
    Crea una etiqueta de formulario usando CustomTkinter.
    """

    anchor = {
        "e": "e",
        "w": "w",
        "center": "center",
        "n": "n",
        "s": "s",
        "ne": "ne",
        "nw": "nw",
        "se": "se",
        "sw": "sw",
    }.get(sticky, "w")

    caption = ctk.CTkLabel(
        parent,
        text=text,
        font=theme.font("body_bold"),
        anchor=anchor,
        text_color=Colors.TEXT,
        fg_color="transparent",
    )

    theme.remember(
        caption,
        "label",
        bg=background,
        fg="text",
    )

    caption.grid(
        row=row,
        column=column,
        sticky=sticky,
        padx=(padx, 4),
        pady=pady,
    )

    return caption


# ============================================================================
# LABELED ENTRY
# ============================================================================

def labeled_entry(
    parent: Any,
    text: str,
    textvariable: Optional[tk.Variable] = None,
    width: Optional[int] = None,
    show: Optional[str] = None,
    row: int = 0,
    column: int = 0,
    label_column: Optional[int] = None,
    entry_column: Optional[int] = None,
    label_sticky: str = "e",
    entry_sticky: str = "ew",
    padx: int = 8,
    pady: int = 5,
    background: str = "surface",
    expand: bool = True,
    **kwargs: Any,
) -> Tuple[ctk.CTkLabel, ctk.CTkEntry]:
    """
    Crea una etiqueta y un campo de entrada en una misma fila.

    Por defecto, el campo ocupa el espacio horizontal disponible.
    """

    caption_column = (
        column
        if label_column is None
        else label_column
    )

    field_column = (
        caption_column + 1
        if entry_column is None
        else entry_column
    )

    # ------------------------------------------------------------
    # Configuración de columnas
    # ------------------------------------------------------------

    try:
        # La columna del label mantiene su tamaño natural.
        parent.grid_columnconfigure(
            caption_column,
            weight=0,
        )

        # La columna del input absorbe el espacio disponible.
        parent.grid_columnconfigure(
            field_column,
            weight=1 if expand else 0,
        )
    except (AttributeError, tk.TclError):
        pass

    # ------------------------------------------------------------
    # Label
    # ------------------------------------------------------------

    caption = _caption(
        parent,
        text,
        row,
        caption_column,
        background,
        label_sticky,
        padx,
        pady,
    )

    # ------------------------------------------------------------
    # Entry
    # ------------------------------------------------------------

    entry = make_entry(
        parent,
        textvariable=textvariable,
        width=width,
        show=show,
        expand=expand,
        **kwargs,
    )

    entry.grid(
        row=row,
        column=field_column,
        sticky="ew" if expand else entry_sticky,
        padx=(0, padx),
        pady=pady,
    )

    return caption, entry


# ============================================================================
# COMBOBOX
# ============================================================================

def labeled_combobox(
    parent: Any,
    text: str,
    values: Sequence[Any] = (),
    textvariable: Optional[tk.Variable] = None,
    width: Optional[int] = None,
    state: str = "readonly",
    on_select: Optional[Callable[[Any], Any]] = None,
    row: int = 0,
    column: int = 0,
    label_column: Optional[int] = None,
    entry_column: Optional[int] = None,
    label_sticky: str = "e",
    entry_sticky: str = "ew",
    padx: int = 8,
    pady: int = 5,
    background: str = "surface",
    **kwargs: Any,
) -> Tuple[ctk.CTkLabel, ctk.CTkComboBox]:
    """
    Crea una etiqueta y un CTkComboBox en una misma fila.

    Devuelve:
        (label, combobox)
    """

    caption_column = (
        column
        if label_column is None
        else label_column
    )

    field_column = (
        caption_column + 1
        if entry_column is None
        else entry_column
    )

    caption = _caption(
        parent,
        text,
        row,
        caption_column,
        background,
        label_sticky,
        padx,
        pady,
    )

    combo = make_combobox(
        parent,
        values=values,
        textvariable=textvariable,
        width=width,
        state=state,
        on_select=on_select,
        **kwargs,
    )

    combo.grid(
        row=row,
        column=field_column,
        sticky=entry_sticky,
        padx=(0, padx),
        pady=pady,
    )

    return caption, combo


def make_combobox(
    parent: Any,
    values: Sequence[Any] = (),
    textvariable: Optional[tk.Variable] = None,
    width: Optional[int] = None,
    state: str = "readonly",
    on_select: Optional[Callable[[Any], Any]] = None,
    tooltip: Optional[str] = None,
    **kwargs: Any,
) -> ctk.CTkComboBox:
    """
    Crea un CTkComboBox estilizado.

    ``on_select`` recibe el evento de selección.
    """

    combo_kwargs: dict[str, Any] = {
        "values": [str(value) for value in values],
        "height": kwargs.pop("height", 36),
        "corner_radius": kwargs.pop("corner_radius", 7),
        "border_width": kwargs.pop("border_width", 1),
        "fg_color": kwargs.pop("fg_color", Colors.INPUT),
        "border_color": kwargs.pop("border_color", Colors.BORDER),
        "button_color": kwargs.pop(
            "button_color",
            Colors.SECONDARY,
        ),
        "button_hover_color": kwargs.pop(
            "button_hover_color",
            Colors.SECONDARY_HOVER,
        ),
        "dropdown_fg_color": kwargs.pop(
            "dropdown_fg_color",
            Colors.SURFACE,
        ),
        "dropdown_hover_color": kwargs.pop(
            "dropdown_hover_color",
            Colors.SURFACE_HOVER,
        ),
        "text_color": kwargs.pop(
            "text_color",
            Colors.TEXT,
        ),
        "dropdown_text_color": kwargs.pop(
            "dropdown_text_color",
            Colors.TEXT,
        ),
        "font": kwargs.pop(
            "font",
            theme.font("body"),
        ),
    }

    if width is not None:
        combo_kwargs["width"] = width

    # CustomTkinter utiliza command en lugar de bind.
    if on_select is not None:
        combo_kwargs["command"] = on_select

    combo_kwargs.update(kwargs)

    combo = ctk.CTkComboBox(
        parent,
        **combo_kwargs,
    )

    # Establecer valor inicial desde StringVar.
    if textvariable is not None:
        try:
            combo.configure(
                variable=textvariable,
            )
        except Exception:
            # Algunas versiones de CTkComboBox no exponen variable
            # de la misma forma.
            try:
                combo.set(textvariable.get())
            except Exception:
                pass

    # readonly es el comportamiento natural de CTkComboBox.
    if state == "disabled":
        combo.configure(state="disabled")

    if tooltip:
        theme.Tooltip(combo, tooltip)

    return combo


# ============================================================================
# CHECKBOX
# ============================================================================

def make_checkbutton(
    parent: Any,
    text: str,
    variable: tk.Variable,
    command: Optional[Callable[[], Any]] = None,
    background: str = "surface",
    font_role: str = "body",
    **kwargs: Any,
) -> ctk.CTkCheckBox:
    """
    Crea una casilla de verificación CustomTkinter.
    """

    checkbox_kwargs: dict[str, Any] = {
        "text": text,
        "variable": variable,
        "font": theme.font(font_role),
        "text_color": Colors.TEXT,
        "fg_color": kwargs.pop(
            "fg_color",
            Colors.PRIMARY,
        ),
        "hover_color": kwargs.pop(
            "hover_color",
            Colors.PRIMARY_HOVER,
        ),
        "border_color": kwargs.pop(
            "border_color",
            Colors.BORDER_LIGHT,
        ),
        "corner_radius": kwargs.pop(
            "corner_radius",
            5,
        ),
        "border_width": kwargs.pop(
            "border_width",
            1,
        ),
    }

    if command is not None:
        checkbox_kwargs["command"] = command

    checkbox_kwargs.update(kwargs)

    checkbox = ctk.CTkCheckBox(
        parent,
        **checkbox_kwargs,
    )

    theme.remember(
        checkbox,
        "checkbutton",
        bg=background,
        font=theme.font(font_role),
    )

    return checkbox


# ============================================================================
# PASSWORD FIELD
# ============================================================================

class PasswordField(ctk.CTkFrame):
    """
    Campo de contraseña reutilizable.

    Incluye:
    - CTkEntry
    - AppButton
    - Mostrar / ocultar contraseña
    """

    def __init__(
        self,
        parent: Any,
        textvariable: Optional[tk.StringVar] = None,
        width: Optional[int] = None,
        background: str = "surface",
        show_button: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )

        theme.remember(
            self,
            "plain",
            bg=background,
            fg="text",
        )

        self.var = (
            textvariable
            if textvariable is not None
            else tk.StringVar()
        )

        self.entry = make_entry(
            self,
            textvariable=self.var,
            width=width,
            show="•",
            **kwargs,
        )

        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
        )

        self._visible = False

        self.toggle_button: Optional[AppButton] = None

        if show_button:
            self.toggle_button = AppButton(
                self,
                text="Ver",
                command=self.toggle_visibility,
                variant="ghost",
                font_role="small_bold",
                width=70,
                tooltip="Mostrar u ocultar la contraseña",
            )

            self.toggle_button.pack(
                side="left",
                padx=(6, 0),
            )

    def toggle_visibility(self) -> None:
        """Alterna entre mostrar y ocultar la contraseña."""

        self._visible = not self._visible

        self.entry.configure(
            show="" if self._visible else "•",
        )

        if self.toggle_button is not None:
            self.toggle_button.configure(
                text="Ocultar" if self._visible else "Ver",
            )

    def get(self) -> str:
        """Devuelve el valor actual del campo."""

        return self.var.get()

    def set(self, value: str) -> None:
        """Establece el valor del campo."""

        self.var.set(value)

    def focus_set(self) -> None:  # type: ignore[override]
        """Enfoca directamente el CTkEntry interno."""

        self.entry.focus_set()