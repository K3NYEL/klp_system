import tkinter as tk
from tkinter import ttk
from datetime import date

from app.core.reports import receivables, sales_summary, top_products


class DashboardView:
    def __init__(self, parent, connection):
        self.parent = parent
        self.connection = connection
        self.frame = tk.Frame(parent, bg="white")
        self.start_date = tk.StringVar(value=date.today().replace(day=1).isoformat())
        self.end_date = tk.StringVar(value=date.today().isoformat())
        self.metric_vars = {key: tk.StringVar(value="0") for key in ("sales", "invoices", "taxes", "receivables")}
        self._build()
        self.refresh()

    def _build(self):
        toolbar = tk.Frame(self.frame, bg="white")
        toolbar.pack(fill=tk.X, padx=18, pady=14)
        tk.Label(toolbar, text="Desde", bg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Entry(toolbar, textvariable=self.start_date, width=12).pack(side=tk.LEFT, padx=6)
        tk.Label(toolbar, text="Hasta", bg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Entry(toolbar, textvariable=self.end_date, width=12).pack(side=tk.LEFT, padx=6)
        tk.Button(toolbar, text="Actualizar", command=self.refresh, bg="#0984e3", fg="white", cursor="hand2").pack(side=tk.LEFT, padx=10)

        cards = tk.Frame(self.frame, bg="white")
        cards.pack(fill=tk.X, padx=18)
        labels = (("Ventas", "sales"), ("Facturas", "invoices"), ("Impuestos", "taxes"), ("Por cobrar", "receivables"))
        for title, key in labels:
            card = tk.LabelFrame(cards, text=title, bg="white", padx=18, pady=12)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            tk.Label(card, textvariable=self.metric_vars[key], bg="white", fg="#0984e3", font=("Arial", 16, "bold")).pack()

        content = tk.Frame(self.frame, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
        left = tk.LabelFrame(content, text="Productos más vendidos", bg="white", padx=8, pady=8)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.products_tree = ttk.Treeview(left, columns=("Código", "Producto", "Unidades", "Ventas"), show="headings")
        for column in ("Código", "Producto", "Unidades", "Ventas"):
            self.products_tree.heading(column, text=column)
        self.products_tree.pack(fill=tk.BOTH, expand=True)

        right = tk.LabelFrame(content, text="Cuentas por cobrar", bg="white", padx=8, pady=8)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        self.receivables_tree = ttk.Treeview(right, columns=("Factura", "Cliente", "Total", "Saldo"), show="headings")
        for column in ("Factura", "Cliente", "Total", "Saldo"):
            self.receivables_tree.heading(column, text=column)
        self.receivables_tree.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        summary = sales_summary(self.connection, self.start_date.get(), self.end_date.get())
        self.metric_vars["sales"].set(f"RD$ {summary['total']:.2f}")
        self.metric_vars["invoices"].set(str(summary["facturas"]))
        self.metric_vars["taxes"].set(f"RD$ {summary['impuestos']:.2f}")
        self.metric_vars["receivables"].set(f"RD$ {sum(row[5] for row in receivables(self.connection)):.2f}")

        for tree in (self.products_tree, self.receivables_tree):
            for item in tree.get_children():
                tree.delete(item)
        for row in top_products(self.connection, self.start_date.get(), self.end_date.get()):
            self.products_tree.insert("", tk.END, values=(row[0], row[1], row[2], f"RD$ {row[3]:.2f}"))
        for row in receivables(self.connection):
            self.receivables_tree.insert("", tk.END, values=(row[1], row[2], f"RD$ {row[3]:.2f}", f"RD$ {row[5]:.2f}"))
