import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class CashMovementView:
    def __init__(self, parent, connection, actor_id):
        self.connection = connection
        self.actor_id = actor_id
        self.window = tk.Toplevel(parent)
        self.window.title("Movimientos de caja")
        self.window.geometry("720x400")
        self._build()
        self.refresh()

    def _build(self):
        form = tk.LabelFrame(self.window, text="Registrar movimiento", padx=10, pady=10)
        form.pack(fill=tk.X, padx=12, pady=12)
        self.kind = tk.StringVar(value="GASTO")
        self.amount = tk.StringVar()
        self.method = tk.StringVar(value="EFECTIVO")
        self.reference = tk.StringVar()
        ttk.Combobox(form, textvariable=self.kind, state="readonly", values=("GASTO", "RETIRO", "INGRESO"), width=12).pack(side=tk.LEFT, padx=5)
        tk.Entry(form, textvariable=self.amount, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Combobox(form, textvariable=self.method, state="readonly", values=("EFECTIVO", "TARJETA", "TRANSFERENCIA", "OTRO"), width=15).pack(side=tk.LEFT, padx=5)
        tk.Entry(form, textvariable=self.reference, width=25).pack(side=tk.LEFT, padx=5)
        tk.Button(form, text="Guardar", command=self.save, bg="#27ae60", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Label(self.window, text="Tipo / Monto / Método / Referencia").pack()

        self.tree = ttk.Treeview(self.window, columns=("Fecha", "Tipo", "Monto", "Método", "Referencia"), show="headings")
        for column in ("Fecha", "Tipo", "Monto", "Método", "Referencia"):
            self.tree.heading(column, text=column)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.connection.execute("SELECT id FROM cash_registers WHERE estado='ABIERTA' LIMIT 1")
        if not self.connection.fetchone():
            return
        for row in self.connection.execute(
            """SELECT fecha, tipo, monto, metodo_pago, COALESCE(referencia, '')
               FROM cash_movements ORDER BY id DESC LIMIT 100"""
        ):
            self.tree.insert("", tk.END, values=row)

    def save(self):
        try:
            amount = float(self.amount.get())
            if amount <= 0:
                raise ValueError("El monto debe ser mayor que cero.")
            cash = self.connection.execute("SELECT id FROM cash_registers WHERE estado='ABIERTA' LIMIT 1").fetchone()
            if not cash:
                raise ValueError("Debe abrir una caja primero.")
            self.connection.execute(
                """INSERT INTO cash_movements (caja_id, tipo, monto, metodo_pago, referencia, usuario_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (cash[0], self.kind.get(), amount, self.method.get(), self.reference.get().strip(), self.actor_id),
            )
            self.connection.commit()
            self.amount.set("")
            self.reference.set("")
            self.refresh()
        except ValueError as exc:
            messagebox.showerror("Caja", str(exc), parent=self.window)
