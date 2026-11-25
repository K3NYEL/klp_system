"""Dashboard principal de KLP SYSTEM.

El dashboard muestra únicamente la información más importante del negocio.
Los listados detallados se abren en ventanas independientes.

Información visible:
    - Ventas del período.
    - Cantidad de facturas.
    - ITBIS.
    - Cuentas por cobrar.
    - Efectivo esperado.
    - Estado de caja.
    - Ingresos y egresos.
    - Resumen de cuentas por cobrar.
    - Actividad reciente.

Información detallada:
    - Movimientos de caja.
    - Productos más vendidos.
    - Cuentas por cobrar.
"""

from __future__ import annotations

import sqlite3
import tkinter as tk
from datetime import date
from tkinter import messagebox
from typing import Any, Callable, Optional

from app.ui import tk_widgets as tkui

from app.core.reports import receivables, sales_summary, top_products
from app.ui import theme
from app.ui.components import cards, inputs, tables
from app.ui.components.buttons import AppButton


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

DEFAULT_MOVEMENT_KINDS: tuple[str, ...] = (
    "GASTO",
    "RETIRO",
    "INGRESO",
)

DEFAULT_PAYMENT_METHODS: tuple[str, ...] = (
    "EFECTIVO",
    "TARJETA",
    "TRANSFERENCIA",
    "OTRO",
)

MOVEMENT_STATE_TAGS = {
    "VENTA": "info",
    "INGRESO": "ok",
    "RETIRO": "warn",
    "GASTO": "danger",
}


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class DashboardCajaView:
    """Dashboard principal y control de caja."""

    def __init__(
        self,
        parent: tk.Misc,
        connection: Any,
        actor_id: Optional[int] = None,
        on_open_cash: Optional[Callable[[], Any]] = None,
        on_close_cash: Optional[Callable[[], Any]] = None,
        can_manage_cash: bool = False,
        on_change: Optional[Callable[[], Any]] = None,
    ) -> None:

        self.parent = parent
        self.connection = connection
        self.actor_id = actor_id

        self.on_open_cash = on_open_cash
        self.on_close_cash = on_close_cash
        self.can_manage_cash = can_manage_cash
        self.on_change = on_change

        self.frame = tkui.Frame(parent)

        theme.remember(
            self.frame,
            "plain",
            bg="window",
            fg="text",
        )

        self.frame.pack(
            fill="both",
            expand=True,
        )

        # ------------------------------------------------------------------
        # Variables
        # ------------------------------------------------------------------

        self.start_date = tk.StringVar(
            value=date.today().replace(day=1).isoformat()
        )

        self.end_date = tk.StringVar(
            value=date.today().isoformat()
        )

        self.kind = tk.StringVar(value="GASTO")
        self.amount = tk.StringVar()
        self.method = tk.StringVar(value="EFECTIVO")
        self.reference = tk.StringVar()

        self.cash_info_var = tk.StringVar(
            value="No hay una caja abierta."
        )

        self.receivables_info_var = tk.StringVar(
            value="No hay facturas pendientes."
        )

        # ------------------------------------------------------------------
        # Métricas
        # ------------------------------------------------------------------

        self.metrics: dict[str, Any] = {}

        # ------------------------------------------------------------------
        # Ventanas secundarias
        # ------------------------------------------------------------------

        self.movements_window: Optional[tkui.Toplevel] = None
        self.movements_table: Optional[tables.DataTable] = None

        self.products_window: Optional[tkui.Toplevel] = None
        self.products_table: Optional[tables.DataTable] = None

        self.receivables_window: Optional[tkui.Toplevel] = None
        self.receivables_table: Optional[tables.DataTable] = None

        # ------------------------------------------------------------------
        # Datos almacenados
        # ------------------------------------------------------------------

        self._products_rows: list[tuple[Any, ...]] = []
        self._receivables_rows: list[tuple[Any, ...]] = []

        self._recent_activity_rows: list[tuple[Any, ...]] = []

        # ------------------------------------------------------------------
        # Construcción
        # ------------------------------------------------------------------

        self._build()
        self.refresh()

    # =======================================================================
    # CONSTRUCCIÓN
    # =======================================================================

    def _build(self) -> None:
        self._build_header()
        self._build_metrics()
        self._build_main_content()

    # -----------------------------------------------------------------------
    # Header
    # -----------------------------------------------------------------------

    def _build_header(self) -> None:
        header = cards.Toolbar(
            self.frame,
            padding=12,
        )

        header.pack(
            fill="x",
            padx=16,
            pady=(14, 10),
        )

        left = header.left
        right = header.right

        dashboard_label = tkui.Label(
            left,
            text="Dashboard",
            font=theme.font("body_bold"),
            anchor="w",
        )

        dashboard_label.pack(
            side="left",
            padx=(0, 18),
        )

        # Fecha inicial
        cards.label(
            left,
            "Desde",
            font_role="small",
            background="surface_alt",
        ).pack(
            side="left",
        )

        inputs.make_entry(
            left,
            textvariable=self.start_date,
            width=12,
        ).pack(
            side="left",
            padx=(6, 8),
        )

        # Fecha final
        cards.label(
            left,
            "Hasta",
            font_role="small",
            background="surface_alt",
        ).pack(
            side="left",
        )

        inputs.make_entry(
            left,
            textvariable=self.end_date,
            width=12,
        ).pack(
            side="left",
            padx=(6, 8),
        )

        AppButton(
            left,
            "Actualizar",
            command=self.refresh,
            variant="primary",
            tooltip="Actualizar información del dashboard",
        ).pack(
            side="left",
        )

        # Estado de caja
        self.cash_badge = cards.Badge(
            right,
            text="CAJA CERRADA",
            tone="muted",
        )

        self.cash_badge.pack(
            side="left",
            padx=(0, 8),
        )

        self.open_cash_button = AppButton(
            right,
            "Abrir caja",
            command=self.open_cash,
            variant="success",
            tooltip="Abrir caja",
        )

        self.open_cash_button.pack(
            side="left",
            padx=3,
        )

        self.close_cash_button = AppButton(
            right,
            "Cerrar caja",
            command=self.close_cash,
            variant="danger",
            tooltip="Cerrar caja",
        )

        self.close_cash_button.pack(
            side="left",
            padx=3,
        )

    # -----------------------------------------------------------------------
    # Métricas
    # -----------------------------------------------------------------------

    def _build_metrics(self) -> None:
        row = tkui.Frame(self.frame)

        theme.remember(
            row,
            "plain",
            bg="window",
            fg="text",
        )

        row.pack(
            fill="x",
            padx=16,
            pady=(0, 12),
        )

        self.metrics = {
            "sales": cards.MetricCard(
                row,
                "Ventas",
                tone="accent",
            ),
            "invoices": cards.MetricCard(
                row,
                "Facturas",
                tone="accent_dark",
            ),
            "taxes": cards.MetricCard(
                row,
                "ITBIS",
                tone="warning",
            ),
            "receivables": cards.MetricCard(
                row,
                "Por cobrar",
                tone="danger",
            ),
            "cash": cards.MetricCard(
                row,
                "Efectivo",
                tone="success",
            ),
        }

        for metric in self.metrics.values():
            metric.pack(
                side="left",
                fill="both",
                expand=True,
                padx=4,
            )

    # -----------------------------------------------------------------------
    # Contenido principal
    # -----------------------------------------------------------------------

    def _build_main_content(self) -> None:
        content = tkui.Frame(self.frame)

        theme.remember(
            content,
            "plain",
            bg="window",
            fg="text",
        )

        content.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 14),
        )

        content.columnconfigure(
            0,
            weight=3,
            uniform="dashboard",
        )

        content.columnconfigure(
            1,
            weight=2,
            uniform="dashboard",
        )

        content.rowconfigure(
            0,
            weight=1,
        )

        # Izquierda
        self._build_cash_panel(content)

        # Derecha
        right_column = tkui.Frame(content)

        theme.remember(
            right_column,
            "plain",
            bg="window",
            fg="text",
        )

        right_column.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
        )

        right_column.columnconfigure(
            0,
            weight=1,
        )

        right_column.rowconfigure(
            0,
            weight=1,
        )

        right_column.rowconfigure(
            1,
            weight=1,
        )

        self._build_quick_actions(
            right_column,
        )

        self._build_activity_panel(
            right_column,
        )

    # =======================================================================
    # PANEL DE CAJA
    # =======================================================================

    def _build_cash_panel(self, parent: tk.Misc) -> None:
        card = cards.Card(
            parent,
            title="Control de Caja",
            subtitle="Estado actual de la caja",
            padding=14,
        )

        card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )

        body = card.body

        # ------------------------------------------------------------------
        # Estado
        # ------------------------------------------------------------------

        status = tkui.Frame(body)

        theme.remember(
            status,
            "plain",
            bg="surface",
            fg="text",
        )

        status.pack(
            fill="x",
            pady=(0, 12),
        )

        self.cash_info_label = tkui.Label(
            status,
            textvariable=self.cash_info_var,
            anchor="w",
            justify="left",
            wraplength=620,
            font=theme.font("body"),
        )

        self.cash_info_label.pack(
            fill="x",
            padx=4,
            pady=6,
        )

        # ------------------------------------------------------------------
        # Resumen financiero de caja
        # ------------------------------------------------------------------

        summary = tkui.Frame(body)

        theme.remember(
            summary,
            "plain",
            bg="surface",
            fg="text",
        )

        summary.pack(
            fill="x",
            pady=(0, 14),
        )

        summary.columnconfigure(
            0,
            weight=1,
        )

        summary.columnconfigure(
            1,
            weight=1,
        )

        summary.columnconfigure(
            2,
            weight=1,
        )

        self.cash_initial_label = self._create_cash_summary(
            summary,
            "Inicial",
            "RD$ 0.00",
            0,
        )

        self.cash_income_label = self._create_cash_summary(
            summary,
            "Ingresos",
            "RD$ 0.00",
            1,
        )

        self.cash_expenses_label = self._create_cash_summary(
            summary,
            "Egresos",
            "RD$ 0.00",
            2,
        )

        # ------------------------------------------------------------------
        # Registro rápido
        # ------------------------------------------------------------------

        section_title = tkui.Label(
            body,
            text="Registrar movimiento",
            anchor="w",
            font=theme.font("body_bold"),
        )

        section_title.pack(
            fill="x",
            pady=(0, 8),
        )

        form = tkui.Frame(body)

        theme.remember(
            form,
            "plain",
            bg="surface",
            fg="text",
        )

        form.pack(
            fill="x",
            pady=(0, 8),
        )

        form.columnconfigure(
            1,
            weight=1,
        )

        form.columnconfigure(
            3,
            weight=1,
        )

        _, self.kind_combo = inputs.labeled_combobox(
            form,
            "Tipo",
            values=DEFAULT_MOVEMENT_KINDS,
            textvariable=self.kind,
            width=14,
            row=0,
            column=0,
            label_column=0,
            entry_column=1,
        )

        _, self.amount_entry = inputs.labeled_entry(
            form,
            "Monto",
            textvariable=self.amount,
            width=14,
            row=0,
            column=2,
            label_column=2,
            entry_column=3,
            entry_sticky="ew",
        )

        _, self.method_combo = inputs.labeled_combobox(
            form,
            "Método",
            values=DEFAULT_PAYMENT_METHODS,
            textvariable=self.method,
            width=14,
            row=1,
            column=0,
            label_column=0,
            entry_column=1,
        )

        _, self.reference_entry = inputs.labeled_entry(
            form,
            "Referencia",
            textvariable=self.reference,
            width=24,
            row=1,
            column=2,
            label_column=2,
            entry_column=3,
            entry_sticky="ew",
        )

        # ------------------------------------------------------------------
        # Botones
        # ------------------------------------------------------------------

        actions = tkui.Frame(body)

        theme.remember(
            actions,
            "plain",
            bg="surface",
            fg="text",
        )

        actions.pack(
            fill="x",
            pady=(4, 8),
        )

        self.save_button = AppButton(
            actions,
            "Guardar movimiento",
            command=self.save_movement,
            variant="success",
            tooltip="Guardar movimiento",
        )

        self.save_button.pack(
            side="left",
        )

        AppButton(
            actions,
            "Limpiar",
            command=self.clear_form,
            variant="neutral",
        ).pack(
            side="left",
            padx=6,
        )

        AppButton(
            actions,
            "Ver movimientos",
            command=self.open_movements,
            variant="primary",
            tooltip="Abrir historial completo",
        ).pack(
            side="right",
        )

        # ------------------------------------------------------------------
        # Estado inferior
        # ------------------------------------------------------------------

        self.totals_badge = cards.Badge(
            body,
            text="Ingresos RD$ 0.00  |  Egresos RD$ 0.00",
            tone="neutral",
        )

        self.totals_badge.pack(
            anchor="w",
            pady=(4, 0),
        )

    def _create_cash_summary(
        self,
        parent: tk.Misc,
        title: str,
        value: str,
        column: int,
    ) -> tkui.Label:

        box = tkui.Frame(parent)

        theme.remember(
            box,
            "plain",
            bg="surface",
            fg="text",
        )

        box.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=4,
            pady=4,
        )

        label = tkui.Label(
            box,
            text=title,
            anchor="w",
            font=theme.font("small"),
        )

        label.pack(
            fill="x",
            padx=8,
            pady=(7, 0),
        )

        value_label = tkui.Label(
            box,
            text=value,
            anchor="w",
            font=theme.font("body_bold"),
        )

        value_label.pack(
            fill="x",
            padx=8,
            pady=(2, 7),
        )

        return value_label

    # =======================================================================
    # ACCIONES RÁPIDAS
    # =======================================================================

    def _build_quick_actions(self, parent: tk.Misc) -> None:
        card = cards.Card(
            parent,
            title="Acciones rápidas",
            subtitle="Accede a la información detallada",
            padding=12,
        )

        card.grid(
            row=0,
            column=0,
            sticky="nsew",
            pady=(0, 8),
        )

        body = card.body

        body.columnconfigure(
            0,
            weight=1,
        )

        body.columnconfigure(
            1,
            weight=1,
        )

        AppButton(
            body,
            "Movimientos de caja",
            command=self.open_movements,
            variant="primary",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5),
            pady=(0, 8),
        )

        AppButton(
            body,
            "Productos más vendidos",
            command=self.open_products,
            variant="neutral",
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0),
            pady=(0, 8),
        )

        AppButton(
            body,
            "Cuentas por cobrar",
            command=self.open_receivables,
            variant="danger",
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
        )

    # =======================================================================
    # ACTIVIDAD RECIENTE
    # =======================================================================

    def _build_activity_panel(self, parent: tk.Misc) -> None:
        card = cards.Card(
            parent,
            title="Actividad reciente",
            subtitle="Últimos movimientos registrados",
            padding=12,
        )

        card.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        body = card.body

        self.activity_container = tkui.Frame(body)

        theme.remember(
            self.activity_container,
            "plain",
            bg="surface",
            fg="text",
        )

        self.activity_container.pack(
            fill="both",
            expand=True,
        )

        AppButton(
            body,
            "Ver todos los movimientos",
            command=self.open_movements,
            variant="neutral",
        ).pack(
            fill="x",
            pady=(8, 0),
        )

    def _refresh_activity(self) -> None:
        """Actualiza las últimas actividades visibles."""

        for widget in self.activity_container.winfo_children():
            widget.destroy()

        if not self._recent_activity_rows:
            empty = tkui.Label(
                self.activity_container,
                text="No hay actividad reciente.",
                anchor="w",
                font=theme.font("small"),
            )

            empty.pack(
                fill="x",
                padx=8,
                pady=12,
            )

            return

        for row in self._recent_activity_rows[:5]:
            fecha, tipo, monto, referencia = row

            item = tkui.Frame(
                self.activity_container,
                height=34,
            )

            theme.remember(
                item,
                "plain",
                bg="surface",
                fg="text",
            )

            item.pack(
                fill="x",
                padx=4,
                pady=2,
            )

            item.grid_propagate(False)

            icon_text = {
                "VENTA": "●",
                "INGRESO": "●",
                "GASTO": "●",
                "RETIRO": "●",
            }.get(
                tipo,
                "●",
            )

            icon = tkui.Label(
                item,
                text=icon_text,
                width=20,
                anchor="w",
            )

            icon.grid(
                row=0,
                column=0,
                padx=(6, 2),
                sticky="w",
            )

            type_label = tkui.Label(
                item,
                text=tipo,
                width=70,
                anchor="w",
                font=theme.font("small_bold"),
            )

            type_label.grid(
                row=0,
                column=1,
                padx=4,
                sticky="w",
            )

            ref_label = tkui.Label(
                item,
                text=referencia or "Sin referencia",
                anchor="w",
                font=theme.font("small"),
            )

            ref_label.grid(
                row=0,
                column=2,
                padx=4,
                sticky="ew",
            )

            amount_label = tkui.Label(
                item,
                text=f"RD$ {float(monto):.2f}",
                anchor="e",
                font=theme.font("small_bold"),
            )

            amount_label.grid(
                row=0,
                column=3,
                padx=(4, 8),
                sticky="e",
            )

            item.columnconfigure(
                2,
                weight=1,
            )

    # =======================================================================
    # REFRESH GENERAL
    # =======================================================================

    def refresh(self) -> None:
        try:
            self.refresh_metrics()
            self.refresh_cash()
            self.refresh_products()
            self.refresh_receivables()
            self.refresh_activity()

        except sqlite3.Error as exc:
            messagebox.showerror(
                "Dashboard",
                f"No se pudieron cargar los datos:\n{exc}",
                parent=self.frame,
            )

    # =======================================================================
    # MÉTRICAS
    # =======================================================================

    def refresh_metrics(self) -> None:
        summary = sales_summary(
            self.connection,
            self.start_date.get(),
            self.end_date.get(),
        )

        self.metrics["sales"].set_value(
            f"RD$ {summary['total']:.2f}"
        )

        self.metrics["invoices"].set_value(
            str(summary["facturas"])
        )

        self.metrics["taxes"].set_value(
            f"RD$ {summary['impuestos']:.2f}"
        )

        pending = receivables(
            self.connection
        )

        pending_total = sum(
            float(row[5] or 0)
            for row in pending
        )

        self.metrics["receivables"].set_value(
            f"RD$ {pending_total:.2f}"
        )

        self.metrics["receivables"].set_hint(
            "Sin facturas pendientes"
            if not pending
            else f"{len(pending)} factura(s) pendiente(s)"
        )

    # =======================================================================
    # PRODUCTOS
    # =======================================================================

    def refresh_products(self) -> None:
        rows = top_products(
            self.connection,
            self.start_date.get(),
            self.end_date.get(),
        )

        self._products_rows = [
            tuple(row)
            for row in rows
        ]

        if (
            self.products_table is not None
            and self.products_window is not None
            and self.products_window.winfo_exists()
        ):
            self.products_table.set_rows(
                self._products_rows,
                formats={
                    3: "RD$ {:.2f}",
                },
            )

    # =======================================================================
    # CUENTAS POR COBRAR
    # =======================================================================

    def refresh_receivables(self) -> None:
        rows = receivables(
            self.connection
        )

        self._receivables_rows = [
            (
                row[1],
                row[2],
                row[3],
                row[5],
            )
            for row in rows
        ]

        total = sum(
            float(row[3] or 0)
            for row in self._receivables_rows
        )

        self.receivables_info_var.set(
            "No hay facturas pendientes."
            if not self._receivables_rows
            else (
                f"{len(self._receivables_rows)} "
                "factura(s) pendiente(s) de cobro."
            )
        )

        if (
            self.receivables_table is not None
            and self.receivables_window is not None
            and self.receivables_window.winfo_exists()
        ):
            self.receivables_table.set_rows(
                self._receivables_rows,
                formats={
                    2: "RD$ {:.2f}",
                    3: "RD$ {:.2f}",
                },
            )

        # Guardamos el total para que la tarjeta se actualice.
        self._receivables_total = total

    # =======================================================================
    # ACTIVIDAD RECIENTE
    # =======================================================================

    def refresh_activity(self) -> None:
        rows = self.connection.execute(
            """
            SELECT
                fecha,
                tipo,
                monto,
                COALESCE(referencia, '')
            FROM cash_movements
            ORDER BY id DESC
            LIMIT 5
            """
        ).fetchall()

        self._recent_activity_rows = [
            tuple(row)
            for row in rows
        ]

        self._refresh_activity()

    # =======================================================================
    # CAJA
    # =======================================================================

    def open_cash_register(self):
        return self.connection.execute(
            """
            SELECT
                id,
                fecha_apertura,
                monto_inicial
            FROM cash_registers
            WHERE estado = 'ABIERTA'
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

    def expected_cash(
        self,
        cash_id: int,
        initial: float,
    ) -> float:

        row = self.connection.execute(
            """
            SELECT COALESCE(
                SUM(
                    CASE
                        WHEN tipo IN ('VENTA', 'INGRESO')
                        THEN monto
                        ELSE -monto
                    END
                ),
                0
            )
            FROM cash_movements
            WHERE caja_id = ?
              AND (
                  tipo <> 'VENTA'
                  OR metodo_pago = 'EFECTIVO'
              )
            """,
            (cash_id,),
        ).fetchone()

        return round(
            float(initial) + float(row[0] or 0),
            2,
        )

    def refresh_cash(self) -> None:
        cash = self.open_cash_register()

        if not cash:
            self.cash_badge.set(
                "CAJA CERRADA",
                "muted",
            )

            self.cash_info_var.set(
                "No hay una caja abierta. Abra la caja para "
                "registrar ventas y movimientos de efectivo."
            )

            self.metrics["cash"].set_value(
                "RD$ 0.00"
            )

            self.metrics["cash"].set_hint(
                "Caja cerrada"
            )

            self.cash_initial_label.configure(
                text="RD$ 0.00"
            )

            self.cash_income_label.configure(
                text="RD$ 0.00"
            )

            self.cash_expenses_label.configure(
                text="RD$ 0.00"
            )

            self.totals_badge.set(
                "Sin movimientos de caja",
                "neutral",
            )

            self._set_form_enabled(False)

            self._refresh_open_windows()

            return

        cash_id = int(cash[0])
        opened_at = cash[1] or ""
        initial = float(cash[2] or 0)

        expected = self.expected_cash(
            cash_id,
            initial,
        )

        totals = self.connection.execute(
            """
            SELECT
                COALESCE(
                    SUM(
                        CASE
                            WHEN tipo IN ('VENTA', 'INGRESO')
                            THEN monto
                            ELSE 0
                        END
                    ),
                    0
                ),
                COALESCE(
                    SUM(
                        CASE
                            WHEN tipo IN ('GASTO', 'RETIRO')
                            THEN monto
                            ELSE 0
                        END
                    ),
                    0
                )
            FROM cash_movements
            WHERE caja_id = ?
            """,
            (cash_id,),
        ).fetchone()

        income = float(
            totals[0] or 0
        )

        expenses = float(
            totals[1] or 0
        )

        self.cash_badge.set(
            f"CAJA ABIERTA · #{cash_id}",
            "ok",
        )

        self.cash_info_var.set(
            f"Caja #{cash_id} abierta el {opened_at} · "
            f"Inicial RD$ {initial:.2f} · "
            f"Efectivo esperado RD$ {expected:.2f}"
        )

        self.metrics["cash"].set_value(
            f"RD$ {expected:.2f}"
        )

        self.metrics["cash"].set_hint(
            f"Apertura RD$ {initial:.2f}"
        )

        self.cash_initial_label.configure(
            text=f"RD$ {initial:.2f}"
        )

        self.cash_income_label.configure(
            text=f"RD$ {income:.2f}"
        )

        self.cash_expenses_label.configure(
            text=f"RD$ {expenses:.2f}"
        )

        self.totals_badge.set(
            f"Ingresos RD$ {income:.2f}  |  "
            f"Egresos RD$ {expenses:.2f}",
            "info",
        )

        self._set_form_enabled(
            self.can_manage_cash
        )

        self._refresh_open_windows()

    # =======================================================================
    # VENTANA DE MOVIMIENTOS
    # =======================================================================

    def open_movements(self) -> None:
        if (
            self.movements_window is not None
            and self.movements_window.winfo_exists()
        ):
            self.movements_window.focus_force()
            self.movements_window.lift()
            self.refresh_movements_table()
            return

        window = tkui.Toplevel(
            self.frame
        )

        self.movements_window = window

        window.title(
            "KLP SYSTEM · Movimientos de caja"
        )

        window.geometry(
            "950x560"
        )

        window.minsize(
            760,
            420,
        )

        theme.remember(
            window,
            "plain",
            bg="window",
            fg="text",
        )

        window.protocol(
            "WM_DELETE_WINDOW",
            self._close_movements_window,
        )

        container = tkui.Frame(
            window
        )

        theme.remember(
            container,
            "plain",
            bg="window",
            fg="text",
        )

        container.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=16,
        )

        card = cards.Card(
            container,
            title="Movimientos de caja",
            subtitle=(
                "Historial completo de ingresos, "
                "gastos, retiros y ventas"
            ),
            padding=14,
        )

        card.pack(
            fill="both",
            expand=True,
        )

        self.movements_table = tables.DataTable(
            card.body,
            columns=(
                "Fecha",
                "Tipo",
                "Monto",
                "Método",
                "Referencia",
            ),
            widths=(
                150,
                100,
                120,
                140,
                300,
            ),
            anchors=(
                "w",
                "w",
                "e",
                "w",
                "w",
            ),
            height=18,
            state_tags=MOVEMENT_STATE_TAGS,
        )

        self.movements_table.pack(
            fill="both",
            expand=True,
        )

        self.refresh_movements_table()

    def refresh_movements_table(self) -> None:
        if self.movements_table is None:
            return

        if (
            self.movements_window is None
            or not self.movements_window.winfo_exists()
        ):
            return

        self.movements_table.clear()

        cash = self.open_cash_register()

        if not cash:
            self.movements_table.add_row(
                (
                    "",
                    "",
                    "",
                    "",
                    "No hay una caja abierta.",
                )
            )

            self.movements_table.restripe()
            return

        cash_id = int(
            cash[0]
        )

        rows = self.connection.execute(
            """
            SELECT
                fecha,
                tipo,
                monto,
                metodo_pago,
                COALESCE(referencia, '')
            FROM cash_movements
            WHERE caja_id = ?
            ORDER BY id DESC
            LIMIT 200
            """,
            (cash_id,),
        )

        for row in rows:
            self.movements_table.add_row(
                (
                    row[0],
                    row[1],
                    f"RD$ {float(row[2]):.2f}",
                    row[3],
                    row[4],
                ),
                state=row[1],
            )

        self.movements_table.restripe()

    def _close_movements_window(self) -> None:
        try:
            if (
                self.movements_window is not None
                and self.movements_window.winfo_exists()
            ):
                self.movements_window.destroy()

        except tk.TclError:
            pass

        finally:
            self.movements_window = None
            self.movements_table = None

    # =======================================================================
    # VENTANA DE PRODUCTOS
    # =======================================================================

    def open_products(self) -> None:
        if (
            self.products_window is not None
            and self.products_window.winfo_exists()
        ):
            self.products_window.focus_force()
            self.products_window.lift()
            self.refresh_products()
            return

        window = tkui.Toplevel(
            self.frame
        )

        self.products_window = window

        window.title(
            "KLP SYSTEM · Productos más vendidos"
        )

        window.geometry(
            "820x520"
        )

        window.minsize(
            640,
            360,
        )

        theme.remember(
            window,
            "plain",
            bg="window",
            fg="text",
        )

        window.protocol(
            "WM_DELETE_WINDOW",
            self._close_products_window,
        )

        container = tkui.Frame(
            window
        )

        theme.remember(
            container,
            "plain",
            bg="window",
            fg="text",
        )

        container.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=16,
        )

        card = cards.Card(
            container,
            title="Productos más vendidos",
            subtitle=(
                f"Desde {self.start_date.get()} "
                f"hasta {self.end_date.get()}"
            ),
            padding=14,
        )

        card.pack(
            fill="both",
            expand=True,
        )

        self.products_table = tables.DataTable(
            card.body,
            columns=(
                "Código",
                "Producto",
                "Unidades",
                "Ventas",
            ),
            widths=(
                120,
                280,
                110,
                140,
            ),
            anchors=(
                "w",
                "w",
                "e",
                "e",
            ),
            height=16,
        )

        self.products_table.pack(
            fill="both",
            expand=True,
        )

        self.products_table.set_rows(
            self._products_rows,
            formats={
                3: "RD$ {:.2f}",
            },
        )

    def _close_products_window(self) -> None:
        try:
            if (
                self.products_window is not None
                and self.products_window.winfo_exists()
            ):
                self.products_window.destroy()

        except tk.TclError:
            pass

        finally:
            self.products_window = None
            self.products_table = None

    # =======================================================================
    # VENTANA DE CUENTAS POR COBRAR
    # =======================================================================

    def open_receivables(self) -> None:
        if (
            self.receivables_window is not None
            and self.receivables_window.winfo_exists()
        ):
            self.receivables_window.focus_force()
            self.receivables_window.lift()
            self.refresh_receivables()
            return

        window = tkui.Toplevel(
            self.frame
        )

        self.receivables_window = window

        window.title(
            "KLP SYSTEM · Cuentas por cobrar"
        )

        window.geometry(
            "820x520"
        )

        window.minsize(
            640,
            360,
        )

        theme.remember(
            window,
            "plain",
            bg="window",
            fg="text",
        )

        window.protocol(
            "WM_DELETE_WINDOW",
            self._close_receivables_window,
        )

        container = tkui.Frame(
            window
        )

        theme.remember(
            container,
            "plain",
            bg="window",
            fg="text",
        )

        container.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=16,
        )

        card = cards.Card(
            container,
            title="Cuentas por cobrar",
            subtitle="Facturas con saldo pendiente",
            padding=14,
        )

        card.pack(
            fill="both",
            expand=True,
        )

        self.receivables_table = tables.DataTable(
            card.body,
            columns=(
                "Factura",
                "Cliente",
                "Total",
                "Saldo",
            ),
            widths=(
                120,
                260,
                130,
                130,
            ),
            anchors=(
                "w",
                "w",
                "e",
                "e",
            ),
            height=16,
        )

        self.receivables_table.pack(
            fill="both",
            expand=True,
        )

        self.receivables_table.set_rows(
            self._receivables_rows,
            formats={
                2: "RD$ {:.2f}",
                3: "RD$ {:.2f}",
            },
        )

    def _close_receivables_window(self) -> None:
        try:
            if (
                self.receivables_window is not None
                and self.receivables_window.winfo_exists()
            ):
                self.receivables_window.destroy()

        except tk.TclError:
            pass

        finally:
            self.receivables_window = None
            self.receivables_table = None

    # =======================================================================
    # VENTANAS ABIERTAS
    # =======================================================================

    def _refresh_open_windows(self) -> None:
        if (
            self.movements_window is not None
            and self.movements_window.winfo_exists()
        ):
            self.refresh_movements_table()

        if (
            self.products_window is not None
            and self.products_window.winfo_exists()
            and self.products_table is not None
        ):
            self.products_table.set_rows(
                self._products_rows,
                formats={
                    3: "RD$ {:.2f}",
                },
            )

        if (
            self.receivables_window is not None
            and self.receivables_window.winfo_exists()
            and self.receivables_table is not None
        ):
            self.receivables_table.set_rows(
                self._receivables_rows,
                formats={
                    2: "RD$ {:.2f}",
                    3: "RD$ {:.2f}",
                },
            )

    # =======================================================================
    # ACCIONES DE CAJA
    # =======================================================================

    def open_cash(self) -> None:
        if self.on_open_cash is None:
            messagebox.showinfo(
                "Caja",
                "La apertura de caja no está disponible "
                "en esta vista.",
                parent=self.frame,
            )
            return

        self.on_open_cash()
        self.refresh()

    def close_cash(self) -> None:
        if self.on_close_cash is None:
            messagebox.showinfo(
                "Caja",
                "El cierre de caja no está disponible "
                "en esta vista.",
                parent=self.frame,
            )
            return

        self.on_close_cash()
        self.refresh()

    # =======================================================================
    # FORMULARIO
    # =======================================================================

    def clear_form(self) -> None:
        self.amount.set("")
        self.reference.set("")

    def focus_movement_form(self) -> None:
        try:
            self.amount_entry.focus_set()
        except tk.TclError:
            pass

    def _set_form_enabled(
        self,
        enabled: bool,
    ) -> None:

        state = (
            "normal"
            if enabled
            else "disabled"
        )

        self.amount_entry.configure(
            state=state
        )

        self.reference_entry.configure(
            state=state
        )

        self.kind_combo.configure(
            state=state
        )

        self.method_combo.configure(
            state=state
        )

        self.save_button.configure(
            state=state
        )

    def save_movement(self) -> None:
        try:
            amount = float(
                self.amount.get().replace(
                    ",",
                    ".",
                )
            )

        except ValueError:
            messagebox.showerror(
                "Caja",
                "El monto debe ser un número válido.",
                parent=self.frame,
            )
            return

        if amount <= 0:
            messagebox.showerror(
                "Caja",
                "El monto debe ser mayor que cero.",
                parent=self.frame,
            )
            return

        cash = self.open_cash_register()

        if not cash:
            messagebox.showwarning(
                "Caja",
                "Debe abrir una caja antes de registrar "
                "movimientos.",
                parent=self.frame,
            )
            return

        try:
            self.connection.execute(
                """
                INSERT INTO cash_movements (
                    caja_id,
                    tipo,
                    monto,
                    metodo_pago,
                    referencia,
                    usuario_id
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    cash[0],
                    self.kind.get(),
                    amount,
                    self.method.get(),
                    self.reference.get().strip(),
                    self.actor_id,
                ),
            )

            self.connection.commit()

        except sqlite3.Error as exc:
            self.connection.rollback()

            messagebox.showerror(
                "Caja",
                f"No se pudo registrar el movimiento:\n{exc}",
                parent=self.frame,
            )
            return

        self.clear_form()
        self.refresh()

        if self.on_change is not None:
            self.on_change()

        messagebox.showinfo(
            "Caja",
            "Movimiento de caja registrado.",
            parent=self.frame,
        )
