"""
Componente de tablas de KLP SYSTEM.

DataTable utiliza un Frame como contenedor y un ttk.Treeview
internamente, ya que Tkinter no dispone de un componente
nativo equivalente a Treeview.

La API mantiene compatibilidad con las tablas existentes del sistema.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from typing import Any, Iterable, Mapping, Optional, Sequence

from app.ui import tk_widgets as tkui

from app.ui import theme
from app.ui.styles import Colors, Fonts

# ================================================================
# CONFIGURACIÓN
# ================================================================

TABLE_ROW_HEIGHT = 34
TABLE_HEADING_HEIGHT = 36

TABLE_FONT = Fonts.SMALL
TABLE_HEADING_FONT = Fonts.SMALL_BOLD

TABLE_CORNER_RADIUS = 10
TABLE_BORDER_WIDTH = 1


# ================================================================
# ESTADOS
# ================================================================

STATE_TAGS = {
    "activo": {
        "background": "#E8F4EB",
        "foreground": "#27834A",
    },
    "inactivo": {
        "background": "#FBE9E8",
        "foreground": "#A92724",
    },
    "pendiente": {
        "background": "#FBF2DF",
        "foreground": "#80520D",
    },
    "pagado": {
        "background": "#E8F4EB",
        "foreground": "#27834A",
    },
    "cancelado": {
        "background": "#FBE9E8",
        "foreground": "#A92724",
    },
}


# ================================================================
# TONOS (usados por el parámetro ``state_tags`` de DataTable)
# ================================================================
#
# Permiten que quien crea la tabla defina sus propios nombres de
# tag (p. ej. "VENTA", "INGRESO") y les asigne un tono semántico
# genérico, sin tener que conocer los colores exactos de KLP SYSTEM.

TONE_COLORS = {
    "info": {
        "background": "#EAF3F8",
        "foreground": "#20577F",
    },
    "ok": {
        "background": "#E8F4EB",
        "foreground": "#27834A",
    },
    "warn": {
        "background": "#FBF2DF",
        "foreground": "#80520D",
    },
    "danger": {
        "background": "#FBE9E8",
        "foreground": "#A92724",
    },
    "neutral": {
        "background": "#F3F2EF",
        "foreground": "#6B6B66",
    },
}


# ================================================================
# UTILIDADES
# ================================================================


def _as_map(value: Any) -> Mapping[str, Any]:
    """
    Convierte un valor a Mapping cuando es posible.
    """

    if isinstance(value, Mapping):
        return value

    return {}


# ================================================================
# DATA TABLE
# ================================================================


class DataTable(tkui.Frame):
    """
    Tabla reutilizable para KLP SYSTEM.

    Estructura:

        DataTable (Frame)
        ├── ttk.Treeview
        ├── tkui.Scrollbar vertical
        └── tkui.Scrollbar horizontal (opcional, ver ``hscroll``)

    El Treeview continúa siendo ttk porque Tkinter no dispone
    de un componente de tabla nativo.
    """

    def __init__(
        self,
        master,
        columns: Sequence[str],
        headings: Optional[Sequence[str]] = None,
        *,
        height: int = 8,
        width: Optional[int] = None,
        # Compatibilidad con la versión anterior
        widths: Optional[Mapping[str, int] | Sequence[int]] = None,
        anchors: Optional[Mapping[str, str] | Sequence[str]] = None,
        background: Optional[str] = None,
        selectmode: str = "browse",
        show: str = "headings",
        # Alias moderno
        column_widths: Optional[Mapping[str, int]] = None,
        stretch_columns: bool = True,
        row_height: int = TABLE_ROW_HEIGHT,
        heading_height: int = TABLE_HEADING_HEIGHT,
        corner_radius: int = TABLE_CORNER_RADIUS,
        border_width: int = TABLE_BORDER_WIDTH,
        # Controla si se crea la barra de scroll horizontal.
        # Antes no existía como parámetro propio y terminaba
        # colándose en **kwargs hacia Frame, que no lo acepta.
        hscroll: bool = True,
        # Permite definir tags de fila propios (p. ej. tipos de
        # movimiento) mapeando un nombre de tag a un tono genérico
        # ("info", "ok", "warn", "danger", "neutral"). Igual que
        # hscroll, antes no era un parámetro propio y se colaba en
        # **kwargs hacia Frame.
        state_tags: Optional[Mapping[str, str]] = None,
        **kwargs,
    ):
        # ============================================================
        # COLUMNAS
        # ============================================================

        self.columns = tuple(columns)

        self.headings = tuple(headings) if headings is not None else self.columns

        self.stretch_columns = stretch_columns

        self.row_height = row_height
        self.heading_height = heading_height

        # Guardamos la preferencia de scroll horizontal para
        # usarla más abajo, al construir las barras de scroll.
        self.hscroll = hscroll

        # Tags de fila personalizados (nombre de tag -> tono).
        self.custom_state_tags = dict(state_tags) if state_tags else {}

        # ============================================================
        # WIDTHS
        # ============================================================

        self.column_widths = {}

        # column_widths tiene prioridad.
        if column_widths is not None:
            self.column_widths.update(column_widths)

        # Compatibilidad con widths.
        if widths is not None:

            if isinstance(widths, Mapping):

                self.column_widths.update(widths)

            else:

                for index, column in enumerate(self.columns):

                    if index < len(widths):

                        self.column_widths[column] = widths[index]

        # ============================================================
        # ANCHORS
        # ============================================================

        self.column_anchors = {}

        if anchors is not None:

            if isinstance(anchors, Mapping):

                self.column_anchors.update(anchors)

            else:

                for index, column in enumerate(self.columns):

                    if index < len(anchors):

                        self.column_anchors[column] = anchors[index]

        # ============================================================
        # BACKGROUND
        # ============================================================

        self.table_background = background or Colors.SURFACE

        # ============================================================
        # FRAME EXTERNO
        # ============================================================

        frame_kwargs = {
            "height": ((height * row_height) + heading_height),
            "fg_color": self.table_background,
            "corner_radius": corner_radius,
            "border_width": border_width,
            "border_color": Colors.BORDER,
        }

        # Frame no debe recibir width=None.
        if width is not None:
            frame_kwargs["width"] = width

        # Otros argumentos válidos de Frame.
        frame_kwargs.update(kwargs)

        super().__init__(
            master,
            **frame_kwargs,
        )

        # ============================================================
        # GRID PRINCIPAL
        # ============================================================

        self.grid_rowconfigure(
            0,
            weight=1,
        )

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        # ============================================================
        # FRAME INTERNO
        # ============================================================

        self.table_frame = tkui.Frame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )

        self.table_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=1,
            pady=1,
        )

        self.table_frame.grid_rowconfigure(
            0,
            weight=1,
        )

        self.table_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        # ============================================================
        # ESTILO TTK
        # ============================================================

        # IMPORTANTE:
        # Aquí solamente configuramos ttk.Style.
        # self.tree todavía NO existe.
        self._configure_tree_style()

        # ============================================================
        # TREEVIEW
        # ============================================================

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=self.columns,
            show=show,
            height=height,
            selectmode=selectmode,
            style="KLP.Treeview",
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        # ============================================================
        # TAGS DEL TREEVIEW
        # ============================================================

        # Ahora sí existe self.tree.
        self._configure_tree_tags()

        # ============================================================
        # SCROLLBAR VERTICAL
        # ============================================================

        self.vertical_scrollbar = tkui.Scrollbar(
            self.table_frame,
            orientation="vertical",
            command=self.tree.yview,
            width=12,
        )

        self.vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        self.tree.configure(yscrollcommand=self.vertical_scrollbar.set)

        # ============================================================
        # SCROLLBAR HORIZONTAL
        # ============================================================

        # Solo se crea y se conecta al Treeview cuando se solicita
        # explícitamente (hscroll=True, el valor por defecto).
        if self.hscroll:

            self.horizontal_scrollbar = tkui.Scrollbar(
                self.table_frame,
                orientation="horizontal",
                command=self.tree.xview,
                height=12,
            )

            self.horizontal_scrollbar.grid(
                row=1,
                column=0,
                sticky="ew",
            )

            self.tree.configure(xscrollcommand=self.horizontal_scrollbar.set)

        else:

            self.horizontal_scrollbar = None

        # ============================================================
        # COLUMNAS
        # ============================================================

        self._configure_columns()

        # ============================================================
        # HOVER
        # ============================================================

        self._hover_item = None

        self.tree.bind(
            "<Motion>",
            self._on_motion,
        )

        self.tree.bind(
            "<Leave>",
            self._clear_hover,
        )

        # ============================================================
        # THEME
        # ============================================================

        theme.remember(
            self,
            "plain",
            bg=self.table_background,
            fg="text",
        )

        theme.remember(
            self.tree,
            "tree",
        )

    # ================================================================
    # ESTILO TTK
    # ================================================================

    def _configure_tree_style(self):
        """
        Configura los estilos globales de ttk.Treeview.

        IMPORTANTE:
        No utiliza self.tree porque el Treeview todavía no existe
        cuando este método es llamado.
        """

        style = ttk.Style(self)

        try:
            style.theme_use("clam")

        except tk.TclError:
            pass

        background = self.table_background

        surface_hover = Colors.SURFACE_HOVER

        card = Colors.CARD
        card_hover = Colors.CARD_HOVER

        border = Colors.BORDER
        text = Colors.TEXT

        # ============================================================
        # TREEVIEW
        # ============================================================

        style.configure(
            "KLP.Treeview",
            background=background,
            foreground=text,
            fieldbackground=background,
            borderwidth=0,
            relief="flat",
            rowheight=self.row_height,
            font=TABLE_FONT,
        )

        # ============================================================
        # HEADINGS
        # ============================================================

        style.configure(
            "KLP.Treeview.Heading",
            background=card,
            foreground=text,
            borderwidth=1,
            bordercolor=border,
            relief="flat",
            font=TABLE_HEADING_FONT,
        )

        # ============================================================
        # TREEVIEW STATES
        # ============================================================

        style.map(
            "KLP.Treeview",
            background=[
                (
                    "selected",
                    Colors.PRIMARY_DARK,
                ),
                (
                    "active",
                    surface_hover,
                ),
            ],
            foreground=[
                (
                    "selected",
                    Colors.TEXT,
                ),
            ],
        )

        # ============================================================
        # HEADING STATES
        # ============================================================

        style.map(
            "KLP.Treeview.Heading",
            background=[
                (
                    "active",
                    card_hover,
                ),
            ],
            foreground=[
                (
                    "active",
                    Colors.TEXT,
                ),
            ],
        )

    # ================================================================
    # TAGS DEL TREEVIEW
    # ================================================================

    def _configure_tree_tags(self):
        """
        Configura los tags de las filas.

        Este método se ejecuta DESPUÉS de crear self.tree.
        """

        # ============================================================
        # ZEBRA
        # ============================================================

        self.tree.tag_configure(
            "even",
            background=Colors.SURFACE,
            foreground=Colors.TEXT,
        )

        self.tree.tag_configure(
            "odd",
            background=Colors.CARD,
            foreground=Colors.TEXT,
        )

        # ============================================================
        # HOVER
        # ============================================================

        self.tree.tag_configure(
            "hover",
            background=Colors.SURFACE_HOVER,
            foreground=Colors.TEXT,
        )

        # ============================================================
        # ESTADOS
        # ============================================================

        for state, state_colors in STATE_TAGS.items():

            self.tree.tag_configure(
                f"state_{state}",
                background=state_colors["background"],
                foreground=state_colors["foreground"],
            )

        # ============================================================
        # ESTADOS PERSONALIZADOS (parámetro state_tags)
        # ============================================================
        #
        # A diferencia de STATE_TAGS (que usa el prefijo "state_"),
        # estos tags se registran con el nombre exacto que definió
        # quien creó la tabla (p. ej. "VENTA", "INGRESO"), porque así
        # es como se referencian luego en add_row(tags=(...)).

        for tag_name, tone in self.custom_state_tags.items():

            tone_colors = TONE_COLORS.get(
                tone,
                TONE_COLORS["neutral"],
            )

            self.tree.tag_configure(
                tag_name,
                background=tone_colors["background"],
                foreground=tone_colors["foreground"],
            )

    # ================================================================
    # COLUMNAS
    # ================================================================

    def _configure_columns(self):
        """
        Configura encabezados, tamaños y alineación.
        """

        for index, column in enumerate(self.columns):

            if index < len(self.headings):

                heading = self.headings[index]

            else:

                heading = column

            width = self.column_widths.get(
                column,
                120,
            )

            anchor = self.column_anchors.get(
                column,
                "w",
            )

            self.tree.heading(
                column,
                text=heading,
                anchor=anchor,
            )

            self.tree.column(
                column,
                width=width,
                minwidth=40,
                anchor=anchor,
                stretch=self.stretch_columns,
            )

    # ================================================================
    # CLEAR
    # ================================================================

    def clear(self):
        """
        Elimina todas las filas.
        """

        for item in self.tree.get_children():

            self.tree.delete(item)

        self._hover_item = None

    # ================================================================
    # ADD ROW
    # ================================================================

    def add_row(
        self,
        values: Sequence[Any],
        *,
        tags: Optional[Iterable[str]] = None,
        iid: Optional[str] = None,
        state: Optional[str] = None,
    ):
        """
        Agrega una fila a la tabla.

        ``state`` permite colorear la fila según un estado, sin que
        quien llama tenga que conocer el nombre interno del tag.
        Acepta tanto los estados fijos de STATE_TAGS (p. ej.
        "activo", "pendiente") como los nombres personalizados que
        se hayan definido con el parámetro ``state_tags`` del
        constructor (p. ej. "VENTA", "INGRESO").
        """

        current_count = len(self.tree.get_children())

        zebra_tag = "even" if current_count % 2 == 0 else "odd"

        final_tags = [zebra_tag]

        if tags:
            final_tags.extend(tags)

        if state is not None:

            state_tag = self._resolve_state_tag(state)

            if state_tag is not None:

                final_tags.append(state_tag)

        insert_kwargs = {
            "values": tuple(values),
            "tags": tuple(final_tags),
        }

        if iid is not None:

            insert_kwargs["iid"] = iid

        item = self.tree.insert(
            "",
            "end",
            **insert_kwargs,
        )

        return item

    # ================================================================
    # RESOLVER TAG DE ESTADO
    # ================================================================

    def _resolve_state_tag(self, state: str) -> Optional[str]:
        """
        Traduce un valor de ``state`` al nombre de tag ya
        configurado en el Treeview.

        Prioridad:
        1. Coincidencia exacta con un tag personalizado, definido
           vía ``state_tags`` (p. ej. "VENTA" -> tag "VENTA").
        2. Coincidencia (sin distinguir mayúsculas/minúsculas) con
           un estado fijo de STATE_TAGS, usando el prefijo
           "state_" (p. ej. "activo" -> tag "state_activo").
        3. Si no hay coincidencia, no se aplica ningún tag de color
           (la fila conserva solo el rayado zebra).
        """

        if state in self.custom_state_tags:

            return state

        normalized = str(state).lower()

        if normalized in STATE_TAGS:

            return f"state_{normalized}"

        return None

    # ================================================================
    # SET ROWS
    # ================================================================

    def set_rows(
        self,
        rows: Sequence[Sequence[Any]],
        formats: Optional[Mapping[int, str]] = None,
    ) -> None:

        self.clear()

        formats = formats or {}

        for row in rows:
            formatted_row = []

            for index, value in enumerate(row):
                if index in formats:
                    try:
                        value = formats[index].format(value)
                    except (ValueError, TypeError):
                        # Si no se puede aplicar el formato,
                        # conservamos el valor original.
                        pass

                formatted_row.append(value)

            self.add_row(formatted_row)

        self.restripe()

    # ================================================================
    # RESTRIPE
    # ================================================================

    def restripe(self):
        """
        Reaplica el patrón de filas pares/impares.
        """

        children = self.tree.get_children()

        for index, item in enumerate(children):

            tags = list(
                self.tree.item(
                    item,
                    "tags",
                )
            )

            tags = [
                tag
                for tag in tags
                if tag
                not in (
                    "even",
                    "odd",
                )
            ]

            zebra_tag = "even" if index % 2 == 0 else "odd"

            tags.insert(
                0,
                zebra_tag,
            )

            self.tree.item(
                item,
                tags=tuple(tags),
            )
    def bind_tree(self, sequence, func, add=None):
        """Permite enlazar eventos directamente al Treeview interno."""
        return self.tree.bind(
            sequence,
            func,
            add=add,
        )
    # ================================================================
    # SELECTED VALUES
    # ================================================================

    def selected_values(self):
        """
        Devuelve los valores de la primera fila seleccionada.
        """

        selection = self.tree.selection()

        if not selection:

            return ()

        item = selection[0]

        return tuple(
            self.tree.item(
                item,
                "values",
            )
        )

    # ================================================================
    # SELECTED INDEX
    # ================================================================

    def selected_index(self):
        """
        Devuelve el índice de la primera fila seleccionada.
        """

        selection = self.tree.selection()

        if not selection:

            return None

        item = selection[0]

        children = self.tree.get_children()

        try:

            return children.index(item)

        except ValueError:

            return None

    # ================================================================
    # ROW COUNT
    # ================================================================

    def row_count(self):
        """
        Devuelve la cantidad de filas.
        """

        return len(self.tree.get_children())

    # ================================================================
    # SELECT FIRST
    # ================================================================

    def select_first(self):
        """
        Selecciona la primera fila.
        """

        children = self.tree.get_children()

        if not children:

            return None

        first = children[0]

        self.tree.selection_set(first)

        self.tree.focus(first)

        self.tree.see(first)

        return first

    # ================================================================
    # REMOVE SELECTED
    # ================================================================

    def remove_selected(self):
        """
        Elimina las filas seleccionadas.
        """

        selection = self.tree.selection()

        if not selection:

            return False

        for item in selection:

            self.tree.delete(item)

        self._hover_item = None

        self.restripe()

        return True

    # ================================================================
    # HOVER
    # ================================================================

    def _on_motion(self, event):
        """
        Detecta la fila debajo del cursor.
        """

        item = self.tree.identify_row(event.y)

        if item == self._hover_item:

            return

        # Restaurar fila anterior.
        if self._hover_item:

            self._restore_row_tags(self._hover_item)

        self._hover_item = item if item else None

        if not item:

            return

        current_tags = list(
            self.tree.item(
                item,
                "tags",
            )
        )

        if "hover" not in current_tags:

            current_tags.append("hover")

        self.tree.item(
            item,
            tags=tuple(current_tags),
        )

    # ================================================================

    def _clear_hover(self, event=None):
        """
        Elimina el estado hover.
        """

        if self._hover_item:

            self._restore_row_tags(self._hover_item)

        self._hover_item = None

    # ================================================================
    # RESTAURAR TAGS
    # ================================================================

    def _restore_row_tags(self, item):
        """
        Restaura los tags originales de una fila.
        """

        try:

            current_tags = list(
                self.tree.item(
                    item,
                    "tags",
                )
            )

        except tk.TclError:

            return

        current_tags = [tag for tag in current_tags if tag != "hover"]

        # Si perdió el tag zebra,
        # lo reconstruimos.
        if "even" not in current_tags and "odd" not in current_tags:

            children = self.tree.get_children()

            try:

                index = children.index(item)

            except ValueError:

                index = 0

            zebra_tag = "even" if index % 2 == 0 else "odd"

            current_tags.insert(
                0,
                zebra_tag,
            )

        self.tree.item(
            item,
            tags=tuple(current_tags),
        )

    # ================================================================
    # COMPATIBILIDAD
    # ================================================================

    def get_tree(self):
        """
        Devuelve el Treeview interno.
        """

        return self.tree

    def selection(self):
        """
        Proxy compatible con Treeview.selection().
        """

        return self.tree.selection()

    def item(
        self,
        item,
        option=None,
        **kwargs,
    ):
        """
        Proxy compatible con Treeview.item().
        """

        return self.tree.item(
            item,
            option,
            **kwargs,
        )

    def insert(
        self,
        *args,
        **kwargs,
    ):
        """
        Proxy compatible con Treeview.insert().
        """

        return self.tree.insert(
            *args,
            **kwargs,
        )

    def delete(
        self,
        *items,
    ):
        """
        Proxy compatible con Treeview.delete().
        """

        result = self.tree.delete(*items)

        self.restripe()

        return result

    def configure_tree(
        self,
        **kwargs,
    ):
        """
        Permite configurar directamente
        el Treeview interno.
        """

        self.tree.configure(**kwargs)
