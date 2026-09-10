import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from app.core.inventory import register_movement


class InventoryMovementView:
    def __init__(self, parent, connection, actor_id):
        self.connection = connection
        self.actor_id = actor_id
        self.window = tk.Toplevel(parent)
        self.window.title("Movimientos de inventario")
        self.window.geometry("720x430")
        self._build()
        self.refresh()

    def _build(self):
        form = tk.LabelFrame(self.window, text="Registrar entrada o ajuste", padx=10, pady=10)
        form.pack(fill=tk.X, padx=12, pady=12)
        self.product = tk.StringVar()
        self.kind = tk.StringVar(value="ENTRADA")
        self.quantity = tk.StringVar(value="1")
        self.reason = tk.StringVar()
        self.products = {}
        tk.Label(form, text="Producto").grid(row=0, column=0, padx=5)
        self.product_combo = ttk.Combobox(form, textvariable=self.product, state="readonly", width=32)
        self.product_combo.grid(row=0, column=1, padx=5)
        ttk.Combobox(form, textvariable=self.kind, state="readonly", values=("ENTRADA", "AJUSTE", "DEVOLUCION"), width=14).grid(row=0, column=2, padx=5)
        tk.Entry(form, textvariable=self.quantity, width=8).grid(row=0, column=3, padx=5)
        tk.Entry(form, textvariable=self.reason, width=22).grid(row=0, column=4, padx=5)
        tk.Button(form, text="Guardar", command=self.save, bg="#27ae60", fg="white").grid(row=0, column=5, padx=5)
        tk.Label(form, text="Cantidad / Motivo").grid(row=1, column=3, columnspan=2)

        self.tree = ttk.Treeview(self.window, columns=("Fecha", "Producto", "Tipo", "Cantidad", "Motivo"), show="headings")
        for column in ("Fecha", "Producto", "Tipo", "Cantidad", "Motivo"):
            self.tree.heading(column, text=column)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=5)

    def refresh(self):
        self.products.clear()
        self.product_combo["values"] = ()
        for row in self.connection.execute("SELECT id, codigo, nombre FROM productos WHERE activo=1 ORDER BY nombre"):
            label = f"{row[1]} - {row[2]}"
            self.products[label] = row[0]
        self.product_combo["values"] = tuple(self.products)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in self.connection.execute(
            """SELECT m.fecha, p.nombre, m.tipo, m.cantidad, m.motivo
               FROM inventory_movements m JOIN productos p ON p.id=m.producto_id
               ORDER BY m.id DESC LIMIT 100"""
        ):
            self.tree.insert("", tk.END, values=row)

    def save(self):
        try:
            product_id = self.products[self.product.get()]
            register_movement(self.connection, product_id, self.kind.get(), int(self.quantity.get()), self.reason.get(), self.actor_id)
            self.quantity.set("1")
            self.reason.set("")
            self.refresh()
            messagebox.showinfo("Inventario", "Movimiento registrado.", parent=self.window)
        except (KeyError, ValueError) as exc:
            messagebox.showerror("Inventario", str(exc), parent=self.window)
