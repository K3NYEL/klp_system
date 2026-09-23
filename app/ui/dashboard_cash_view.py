"""Panel unificado de caja y dashboard.

Antes existían dos pantallas separadas (DashboardView y
CashMovementView); ahora son una sola pestaña: los indicadores del negocio,
el estado de la caja, el registro de movimientos de efectivo, los productos
más vendidos y las cuentas por cobrar.
"""

from __future__ import annotations

import sqlite3
import tkinter as tk
from datetime import date
from tkinter import messagebox
from typing import Any, Callable, Optional

import customtkinter as ctk

from app.core.reports import receivables, sales_summary, top_products
from app.ui import theme
from app.ui.components import cards, inputs, tables
from app.ui.components.buttons import AppButton

# Tonos usados al pintar el estado de la caja.
CASH_TONES = {
    "ABIERTA": "ok",
    "CERRADA": "muted",
}


class DashboardCajaView:
    """Dashboard de indicadores + control de caja en una sola vista."""

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

        self.frame = ctk.CTkFrame(parent)
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

        self.start_date = tk.StringVar(value=date.today().replace(day=1).isoformat())
        self.end_date = tk.StringVar(value=date.today().isoformat())

        self.kind = tk.StringVar(value="GASTO")
        self.amount = tk.StringVar()
        self.method = tk.StringVar(value="EFECTIVO")
        self.reference = tk.StringVar()

        self.movements_window = None
        self.movements_table = None

        self._build()
        self.refresh()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------

    def _build(self) -> None:
        self._build_toolbar()
        self._build_metrics()

        content = ctk.CTkFrame(self.frame)
        theme.remember(
            content,
            "plain",
            bg="window",
            fg="text",
        )

        content.pack(
            fill=tk.BOTH,
            expand=True,
            padx=16,
            pady=(0, 14),
        )

        content.columnconfigure(
            0,
            weight=3,
            uniform="panel",
        )
        content.columnconfigure(
            1,
            weight=2,
            uniform="panel",
        )
        content.rowconfigure(0, weight=1)

        self._build_cash_panel(content)
        self._build_side_panels(content)

    def _build_toolbar(self) -> None:
        toolbar = cards.Toolbar(
            self.frame,
            padding=12,
        )

        toolbar.pack(
            fill=tk.X,
            padx=16,
            pady=(14, 10),
        )

        left = toolbar.left
        right = toolbar.right

        cards.label(
            left,
            "Rango de análisis",
            font_role="body_bold",
            background="surface_alt",
        ).pack(
            side=tk.LEFT,
            padx=(0, 10),
        )

        cards.label(
            left,
            "Desde",
            font_role="small",
            background="surface_alt",
        ).pack(side=tk.LEFT)

        inputs.make_entry(
            left,
            textvariable=self.start_date,
            width=12,
        ).pack(
            side=tk.LEFT,
            padx=(6, 12),
        )

        cards.label(
            left,
            "Hasta",
            font_role="small",
            background="surface_alt",
        ).pack(side=tk.LEFT)

        inputs.make_entry(
            left,
            textvariable=self.end_date,
            width=12,
        ).pack(
            side=tk.LEFT,
            padx=(6, 12),
        )

        AppButton(
            left,
            "Actualizar",
            command=self.refresh,
            variant="primary",
            tooltip="Vuelve a calcular los indicadores del rango indicado",
        ).pack(side=tk.LEFT)

        self.cash_badge = cards.Badge(
            right,
            text="CAJA SIN ABRIR",
            tone="warn",
        )
        self.cash_badge.pack(
            side=tk.LEFT,
            padx=(0, 10),
        )

        self.open_cash_button = AppButton(
            right,
            "Abrir caja",
            command=self.open_cash,
            variant="success",
            tooltip="Registra el monto inicial de la caja",
        )
        self.open_cash_button.pack(
            side=tk.LEFT,
            padx=4,
        )

        self.close_cash_button = AppButton(
            right,
            "Cerrar caja",
            command=self.close_cash,
            variant="danger",
            tooltip="Cuadra el efectivo y cierra el turno",
        )
        self.close_cash_button.pack(
            side=tk.LEFT,
            padx=4,
        )

    def _build_metrics(self) -> None:
        row = ctk.CTkFrame(self.frame)
        theme.remember(
            row,
            "plain",
            bg="window",
            fg="text",
        )

        row.pack(
            fill=tk.X,
            padx=12,
            pady=(0, 12),
        )

        self.metrics = {
            "sales": cards.MetricCard(
                row,
                "Ventas del rango",
                tone="accent",
            ),
            "invoices": cards.MetricCard(
                row,
                "Facturas",
                tone="accent_dark",
            ),
            "taxes": cards.MetricCard(
                row,
                "Impuestos (ITBIS)",
                tone="warning",
            ),
            "receivables": cards.MetricCard(
                row,
                "Por cobrar",
                tone="danger",
            ),
            "cash": cards.MetricCard(
                row,
                "Efectivo en caja",
                tone="success",
            ),
        }

        for metric in self.metrics.values():
            metric.pack(
                side=tk.LEFT,
                fill=tk.BOTH,
                expand=True,
                padx=4,
            )

    def _build_cash_panel(self, content: tk.Misc) -> None:
        card = cards.Card(
            content,
            title="Caja y movimientos de efectivo",
            padding=14,
        )

        card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )

        body = card.body

        self.cash_info_var = tk.StringVar(value="No hay una caja abierta.")

        info = tk.Label(
            body,
            textvariable=self.cash_info_var,
            anchor="w",
            justify=tk.LEFT,
            wraplength=520,
            font=theme.font("body"),
        )

        theme.remember(
            info,
            "label",
            bg="surface",
            fg="text",
        )

        info.pack(
            fill=tk.X,
            pady=(0, 8),
        )

        form = ctk.CTkFrame(body)
        theme.remember(
            form,
            "plain",
            bg="surface",
            fg="text",
        )

        form.pack(fill=tk.X)

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        _, self.kind_combo = inputs.labeled_combobox(
            form,
            "Tipo",
            values=("GASTO", "RETIRO", "INGRESO"),
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
            values=(
                "EFECTIVO",
                "TARJETA",
                "TRANSFERENCIA",
                "OTRO",
            ),
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
        )

        actions = ctk.CTkFrame(body)
        theme.remember(
            actions,
            "plain",
            bg="surface",
            fg="text",
        )

        actions.pack(
            fill=tk.X,
            pady=(8, 10),
        )

        self.save_button = AppButton(
            actions,
            "Guardar movimiento",
            command=self.save_movement,
            variant="success",
            tooltip="Registra el movimiento en la caja abierta",
        )

        self.save_button.pack(side=tk.LEFT)

        AppButton(
            actions,
            "Limpiar",
            command=self.clear_form,
            variant="neutral",
        ).pack(
            side=tk.LEFT,
            padx=6,
        )

        self.totals_badge = cards.Badge(
            actions,
            text="Ingresos RD$ 0.00  |  Egresos RD$ 0.00",
            tone="neutral",
        )

        self.totals_badge.pack(side=tk.RIGHT)

        self.movements_button = AppButton(
            actions,
            "Ver movimientos",
            command=self.open_movements,
            variant="primary",
            tooltip="Abre el listado completo de movimientos de caja",
        )

        self.movements_button.pack(
            side=tk.RIGHT,
            padx=6,
        )

    def _build_side_panels(self, content: tk.Misc) -> None:
        column = ctk.CTkFrame(content)
        theme.remember(
            column,
            "plain",
            bg="window",
            fg="text",
        )

        column.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
        )

        column.rowconfigure(0, weight=1)
        column.rowconfigure(1, weight=1)
        column.columnconfigure(0, weight=1)

        products_card = cards.Card(
            column,
            title="Productos más vendidos",
            padding=12,
        )

        products_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            pady=(0, 8),
        )

        self.products_table = tables.DataTable(
            products_card.body,
            columns=(
                "Código",
                "Producto",
                "Unidades",
                "Ventas",
            ),
            widths=(
                100,
                220,
                90,
                120,
            ),
            anchors=(
                "w",
                "w",
                "e",
                "e",
            ),
            height=5,
        )

        self.products_table.pack(
            fill=tk.BOTH,
            expand=True,
        )

        receivables_card = cards.Card(
            column,
            title="Cuentas por cobrar",
            padding=12,
        )

        receivables_card.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        self.receivables_table = tables.DataTable(
            receivables_card.body,
            columns=(
                "Factura",
                "Cliente",
                "Total",
                "Saldo",
            ),
            widths=(
                110,
                200,
                110,
                110,
            ),
            anchors=(
                "w",
                "w",
                "e",
                "e",
            ),
            height=5,
        )

        self.receivables_table.pack(
            fill=tk.BOTH,
            expand=True,
        )

    # ------------------------------------------------------------------
    # Carga de datos
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Recarga indicadores, estado de caja y listados."""

        try:
            self.refresh_metrics()
            self.refresh_cash()
            self.refresh_products()
            self.refresh_receivables()

        except sqlite3.Error as exc:
            messagebox.showerror(
                "Dashboard",
                f"No se pudieron cargar los indicadores del negocio:\n{exc}",
                parent=self.frame,
            )

    def refresh_metrics(self) -> None:
        summary = sales_summary(
            self.connection,
            self.start_date.get(),
            self.end_date.get(),
        )

        self.metrics["sales"].set_value(f"RD$ {summary['total']:.2f}")

        self.metrics["invoices"].set_value(str(summary["facturas"]))

        self.metrics["taxes"].set_value(f"RD$ {summary['impuestos']:.2f}")

        pending = receivables(self.connection)

        pending_total = sum(float(row[5] or 0) for row in pending)

        self.metrics["receivables"].set_value(f"RD$ {pending_total:.2f}")

        self.metrics["receivables"].set_hint(
            "Sin facturas pendientes"
            if not pending
            else f"{len(pending)} factura(s) con saldo"
        )

    def refresh_products(self) -> None:
        rows = top_products(
            self.connection,
            self.start_date.get(),
            self.end_date.get(),
        )

        self.products_table.set_rows(
            rows,
            formats={
                3: "RD$ {:.2f}",
            },
        )

    def refresh_receivables(self) -> None:
        rows = receivables(self.connection)

        self.receivables_table.set_rows(
            [
                (
                    row[1],
                    row[2],
                    row[3],
                    row[5],
                )
                for row in rows
            ],
            formats={
                2: "RD$ {:.2f}",
                3: "RD$ {:.2f}",
            },
        )

    # ------------------------------------------------------------------
    # Caja
    # ------------------------------------------------------------------

    def open_cash_register(self):
        """Devuelve la caja abierta."""

        return self.connection.execute("""
            SELECT
                id,
                fecha_apertura,
                monto_inicial
            FROM cash_registers
            WHERE estado = 'ABIERTA'
            ORDER BY id DESC
            LIMIT 1
            """).fetchone()

    def expected_cash(
        self,
        cash_id: int,
        initial: float,
    ) -> float:
        """Calcula el efectivo esperado de la caja."""

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

            self.metrics["cash"].set_value("RD$ 0.00")

            self.metrics["cash"].set_hint("Caja cerrada")

            self.totals_badge.set(
                "Sin movimientos de caja",
                "neutral",
            )
            
            self.refresh_movements_table()
            self._set_form_enabled(False)
            return

        cash_id = int(cash[0])
        opened_at = cash[1] or ""
        initial = float(cash[2] or 0)

        expected = self.expected_cash(
            cash_id,
            initial,
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

        self.metrics["cash"].set_value(f"RD$ {expected:.2f}")

        self.metrics["cash"].set_hint(f"Apertura RD$ {initial:.2f} · Caja #{cash_id}")

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

        self.totals_badge.set(
            f"Ingresos RD$ {float(totals[0] or 0):.2f}  |  "
            f"Egresos RD$ {float(totals[1] or 0):.2f}",
            "info",
        )

        self.refresh_movements_table()
        self._set_form_enabled(self.can_manage_cash)
        
    def refresh_movements_table(self) -> None:
        """Recarga los movimientos en la ventana independiente."""

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

        cash_id = int(cash[0])

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

    def _set_form_enabled(
        self,
        enabled: bool,
    ) -> None:
        """Habilita o deshabilita el formulario."""

        state = "normal" if enabled else "disabled"

        self.amount_entry.configure(state=state)

        self.reference_entry.configure(state=state)

        self.kind_combo.configure(state=state)

        self.method_combo.configure(state=state)

        self.save_button.configure(state=state)

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def open_cash(self) -> None:
        """Delega la apertura de caja en la ventana principal."""

        if self.on_open_cash is None:
            messagebox.showinfo(
                "Caja",
                "La apertura de caja no está disponible " "en esta vista.",
                parent=self.frame,
            )
            return

        self.on_open_cash()
        self.refresh()

    def open_movements(self) -> None:
        """Abre el listado completo de movimientos de la caja."""

        if self.movements_window is not None and self.movements_window.winfo_exists():
            self.movements_window.focus_force()
            self.movements_window.lift()
            self.refresh_movements_table()
            return

        window = ctk.CTkToplevel(self.frame)

        self.movements_window = window

        window.title("Movimientos de caja")
        window.geometry("950x560")
        window.minsize(760, 420)

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

        container = ctk.CTkFrame(window)
        theme.remember(
            container,
            "plain",
            bg="window",
            fg="text",
        )

        container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=16,
            pady=16,
        )

        card = cards.Card(
            container,
            title="Movimientos de caja",
            subtitle="Historial de ingresos, gastos, retiros y ventas",
            padding=14,
        )

        card.pack(
            fill=tk.BOTH,
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
            state_tags={
                "VENTA": "info",
                "INGRESO": "ok",
                "RETIRO": "warn",
                "GASTO": "danger",
            },
        )

        self.movements_table.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.refresh_movements_table()

    def _close_movements_window(self) -> None:
        """Cierra la ventana de movimientos y libera sus referencias."""

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

    def close_cash(self) -> None:
        """Delega el cierre de caja en la ventana principal."""

        if self.on_close_cash is None:
            messagebox.showinfo(
                "Caja",
                "El cierre de caja no está disponible " "en esta vista.",
                parent=self.frame,
            )
            return

        self.on_close_cash()
        self.refresh()

    def clear_form(self) -> None:
        self.amount.set("")
        self.reference.set("")

    def focus_movement_form(self) -> None:
        """Coloca el foco en el monto."""

        try:
            self.amount_entry.focus_set()
        except tk.TclError:
            pass

    def save_movement(self) -> None:
        """Registra un movimiento manual en la caja abierta."""

        try:
            amount = float(self.amount.get().replace(",", "."))
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
                "Debe abrir una caja antes de registrar movimientos.",
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
