"""Vista de movimientos de inventario.

Permite registrar entradas, ajustes y devoluciones de productos,
además de consultar los últimos movimientos registrados.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Any, Optional

import customtkinter as ctk

from app.core.inventory import register_movement
from app.ui import theme
from app.ui.components import cards, inputs, tables
from app.ui.components.buttons import AppButton


class InventoryMovementView:
    """Panel de movimientos de inventario."""

    def __init__(
        self,
        parent: tk.Misc,
        connection: Any,
        actor_id: Optional[int] = None,
    ) -> None:
        self.parent = parent
        self.connection = connection
        self.actor_id = actor_id

        self.product = tk.StringVar()
        self.kind = tk.StringVar(value="ENTRADA")
        self.quantity = tk.StringVar(value="1")
        self.reason = tk.StringVar()

        self.products: dict[str, int] = {}

        self.frame = ctk.CTkFrame(parent)

        theme.remember(
            self.frame,
            "plain",
            bg="window",
            fg="text",
        )

        self._build()
        self.refresh()

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------

    def _build(self) -> None:
        self._build_form()
        self._build_table()

    def _build_form(self) -> None:
        card = cards.Card(
            self.frame,
            title="Registrar movimiento de inventario",
            padding=14,
        )

        card.pack(
            fill=tk.X,
            padx=16,
            pady=(16, 10),
        )

        body = card.body

        form = ctk.CTkFrame(body)

        theme.remember(
            form,
            "plain",
            bg="surface",
            fg="text",
        )

        form.pack(
            fill=tk.X,
        )

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        # Producto
        _, self.product_combo = inputs.labeled_combobox(
            form,
            "Producto",
            values=(),
            textvariable=self.product,
            width=260,
            row=0,
            column=0,
            label_column=0,
            entry_column=1,
            entry_sticky="ew",
        )

        # Tipo
        _, self.kind_combo = inputs.labeled_combobox(
            form,
            "Tipo",
            values=(
                "ENTRADA",
                "AJUSTE",
                "DEVOLUCION",
            ),
            textvariable=self.kind,
            width=150,
            row=0,
            column=2,
            label_column=2,
            entry_column=3,
            entry_sticky="ew",
        )

        # Cantidad
        _, self.quantity_entry = inputs.labeled_entry(
            form,
            "Cantidad",
            textvariable=self.quantity,
            width=100,
            row=1,
            column=0,
            label_column=0,
            entry_column=1,
            entry_sticky="ew",
        )

        # Motivo
        _, self.reason_entry = inputs.labeled_entry(
            form,
            "Motivo",
            textvariable=self.reason,
            width=260,
            row=1,
            column=2,
            label_column=2,
            entry_column=3,
            entry_sticky="ew",
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
            pady=(12, 0),
        )

        self.save_button = AppButton(
            actions,
            "Guardar movimiento",
            command=self.save,
            variant="success",
            tooltip="Registra el movimiento de inventario",
        )

        self.save_button.pack(
            side=tk.LEFT,
        )

        AppButton(
            actions,
            "Limpiar",
            command=self.clear_form,
            variant="neutral",
        ).pack(
            side=tk.LEFT,
            padx=6,
        )

    def _build_table(self) -> None:
        card = cards.Card(
            self.frame,
            title="Últimos movimientos",
            padding=14,
        )

        card.pack(
            fill=tk.BOTH,
            expand=True,
            padx=16,
            pady=(0, 16),
        )

        self.tree = tables.DataTable(
            card.body,
            columns=(
                "Fecha",
                "Producto",
                "Tipo",
                "Cantidad",
                "Motivo",
            ),
            widths=(
                150,
                220,
                120,
                100,
                260,
            ),
            anchors=(
                "w",
                "w",
                "w",
                "e",
                "w",
            ),
            height=12,
            state_tags={
                "ENTRADA": "ok",
                "AJUSTE": "warn",
                "DEVOLUCION": "info",
            },
        )

        self.tree.pack(
            fill=tk.BOTH,
            expand=True,
        )

    # ------------------------------------------------------------------
    # Datos
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Recarga productos y movimientos."""

        self._refresh_products()
        self._refresh_movements()

    def _refresh_products(self) -> None:
        self.products.clear()

        rows = self.connection.execute("""
            SELECT id, codigo, nombre
            FROM productos
            WHERE activo = 1
            ORDER BY nombre
            """)

        values = []

        for row in rows:
            label = f"{row[1]} - {row[2]}"

            self.products[label] = int(row[0])
            values.append(label)

        self.product_combo.configure(
            values=values,
        )

        # Si el producto seleccionado ya no existe,
        # limpiamos la selección.
        if self.product.get() not in self.products:
            self.product.set("")

    def _refresh_movements(self) -> None:
        rows = self.connection.execute("""
            SELECT
                m.fecha,
                p.nombre,
                m.tipo,
                m.cantidad,
                COALESCE(m.motivo, '')
            FROM inventory_movements m
            JOIN productos p
                ON p.id = m.producto_id
            ORDER BY m.id DESC
            LIMIT 100
            """).fetchall()

        self.tree.set_rows(
            rows,
        )

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def clear_form(self) -> None:
        """Limpia los campos del formulario."""

        self.product.set("")
        self.kind.set("ENTRADA")
        self.quantity.set("1")
        self.reason.set("")

    def save(self) -> None:
        """Registra un movimiento de inventario."""

        try:
            product_id = self.products[self.product.get()]

            quantity = int(self.quantity.get().strip())

            if quantity <= 0:
                raise ValueError("La cantidad debe ser mayor que cero.")

            reason = self.reason.get().strip()

            register_movement(
                self.connection,
                product_id,
                self.kind.get(),
                quantity,
                reason,
                self.actor_id,
            )

        except KeyError:
            messagebox.showerror(
                "Inventario",
                "Debe seleccionar un producto.",
                parent=self.frame,
            )
            return

        except ValueError as exc:
            messagebox.showerror(
                "Inventario",
                str(exc),
                parent=self.frame,
            )
            return

        except Exception as exc:
            messagebox.showerror(
                "Inventario",
                f"No se pudo registrar el movimiento:\n{exc}",
                parent=self.frame,
            )
            return

        self.clear_form()
        self.refresh()

        messagebox.showinfo(
            "Inventario",
            "Movimiento registrado correctamente.",
            parent=self.frame,
        )

    def focus_product(self) -> None:
        """Coloca el foco en el selector de producto."""

        try:
            self.product_combo.focus_set()
        except tk.TclError:
            pass
