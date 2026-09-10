import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import hashlib
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter  # type: ignore[reportMissingModuleSource]
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer  # type: ignore[reportMissingModuleSource]
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore[reportMissingModuleSource]
from reportlab.lib import colors  # type: ignore[reportMissingModuleSource]

# ``inch`` is a fixed ReportLab unit (72 points).  Defining it locally avoids
inch = 72
import os
import sys
import webbrowser
from datetime import datetime
import os
import logging
from xml.sax.saxutils import escape

from app.auth.login_window import LoginWindow
from app.core.database import audit, connect_database
from app.core.backup import create_backup, restore_backup
from app.auth.authorization import can
from app.core.paths import application_path
from app.core.ui import INPUT_STYLE, CREATOR_URL, configure_app_style, set_app_icon
from app.ui.dashboard_view import DashboardView
from app.ui.cash_view import CashMovementView
from app.ui.inventory_view import InventoryMovementView
from app.ui.user_management_view import UserManagementView
from app.services import customers_service, invoice_service, products_service


class SistemaFacturacion:
    def __init__(self, root, on_logout=None, current_user=None):
        self.root = root
        self.on_logout = on_logout
        self.current_user = current_user or {}
        self.tabs = {}
        self.root.title("Sistema de Facturacion")
        self.base_path = self.get_base_path()
        set_app_icon(self.root, self.base_path)
        self.root.geometry("1200x700")
        if sys.platform == "win32":
            self.root.state("zoomed")
        self.root.configure(bg="#f0f0f0")
        self.root.protocol("WM_DELETE_WINDOW", self.salir)
        configure_app_style()

        # Inicializar base de datos
        self.init_db()

        # Variables para la factura actual
        self.items_factura = []
        self.total_factura = 0

        # Crear interfaz
        self.crear_interfaz()
        self.cargar_datos()

    def init_db(self):
        """Abre la base y aplica las migraciones centralizadas."""
        try:
            db_path = os.path.join(self.base_path, "facturacion.db")
            self.conn = connect_database(db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            messagebox.showerror(
                "Error de Base de Datos",
                f"Error al inicializar la base de datos: {str(e)}",
            )
            if hasattr(self, "conn"):
                self.conn.close()
            raise

    def get_base_path(self):
        return application_path()

    def center_window(self, width, height, window=None):
        if window is None:
            window = self.root
        window.update_idletasks()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def crear_pestaña_admin(self):
        """Crea la pestaña de configuración de la empresa"""
        tab = tk.Frame(self.notebook, bg="white")
        self.empresa_tab = tab
        self.tabs["company"] = tab
        self.notebook.add(tab, text="  Empresa  ")

        form_frame = tk.Frame(tab, bg="white", relief=tk.RIDGE, bd=2)
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            form_frame,
            text="Datos que aparecerán en la factura",
            font=("Arial", 14, "bold"),
            bg="white",
        ).grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(
            form_frame, text="Nombre de la empresa:", bg="white", font=("Arial", 10)
        ).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.empresa_nombre_var = tk.StringVar()
        tk.Entry(
            form_frame,
            textvariable=self.empresa_nombre_var,
            width=50,
            font=("Arial", 10),
        ).grid(row=1, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="RNC:", bg="white", font=("Arial", 10)).grid(
            row=2, column=0, padx=10, pady=5, sticky="e"
        )
        self.empresa_rnc_var = tk.StringVar()
        tk.Entry(
            form_frame, textvariable=self.empresa_rnc_var, width=30, font=("Arial", 10)
        ).grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form_frame, text="Dirección:", bg="white", font=("Arial", 10)).grid(
            row=3, column=0, padx=10, pady=5, sticky="e"
        )
        self.empresa_direccion_var = tk.StringVar()
        tk.Entry(
            form_frame,
            textvariable=self.empresa_direccion_var,
            width=50,
            font=("Arial", 10),
        ).grid(row=3, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Teléfono:", bg="white", font=("Arial", 10)).grid(
            row=4, column=0, padx=10, pady=5, sticky="e"
        )
        self.empresa_telefono_var = tk.StringVar()
        tk.Entry(
            form_frame,
            textvariable=self.empresa_telefono_var,
            width=30,
            font=("Arial", 10),
        ).grid(row=4, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form_frame, text="Email:", bg="white", font=("Arial", 10)).grid(
            row=5, column=0, padx=10, pady=5, sticky="e"
        )
        self.empresa_email_var = tk.StringVar()
        tk.Entry(
            form_frame,
            textvariable=self.empresa_email_var,
            width=50,
            font=("Arial", 10),
        ).grid(row=5, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Sitio web:", bg="white", font=("Arial", 10)).grid(
            row=6, column=0, padx=10, pady=5, sticky="e"
        )
        self.empresa_website_var = tk.StringVar()
        tk.Entry(
            form_frame,
            textvariable=self.empresa_website_var,
            width=50,
            font=("Arial", 10),
        ).grid(row=6, column=1, padx=10, pady=5)

        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=15)

        tk.Button(
            btn_frame,
            text="Guardar empresa",
            command=self.guardar_empresa,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            width=24,
            cursor="hand2",
        ).pack()

    def cargar_empresa(self):
        self.cursor.execute(
            "SELECT nombre, rnc, direccion, telefono, email, website FROM empresa WHERE id = 1"
        )
        row = self.cursor.fetchone()
        if row:
            self.empresa_nombre_var.set(row[0] or "")
            self.empresa_rnc_var.set(row[1] or "")
            self.empresa_direccion_var.set(row[2] or "")
            self.empresa_telefono_var.set(row[3] or "")
            self.empresa_email_var.set(row[4] or "")
            self.empresa_website_var.set(row[5] or "")
        else:
            self.empresa_nombre_var.set("")
            self.empresa_rnc_var.set("")
            self.empresa_direccion_var.set("")
            self.empresa_telefono_var.set("")
            self.empresa_email_var.set("")
            self.empresa_website_var.set("")

    def guardar_empresa(self):
        if not self.require_permission("manage_company"):
            return
        nombre = self.empresa_nombre_var.get().strip()
        rnc = self.empresa_rnc_var.get().strip()
        direccion = self.empresa_direccion_var.get().strip()
        telefono = self.empresa_telefono_var.get().strip()
        email = self.empresa_email_var.get().strip()
        website = self.empresa_website_var.get().strip()

        self.cursor.execute("SELECT id FROM empresa WHERE id = 1")
        if self.cursor.fetchone():
            self.cursor.execute(
                """
                UPDATE empresa
                SET nombre=?, rnc=?, direccion=?, telefono=?, email=?, website=?
                WHERE id = 1
            """,
                (nombre, rnc, direccion, telefono, email, website),
            )
        else:
            self.cursor.execute(
                """
                INSERT INTO empresa (id, nombre, rnc, direccion, telefono, email, website)
                VALUES (1, ?, ?, ?, ?, ?, ?)
            """,
                (nombre, rnc, direccion, telefono, email, website),
            )

        self.conn.commit()
        messagebox.showinfo("Éxito", "Información de la empresa guardada correctamente")

    def crear_interfaz(self):
        """Crea la interfaz principal con pestañas"""
        menu_bar = tk.Menu(self.root)
        archivo_menu = tk.Menu(menu_bar, tearoff=0)
        archivo_menu.add_command(label="Cerrar sesión", command=self.cerrar_sesion)
        archivo_menu.add_command(
            label="Crear copia de seguridad", command=self.crear_backup
        )
        archivo_menu.add_command(
            label="Restaurar copia de seguridad", command=self.restaurar_backup
        )
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.salir)
        menu_bar.add_cascade(label="Archivo", menu=archivo_menu)

        caja_menu = tk.Menu(menu_bar, tearoff=0)
        caja_menu.add_command(label="Abrir caja", command=self.abrir_caja)
        caja_menu.add_command(label="Cerrar caja", command=self.cerrar_caja)
        caja_menu.add_command(
            label="Movimiento manual", command=self.abrir_movimiento_caja
        )
        menu_bar.add_cascade(label="Caja", menu=caja_menu)

        opciones_menu = tk.Menu(menu_bar, tearoff=0)
        opciones_menu.add_command(
            label="Nueva factura",
            command=lambda: self.seleccionar_seccion("invoice"),
            accelerator="Ctrl+N",
        )
        opciones_menu.add_command(
            label="Facturación rápida",
            command=self.abrir_facturacion_rapida,
            accelerator="F2",
        )
        opciones_menu.add_command(
            label="Dashboard", command=lambda: self.seleccionar_seccion("dashboard")
        )
        opciones_menu.add_command(
            label="Movimientos de inventario", command=self.abrir_movimientos_inventario
        )
        opciones_menu.add_command(label="Usuarios", command=self.abrir_usuarios)
        opciones_menu.add_command(
            label="Inventario",
            command=lambda: self.seleccionar_seccion("products"),
            accelerator="Ctrl+I",
        )
        opciones_menu.add_command(
            label="Clientes",
            command=lambda: self.seleccionar_seccion("customers"),
            accelerator="Ctrl+L",
        )
        opciones_menu.add_command(label="Mi empresa", command=self.ir_mi_empresa)
        opciones_menu.add_command(
            label="Facturas guardadas",
            command=lambda: self.seleccionar_seccion("history"),
            accelerator="Ctrl+H",
        )
        opciones_menu.add_separator()
        opciones_menu.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        menu_bar.add_cascade(label="Opciones", menu=opciones_menu)

        ayuda_menu = tk.Menu(menu_bar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        menu_bar.add_cascade(label="Ayuda", menu=ayuda_menu)

        self.root.config(menu=menu_bar)
        self._registrar_atajos()

        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        self.crear_pestaña_facturacion()
        self.crear_pestaña_productos()
        self.crear_pestaña_clientes()
        self.crear_pestaña_admin()
        self.crear_pestaña_historial()
        dashboard = DashboardView(self.notebook, self.conn)
        self.dashboard = dashboard
        self.tabs["dashboard"] = dashboard.frame
        self.notebook.add(dashboard.frame, text="  Dashboard  ")

    def seleccionar_pestaña(self, index):
        """Activa una sección desde el menú principal."""
        self.notebook.select(index)

    def seleccionar_seccion(self, name):
        tab = self.tabs.get(name)
        if tab is not None:
            self.notebook.select(tab)
            if name == "dashboard" and hasattr(self, "dashboard"):
                self.dashboard.refresh()

    def _registrar_atajos(self):
        """Registra atajos globales para que funcionen con cualquier control enfocado."""
        shortcuts = {
            "n": "invoice",
            "i": "products",
            "l": "customers",
            "h": "history",
        }
        for key, tab_index in shortcuts.items():
            self.root.bind_all(
                f"<Control-KeyPress-{key}>",
                lambda event, section=tab_index: self._atajo_pestaña(event, section),
                add="+",
            )
            self.root.bind_all("<F2>", self._atajo_facturacion_rapida, add="+")

    def _atajo_pestaña(self, event, section):
        """Cambia de sección y consume el evento para evitar interferencias del widget."""
        self.seleccionar_seccion(section)
        self.root.focus_set()
        return "break"

    def _atajo_facturacion_rapida(self, event):
        self.abrir_facturacion_rapida()
        return "break"

    def abrir_facturacion_rapida(self):
        """Abre una venta de mostrador para escanear y cobrar sin registrar cliente."""
        if not self.require_permission("create_invoices"):
            return
        if getattr(self, "quick_window", None) and self.quick_window.winfo_exists():
            self.quick_window.deiconify()
            self.quick_code_entry.focus_set()
            return

        window = tk.Toplevel(self.root)
        self.quick_window = window
        window.title("Facturación rápida")
        set_app_icon(window, self.base_path)
        window.geometry("720x520")
        window.configure(bg="#f0f0f0")
        window.transient(self.root)

        header = tk.Frame(window, bg="#0984e3")
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="FACTURACIÓN RÁPIDA",
            bg="#0984e3",
            fg="white",
            font=("Arial", 18, "bold"),
        ).pack(pady=(14, 2))
        tk.Label(
            header,
            text="Escanea el código, confirma el pago y entrega el ticket",
            bg="#0984e3",
            fg="white",
            font=("Arial", 10),
        ).pack(pady=(0, 14))

        scan_frame = tk.Frame(window, bg="white", padx=14, pady=12)
        scan_frame.pack(fill=tk.X, padx=12, pady=12)
        tk.Label(
            scan_frame,
            text="Código de barras / SKU",
            bg="white",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT)
        self.quick_code_var = tk.StringVar()
        self.quick_code_entry = tk.Entry(
            scan_frame,
            textvariable=self.quick_code_var,
            font=("Arial", 13),
            width=28,
            **INPUT_STYLE,
        )
        self.quick_code_entry.pack(side=tk.LEFT, padx=10)
        self.quick_quantity_var = tk.StringVar(value="1")
        tk.Label(
            scan_frame, text="Cantidad", bg="white", font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT)
        tk.Entry(
            scan_frame,
            textvariable=self.quick_quantity_var,
            width=6,
            font=("Arial", 12),
            **INPUT_STYLE,
        ).pack(side=tk.LEFT, padx=8)
        tk.Button(
            scan_frame,
            text="Agregar",
            command=self.agregar_item_rapido,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
        ).pack(side=tk.LEFT)
        self.quick_code_entry.bind("<Return>", lambda event: self.agregar_item_rapido())

        table_frame = tk.Frame(window, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=12)
        self.quick_tree = ttk.Treeview(
            table_frame,
            columns=("Código", "Producto", "Cantidad", "Precio", "Total"),
            show="headings",
            height=12,
        )
        for column in ("Código", "Producto", "Cantidad", "Precio", "Total"):
            self.quick_tree.heading(column, text=column)
        self.quick_tree.column("Código", width=120)
        self.quick_tree.column("Producto", width=260)
        self.quick_tree.column("Cantidad", width=80)
        self.quick_tree.column("Precio", width=100)
        self.quick_tree.column("Total", width=100)
        self.quick_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        footer = tk.Frame(window, bg="#f0f0f0", padx=12, pady=10)
        footer.pack(fill=tk.X)
        self.quick_total_var = tk.StringVar(value="Total: RD$ 0.00")
        tk.Label(
            footer,
            textvariable=self.quick_total_var,
            bg="#f0f0f0",
            fg="#27ae60",
            font=("Arial", 15, "bold"),
        ).pack(side=tk.LEFT)
        self.quick_payment_var = tk.StringVar(value="EFECTIVO")
        ttk.Combobox(
            footer,
            textvariable=self.quick_payment_var,
            values=("EFECTIVO", "TARJETA", "TRANSFERENCIA", "OTRO"),
            state="readonly",
            width=16,
        ).pack(side=tk.LEFT, padx=18)
        tk.Button(
            footer,
            text="Quitar seleccionado",
            command=self.eliminar_item_rapido,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
        ).pack(side=tk.RIGHT, padx=5)
        tk.Button(
            footer,
            text="Cobrar e imprimir ticket",
            command=self.confirmar_factura_rapida,
            bg="#0984e3",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
        ).pack(side=tk.RIGHT, padx=5)
        self.quick_items = []
        window.protocol("WM_DELETE_WINDOW", window.destroy)
        window.after(100, self.quick_code_entry.focus_set)

    def agregar_item_rapido(self):
        code = self.quick_code_var.get().strip()
        if not code:
            return
        try:
            quantity = int(self.quick_quantity_var.get())
            if quantity <= 0:
                raise ValueError("La cantidad debe ser mayor que cero")
            self.cursor.execute(
                "SELECT codigo, nombre, precio, stock FROM productos "
                "WHERE activo=1 AND (codigo=? OR codigo_barras=?) LIMIT 1",
                (code, code),
            )
            product = self.cursor.fetchone()
            if not product:
                messagebox.showwarning(
                    "Producto no encontrado",
                    f"No existe un producto con código: {code}",
                    parent=self.quick_window,
                )
                return
            existing = next(
                (item for item in self.quick_items if item["codigo"] == product[0]),
                None,
            )
            current_quantity = existing["cantidad"] if existing else 0
            if current_quantity + quantity > product[3]:
                raise ValueError(f"Stock insuficiente. Disponible: {product[3]}")
            if existing:
                existing["cantidad"] += quantity
                existing["subtotal"] = existing["cantidad"] * existing["precio"]
            else:
                self.quick_items.append(
                    {
                        "codigo": product[0],
                        "nombre": product[1],
                        "precio": product[2],
                        "cantidad": quantity,
                        "subtotal": product[2] * quantity,
                    }
                )
            self._refrescar_factura_rapida()
            self.quick_code_var.set("")
            self.quick_quantity_var.set("1")
            self.quick_code_entry.focus_set()
        except ValueError as exc:
            messagebox.showwarning("Validación", str(exc), parent=self.quick_window)

    def _refrescar_factura_rapida(self):
        for row in self.quick_tree.get_children():
            self.quick_tree.delete(row)
        total = 0
        for item in self.quick_items:
            total += item["subtotal"]
            self.quick_tree.insert(
                "",
                tk.END,
                values=(
                    item["codigo"],
                    item["nombre"],
                    item["cantidad"],
                    f"RD$ {item['precio']:.2f}",
                    f"RD$ {item['subtotal']:.2f}",
                ),
            )
        self.quick_total_var.set(f"Total: RD$ {total:.2f}")

    def eliminar_item_rapido(self):
        selected = self.quick_tree.selection()
        if selected:
            del self.quick_items[self.quick_tree.index(selected[0])]
            self._refrescar_factura_rapida()

    def confirmar_factura_rapida(self):
        if not self.quick_items:
            messagebox.showwarning(
                "Venta vacía", "Escanea al menos un producto.", parent=self.quick_window
            )
            return
        payment = self.quick_payment_var.get()
        invoice_number = self.generar_numero_factura()
        pdf_path = None
        try:
            self.cursor.execute(
                "SELECT id FROM clientes WHERE nombre=? LIMIT 1", ("CONSUMIDOR FINAL",)
            )
            customer = self.cursor.fetchone()
            if not customer:
                self.cursor.execute(
                    "INSERT INTO clientes (nombre, cedula) VALUES (?, NULL)",
                    ("CONSUMIDOR FINAL",),
                )
                customer_id = self.cursor.lastrowid
            else:
                customer_id = customer[0]
            subtotal = sum(item["subtotal"] for item in self.quick_items)
            tax = round(subtotal * 0.18, 2)
            total = round(subtotal + tax, 2)
            user_id = self.current_user.get("id")
            self.cursor.execute(
                """INSERT INTO facturas (numero, fecha, cliente_id, subtotal, itbis, total, estado, metodo_pago, usuario_id)
                   VALUES (?, DATE('now'), ?, ?, ?, ?, 'PAGADA', ?, ?)""",
                (invoice_number, customer_id, subtotal, tax, total, payment, user_id),
            )
            invoice_id = self.cursor.lastrowid
            self.cursor.execute(
                "SELECT id FROM payment_methods WHERE nombre=?", (payment,)
            )
            payment_method = self.cursor.fetchone()
            if not payment_method:
                raise ValueError("Método de pago no válido")
            for item in self.quick_items:
                self.cursor.execute(
                    "SELECT id, stock FROM productos WHERE codigo=?", (item["codigo"],)
                )
                product_id, stock = self.cursor.fetchone()
                self.cursor.execute(
                    "UPDATE productos SET stock=stock-? WHERE id=? AND stock>=?",
                    (item["cantidad"], product_id, item["cantidad"]),
                )
                if self.cursor.rowcount != 1:
                    raise ValueError(f"Stock insuficiente para {item['nombre']}")
                self.cursor.execute(
                    "INSERT INTO factura_items (factura_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (
                        invoice_id,
                        product_id,
                        item["cantidad"],
                        item["precio"],
                        item["subtotal"],
                    ),
                )
                self.cursor.execute(
                    "INSERT INTO inventory_movements (producto_id, tipo, cantidad, motivo, referencia, usuario_id) VALUES (?, 'SALIDA', ?, 'Venta rápida', ?, ?)",
                    (product_id, -item["cantidad"], invoice_number, user_id),
                )
            self.cursor.execute(
                "INSERT INTO payments (factura_id, metodo_id, monto, usuario_id) VALUES (?, ?, ?, ?)",
                (invoice_id, payment_method[0], total, user_id),
            )
            self.cursor.execute(
                "SELECT id FROM cash_registers WHERE estado='ABIERTA' ORDER BY id DESC LIMIT 1"
            )
            cash = self.cursor.fetchone()
            if not cash:
                raise ValueError("Debe abrir una caja antes de vender")
            self.cursor.execute(
                "INSERT INTO cash_movements (caja_id, tipo, monto, metodo_pago, referencia, usuario_id) VALUES (?, 'VENTA', ?, ?, ?, ?)",
                (cash[0], total, payment, invoice_number, user_id),
            )
            audit(
                self.conn,
                "CREAR_FACTURA_RAPIDA",
                "facturas",
                invoice_id,
                invoice_number,
                user_id,
            )
            pdf_path = self.generar_pdf(invoice_id)
            self.conn.commit()
            self.quick_items.clear()
            self._refrescar_factura_rapida()
            self.cargar_productos()
            self.cargar_historial()
            messagebox.showinfo(
                "Venta completada",
                f"Ticket generado correctamente:\n{pdf_path}",
                parent=self.quick_window,
            )
            self.quick_code_entry.focus_set()
        except Exception as exc:
            self.conn.rollback()
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)
            messagebox.showerror(
                "Error en venta rápida", str(exc), parent=self.quick_window
            )

    def require_permission(self, permission):
        if can(self.current_user.get("role"), permission):
            return True
        messagebox.showwarning(
            "Permiso insuficiente",
            "Su usuario no tiene permisos para realizar esta operación.",
        )
        return False

    def ir_mi_empresa(self):
        empresa_win = tk.Toplevel(self.root)
        empresa_win.title("Mi Empresa")
        set_app_icon(empresa_win, self.base_path)
        empresa_win.geometry("640x420")
        empresa_win.configure(bg="#f0f0f0")
        empresa_win.transient(self.root)
        empresa_win.grab_set()
        self.center_window(640, 420, window=empresa_win)

        container = tk.Frame(
            empresa_win,
            bg="white",
            relief=tk.RIDGE,
            bd=0,
            highlightbackground="#dfe6e9",
            highlightthickness=1,
        )
        container.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
        container.columnconfigure(1, weight=1)

        tk.Label(
            container,
            text="Datos de mi empresa",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#2d3436",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(18, 12))

        fields = [
            ("Nombre de la empresa", self.empresa_nombre_var),
            ("RNC", self.empresa_rnc_var),
            ("Dirección", self.empresa_direccion_var),
            ("Teléfono", self.empresa_telefono_var),
            ("Email", self.empresa_email_var),
            ("Sitio web", self.empresa_website_var),
        ]

        for index, (label, variable) in enumerate(fields, start=1):
            tk.Label(
                container, text=label, bg="white", font=("Arial", 10, "bold")
            ).grid(row=index, column=0, padx=20, pady=6, sticky="w")
            tk.Entry(
                container, textvariable=variable, font=("Arial", 10), **INPUT_STYLE
            ).grid(row=index, column=1, padx=(0, 20), pady=6, sticky="ew")

        btn_frame = tk.Frame(container, bg="white")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=(18, 16))

        tk.Button(
            btn_frame,
            text="Guardar datos",
            command=self.guardar_empresa,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            width=18,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            btn_frame,
            text="Cerrar",
            command=empresa_win.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=6)

    def cerrar_sesion(self):
        if messagebox.askyesno(
            "Cerrar sesión", "¿Desea cerrar sesión y volver al login?"
        ):
            self.root.destroy()
            if self.on_logout:
                self.on_logout()

    def salir(self):
        if messagebox.askyesno("Salir", "¿Desea salir del sistema?"):
            self.root.destroy()

    def crear_backup(self):
        if not self.require_permission("manage_company"):
            return
        try:
            backup_dir = os.path.join(self.base_path, "backups")
            backup_path = create_backup(
                os.path.join(self.base_path, "facturacion.db"), backup_dir
            )
            self.cursor.execute(
                "INSERT INTO backups (ruta) VALUES (?)", (str(backup_path),)
            )
            audit(
                self.conn,
                "CREAR_BACKUP",
                "backups",
                self.cursor.lastrowid,
                str(backup_path),
            )
            self.conn.commit()
            messagebox.showinfo(
                "Copia de seguridad", f"Backup creado correctamente:\n{backup_path}"
            )
        except Exception as exc:
            messagebox.showerror(
                "Error de backup", f"No se pudo crear la copia de seguridad:\n{exc}"
            )

    def abrir_usuarios(self):
        if self.require_permission("manage_users"):
            UserManagementView(self.root, self.conn, self.current_user.get("id"))

    def abrir_movimientos_inventario(self):
        if self.require_permission("manage_products"):
            InventoryMovementView(self.root, self.conn, self.current_user.get("id"))

    def abrir_movimiento_caja(self):
        if self.require_permission("manage_cash"):
            CashMovementView(self.root, self.conn, self.current_user.get("id"))

    def restaurar_backup(self):
        if not self.require_permission("manage_company"):
            return
        backup_path = filedialog.askopenfilename(
            title="Seleccionar copia de seguridad",
            initialdir=os.path.join(self.base_path, "backups"),
            filetypes=(("Bases SQLite", "*.db"), ("Todos los archivos", "*.*")),
        )
        if not backup_path:
            return
        if not messagebox.askyesno(
            "Restaurar copia",
            "Se guardará una copia de la base actual antes de restaurar. ¿Continuar?",
        ):
            return
        database_path = os.path.join(self.base_path, "facturacion.db")
        try:
            self.conn.close()
            restore_backup(
                backup_path, database_path, os.path.join(self.base_path, "backups")
            )
            self.conn = connect_database(database_path)
            self.cursor = self.conn.cursor()
            self.cargar_datos()
            self.dashboard.refresh()
            messagebox.showinfo(
                "Restauración", "La copia de seguridad fue restaurada correctamente."
            )
        except Exception as exc:
            try:
                self.conn = connect_database(database_path)
                self.cursor = self.conn.cursor()
            except sqlite3.Error:
                pass
            messagebox.showerror("Error de restauración", str(exc))

    def abrir_caja(self):
        if not self.require_permission("manage_cash"):
            return
        self.cursor.execute("SELECT id FROM cash_registers WHERE estado='ABIERTA'")
        if self.cursor.fetchone():
            messagebox.showwarning("Caja", "Ya existe una caja abierta.")
            return
        amount = simpledialog.askfloat(
            "Abrir caja", "Monto inicial:", minvalue=0, parent=self.root
        )
        if amount is None:
            return
        self.cursor.execute(
            "INSERT INTO cash_registers (usuario_apertura, monto_inicial) VALUES (?, ?)",
            (self.current_user.get("id"), amount),
        )
        caja_id = self.cursor.lastrowid
        audit(
            self.conn,
            "ABRIR_CAJA",
            "cash_registers",
            caja_id,
            f"{amount:.2f}",
            self.current_user.get("id"),
        )
        self.conn.commit()
        messagebox.showinfo("Caja", "Caja abierta correctamente.")

    def cerrar_caja(self):
        if not self.require_permission("manage_cash"):
            return
        self.cursor.execute(
            "SELECT id, monto_inicial FROM cash_registers WHERE estado='ABIERTA' ORDER BY id DESC LIMIT 1"
        )
        cash = self.cursor.fetchone()
        if not cash:
            messagebox.showwarning("Caja", "No hay una caja abierta.")
            return
        self.cursor.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo IN ('VENTA', 'INGRESO') THEN monto ELSE -monto END), 0) "
            "FROM cash_movements WHERE caja_id=? AND (tipo <> 'VENTA' OR metodo_pago='EFECTIVO')",
            (cash[0],),
        )
        expected = round(cash[1] + self.cursor.fetchone()[0], 2)
        counted = simpledialog.askfloat(
            "Cerrar caja",
            f"Efectivo esperado: RD$ {expected:.2f}\nMonto contado:",
            minvalue=0,
            parent=self.root,
        )
        if counted is None:
            return
        difference = round(counted - expected, 2)
        self.cursor.execute(
            """UPDATE cash_registers SET fecha_cierre=CURRENT_TIMESTAMP,
               monto_esperado=?, monto_contado=?, diferencia=?, estado='CERRADA' WHERE id=?""",
            (expected, counted, difference, cash[0]),
        )
        audit(
            self.conn,
            "CERRAR_CAJA",
            "cash_registers",
            cash[0],
            f"Diferencia: {difference:.2f}",
            self.current_user.get("id"),
        )
        self.conn.commit()
        messagebox.showinfo("Caja", f"Caja cerrada. Diferencia: RD$ {difference:.2f}")

    def mostrar_acerca_de(self):
        about = tk.Toplevel(self.root)
        about.title("Acerca de")
        set_app_icon(about, self.base_path)
        about.resizable(False, False)
        about.configure(bg="#f0f0f0")
        about.geometry("400x240")
        self.center_window(400, 240, window=about)
        about.transient(self.root)
        about.grab_set()
        about.attributes("-topmost", True)
        about.after(100, lambda: about.attributes("-topmost", False))
        about.focus_force()

        tk.Label(
            about,
            text="Sistema de Facturación",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0",
        ).pack(pady=(20, 8))
        tk.Label(
            about,
            text="Versión 1.0\nDesarrollado por K.A.R.M.",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#555",
        ).pack()

        link = tk.Label(
            about,
            text=CREATOR_URL,
            font=("Arial", 10, "underline"),
            fg="#0984e3",
            bg="#f0f0f0",
            cursor="hand2",
        )
        link.pack(pady=12)
        link.bind("<Button-1>", lambda event: webbrowser.open_new_tab(CREATOR_URL))

        tk.Button(
            about,
            text="Cerrar",
            command=about.destroy,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            activebackground="#2980b9",
            activeforeground="white",
            width=12,
            cursor="hand2",
            relief=tk.FLAT,
        ).pack(pady=(10, 16))

    def crear_pestaña_facturacion(self):
        """Crea la pestaña de facturación"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="  Crear Factura  ")
        self.tabs["invoice"] = tab

        # Canvas con scrollbar que envuelve todo
        main_canvas = tk.Canvas(tab, bg="white", highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(
            tab, orient="vertical", command=main_canvas.yview
        )
        main_canvas.configure(yscrollcommand=main_scrollbar.set)

        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(main_canvas, bg="white")
        win = main_canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_frame_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))

        def on_canvas_configure(event):
            main_canvas.itemconfig(win, width=event.width)

        inner.bind("<Configure>", on_frame_configure)
        main_canvas.bind("<Configure>", on_canvas_configure)

        # Frame unificado
        unified_frame = tk.LabelFrame(
            inner,
            text="  Factura  ",
            bg="white",
            fg="#2d3436",
            font=("Arial", 11, "bold"),
            padx=16,
            pady=12,
        )
        unified_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        unified_frame.columnconfigure(1, weight=1)
        unified_frame.columnconfigure(3, weight=1)

        # --- Datos del comprobante ---
        tk.Label(
            unified_frame, text="Factura No.", font=("Arial", 10, "bold"), bg="white"
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.num_factura = tk.StringVar(value=self.generar_numero_factura())
        tk.Entry(
            unified_frame,
            textvariable=self.num_factura,
            state="readonly",
            width=20,
            font=("Arial", 10),
        ).grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(
            unified_frame, text="Fecha", font=("Arial", 10, "bold"), bg="white"
        ).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.fecha_factura = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        tk.Entry(
            unified_frame,
            textvariable=self.fecha_factura,
            state="readonly",
            width=15,
            font=("Arial", 10),
        ).grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        tk.Label(
            unified_frame, text="Cliente", font=("Arial", 10, "bold"), bg="white"
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.cliente_var = tk.StringVar()
        self.combo_cliente = ttk.Combobox(
            unified_frame, textvariable=self.cliente_var, width=40, font=("Arial", 10)
        )
        self.combo_cliente.grid(
            row=1, column=1, columnspan=3, padx=10, pady=5, sticky="ew"
        )

        tk.Label(
            unified_frame, text="Método de pago", font=("Arial", 10, "bold"), bg="white"
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.metodo_pago_var = tk.StringVar(value="EFECTIVO")
        self.combo_metodo_pago = ttk.Combobox(
            unified_frame,
            textvariable=self.metodo_pago_var,
            values=("EFECTIVO", "TARJETA", "TRANSFERENCIA", "CREDITO", "OTRO"),
            state="readonly",
            width=20,
        )
        self.combo_metodo_pago.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Separador
        ttk.Separator(unified_frame, orient="horizontal").grid(
            row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=6
        )

        # --- Agregar producto ---
        tk.Label(
            unified_frame, text="Producto", bg="white", font=("Arial", 10, "bold")
        ).grid(row=4, column=0, padx=5, pady=5)
        self.producto_var = tk.StringVar()
        self.combo_producto = ttk.Combobox(
            unified_frame, textvariable=self.producto_var, width=35, font=("Arial", 10)
        )
        self.combo_producto.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.combo_producto.bind("<<ComboboxSelected>>", self.seleccionar_producto)

        tk.Label(
            unified_frame, text="Precio", bg="white", font=("Arial", 10, "bold")
        ).grid(row=4, column=2, padx=5, pady=5)
        self.precio_var = tk.StringVar()
        tk.Entry(
            unified_frame, textvariable=self.precio_var, width=12, font=("Arial", 10)
        ).grid(row=4, column=3, padx=5, pady=5, sticky="w")

        tk.Label(
            unified_frame, text="Cantidad", bg="white", font=("Arial", 10, "bold")
        ).grid(row=5, column=0, padx=5, pady=5)
        self.cantidad_var = tk.StringVar(value="1")
        tk.Entry(
            unified_frame, textvariable=self.cantidad_var, width=10, font=("Arial", 10)
        ).grid(row=5, column=1, padx=5, pady=5, sticky="w")

        tk.Button(
            unified_frame,
            text="Agregar producto",
            command=self.agregar_item,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
        ).grid(row=5, column=3, padx=10, pady=5, sticky="e")

        # Separador
        ttk.Separator(unified_frame, orient="horizontal").grid(
            row=6, column=0, columnspan=4, sticky="ew", padx=5, pady=6
        )

        # --- Tabla de productos ---
        table_frame = tk.Frame(unified_frame, bg="white")
        table_frame.grid(row=7, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        table_frame.columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview para items
        self.tree_items = ttk.Treeview(
            table_frame,
            columns=("Código", "Producto", "Cantidad", "Precio", "Subtotal"),
            show="headings",
            height=6,
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self.tree_items.yview)

        self.tree_items.heading("Código", text="Código")
        self.tree_items.heading("Producto", text="Producto")
        self.tree_items.heading("Cantidad", text="Cantidad")
        self.tree_items.heading("Precio", text="Precio Unit.")
        self.tree_items.heading("Subtotal", text="Subtotal")

        self.tree_items.column("Código", width=140, minwidth=100, stretch=False)
        self.tree_items.column("Producto", width=420, minwidth=220, stretch=True)
        self.tree_items.column("Cantidad", width=110, minwidth=80, stretch=False)
        self.tree_items.column("Precio", width=140, minwidth=100, stretch=False)
        self.tree_items.column("Subtotal", width=150, minwidth=110, stretch=False)

        self.tree_items.pack(fill=tk.BOTH, expand=True)

        # Separador
        ttk.Separator(unified_frame, orient="horizontal").grid(
            row=8, column=0, columnspan=4, sticky="ew", padx=5, pady=6
        )

        # --- Totales en fila horizontal ---
        totals_row = tk.Frame(unified_frame, bg="white")
        totals_row.grid(
            row=9, column=0, columnspan=4, sticky="ew", padx=10, pady=(4, 2)
        )
        totals_row.columnconfigure(1, weight=1)

        tk.Label(
            totals_row, text="Subtotal:", font=("Arial", 11, "bold"), bg="white"
        ).pack(side=tk.LEFT, padx=(0, 4))
        self.subtotal_var = tk.StringVar(value="RD$ 0.00")
        tk.Label(
            totals_row, textvariable=self.subtotal_var, font=("Arial", 11), bg="white"
        ).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            totals_row, text="ITBIS (18%):", font=("Arial", 11, "bold"), bg="white"
        ).pack(side=tk.LEFT, padx=(0, 4))
        self.itbis_var = tk.StringVar(value="RD$ 0.00")
        tk.Label(
            totals_row, textvariable=self.itbis_var, font=("Arial", 11), bg="white"
        ).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            totals_row,
            text="TOTAL:",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#27ae60",
        ).pack(side=tk.LEFT, padx=(0, 4))
        self.total_var = tk.StringVar(value="RD$ 0.00")
        tk.Label(
            totals_row,
            textvariable=self.total_var,
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#27ae60",
        ).pack(side=tk.LEFT)

        # --- Botones ---
        btn_frame = tk.Frame(unified_frame, bg="white")
        btn_frame.grid(row=10, column=0, columnspan=4, pady=(4, 6))

        tk.Button(
            btn_frame,
            text="Guardar factura y crear PDF",
            command=self.generar_factura,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            width=23,
            height=1,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            btn_frame,
            text="Limpiar y crear nueva factura",
            command=self.nueva_factura,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10, "bold"),
            width=23,
            height=1,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            btn_frame,
            text="Eliminar producto",
            command=self.eliminar_item,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            width=23,
            height=1,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=6)

    def crear_pestaña_productos(self):
        """Crea la pestaña de gestión de productos"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="  Inventario  ")
        self.tabs["products"] = tab

        # Frame para formulario
        form_frame = tk.Frame(tab, bg="white", relief=tk.RIDGE, bd=2)
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            form_frame,
            text="Inventario de productos",
            font=("Arial", 14, "bold"),
            bg="white",
        ).grid(row=0, column=0, columnspan=4, pady=10)

        # Campos del formulario
        tk.Label(form_frame, text="Código:", bg="white", font=("Arial", 10)).grid(
            row=1, column=0, padx=10, pady=5, sticky="e"
        )
        self.prod_codigo = tk.Entry(form_frame, width=20, font=("Arial", 10))
        self.prod_codigo.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Nombre:", bg="white", font=("Arial", 10)).grid(
            row=1, column=2, padx=10, pady=5, sticky="e"
        )
        self.prod_nombre = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.prod_nombre.grid(row=1, column=3, padx=10, pady=5)

        tk.Label(form_frame, text="Precio:", bg="white", font=("Arial", 10)).grid(
            row=2, column=0, padx=10, pady=5, sticky="e"
        )
        self.prod_precio = tk.Entry(form_frame, width=20, font=("Arial", 10))
        self.prod_precio.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Stock:", bg="white", font=("Arial", 10)).grid(
            row=2, column=2, padx=10, pady=5, sticky="e"
        )
        self.prod_stock = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.prod_stock.grid(row=2, column=3, padx=10, pady=5)

        # Botones
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)

        tk.Button(
            btn_frame,
            text="Agregar",
            command=self.agregar_producto,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Actualizar",
            command=self.actualizar_producto,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Eliminar",
            command=self.eliminar_producto,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Limpiar",
            command=self.limpiar_form_producto,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        # Frame para búsqueda
        search_frame = tk.Frame(tab, bg="white")
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            search_frame,
            text="Buscar por código o nombre:",
            bg="white",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, padx=5)
        self.prod_buscar = tk.Entry(search_frame, width=40, font=("Arial", 10))
        self.prod_buscar.pack(side=tk.LEFT, padx=5)
        self.prod_buscar.bind("<KeyRelease>", lambda e: self.cargar_productos())

        # Frame para tabla
        table_frame = tk.Frame(tab, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_productos = ttk.Treeview(
            table_frame,
            columns=("ID", "Código", "Nombre", "Precio", "Stock"),
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self.tree_productos.yview)

        self.tree_productos.heading("ID", text="ID")
        self.tree_productos.heading("Código", text="Código")
        self.tree_productos.heading("Nombre", text="Nombre")
        self.tree_productos.heading("Precio", text="Precio")
        self.tree_productos.heading("Stock", text="Stock")

        self.tree_productos.column("ID", width=50)
        self.tree_productos.column("Código", width=100)
        self.tree_productos.column("Nombre", width=300)
        self.tree_productos.column("Precio", width=100)
        self.tree_productos.column("Stock", width=100)

        self.tree_productos.pack(fill=tk.BOTH, expand=True)
        self.tree_productos.bind("<ButtonRelease-1>", self.seleccionar_producto_tabla)

    def crear_pestaña_clientes(self):
        """Crea la pestaña de gestión de clientes"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="  Clientes  ")
        self.tabs["customers"] = tab

        # Frame para formulario
        form_frame = tk.Frame(tab, bg="white", relief=tk.RIDGE, bd=2)
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            form_frame,
            text="Registro de clientes",
            font=("Arial", 14, "bold"),
            bg="white",
        ).grid(row=0, column=0, columnspan=4, pady=10)

        # Campos del formulario
        tk.Label(form_frame, text="Nombre:", bg="white", font=("Arial", 10)).grid(
            row=1, column=0, padx=10, pady=5, sticky="e"
        )
        self.cli_nombre = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.cli_nombre.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Cédula:", bg="white", font=("Arial", 10)).grid(
            row=1, column=2, padx=10, pady=5, sticky="e"
        )
        self.cli_cedula = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.cli_cedula.grid(row=1, column=3, padx=10, pady=5)

        tk.Label(form_frame, text="Teléfono:", bg="white", font=("Arial", 10)).grid(
            row=2, column=0, padx=10, pady=5, sticky="e"
        )
        self.cli_telefono = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.cli_telefono.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Dirección:", bg="white", font=("Arial", 10)).grid(
            row=2, column=2, padx=10, pady=5, sticky="e"
        )
        self.cli_direccion = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.cli_direccion.grid(row=2, column=3, padx=10, pady=5)

        # Botones
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)

        tk.Button(
            btn_frame,
            text="Agregar",
            command=self.agregar_cliente,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Actualizar",
            command=self.actualizar_cliente,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Desactivar",
            command=self.eliminar_cliente,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Limpiar",
            command=self.limpiar_form_cliente,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        # Frame para búsqueda
        search_frame = tk.Frame(tab, bg="white")
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            search_frame,
            text="Buscar por nombre o cédula:",
            bg="white",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, padx=5)
        self.cli_buscar = tk.Entry(search_frame, width=40, font=("Arial", 10))
        self.cli_buscar.pack(side=tk.LEFT, padx=5)
        self.cli_buscar.bind("<KeyRelease>", lambda e: self.cargar_clientes())

        # Frame para tabla
        table_frame = tk.Frame(tab, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_clientes = ttk.Treeview(
            table_frame,
            columns=("ID", "Nombre", "Cédula", "Teléfono", "Dirección"),
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self.tree_clientes.yview)

        self.tree_clientes.heading("ID", text="ID")
        self.tree_clientes.heading("Nombre", text="Nombre")
        self.tree_clientes.heading("Cédula", text="Cédula")
        self.tree_clientes.heading("Teléfono", text="Teléfono")
        self.tree_clientes.heading("Dirección", text="Dirección")

        self.tree_clientes.column("ID", width=50)
        self.tree_clientes.column("Nombre", width=200)
        self.tree_clientes.column("Cédula", width=120)
        self.tree_clientes.column("Teléfono", width=120)
        self.tree_clientes.column("Dirección", width=300)

        self.tree_clientes.pack(fill=tk.BOTH, expand=True)
        self.tree_clientes.bind("<ButtonRelease-1>", self.seleccionar_cliente_tabla)

    def crear_pestaña_historial(self):
        """Crea la pestaña de historial de facturas"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="  Facturas guardadas  ")
        self.tabs["history"] = tab

        # Frame para búsqueda
        search_frame = tk.Frame(tab, bg="white")
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            search_frame,
            text="Buscar factura o cliente:",
            bg="white",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, padx=5)
        self.hist_buscar = tk.Entry(search_frame, width=30, font=("Arial", 10))
        self.hist_buscar.pack(side=tk.LEFT, padx=5)
        self.hist_buscar.bind("<KeyRelease>", lambda e: self.cargar_historial())

        tk.Button(
            search_frame,
            text="Ver detalles",
            command=self.ver_detalles_factura,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            search_frame,
            text="Crear PDF de nuevo",
            command=self.regenerar_pdf,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            search_frame,
            text="Registrar abono",
            command=self.registrar_abono,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            search_frame,
            text="Anular factura",
            command=self.anular_factura,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=5)

        # Frame para tabla
        table_frame = tk.Frame(tab, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_historial = ttk.Treeview(
            table_frame,
            columns=(
                "ID",
                "Número",
                "Fecha",
                "Cliente",
                "Subtotal",
                "ITBIS",
                "Total",
                "Estado",
            ),
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self.tree_historial.yview)

        self.tree_historial.heading("ID", text="ID")
        self.tree_historial.heading("Número", text="Número")
        self.tree_historial.heading("Fecha", text="Fecha")
        self.tree_historial.heading("Cliente", text="Cliente")
        self.tree_historial.heading("Subtotal", text="Subtotal")
        self.tree_historial.heading("ITBIS", text="ITBIS")
        self.tree_historial.heading("Total", text="Total")
        self.tree_historial.heading("Estado", text="Estado")

        self.tree_historial.column("ID", width=50)
        self.tree_historial.column("Número", width=120)
        self.tree_historial.column("Fecha", width=100)
        self.tree_historial.column("Cliente", width=250)
        self.tree_historial.column("Subtotal", width=100)
        self.tree_historial.column("ITBIS", width=100)
        self.tree_historial.column("Total", width=100)
        self.tree_historial.column("Estado", width=100)

        self.tree_historial.pack(fill=tk.BOTH, expand=True)

    # Métodos de Productos
    def agregar_producto(self):
        if not self.require_permission("manage_products"):
            return
        codigo = self.prod_codigo.get().strip()
        nombre = self.prod_nombre.get().strip()
        precio = self.prod_precio.get().strip()
        stock = self.prod_stock.get().strip()

        if not all([codigo, nombre, precio, stock]):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return

        try:
            precio = float(precio)
            stock = int(stock)
            if precio <= 0:
                raise ValueError("El precio debe ser mayor a 0")
            if stock < 0:
                raise ValueError("El stock no puede ser negativo")

            products_service.create_product(
                self.conn, codigo, nombre, precio, stock, self.current_user.get("id")
            )
            messagebox.showinfo("Éxito", "Producto agregado correctamente")
            self.limpiar_form_producto()
            self.cargar_productos()
            self.cargar_datos()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El código del producto ya existe")
        except ValueError:
            messagebox.showerror("Error", "Precio y Stock deben ser números válidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar producto: {str(e)}")

    def eliminar_producto(self):
        if not self.require_permission("manage_products"):
            return
        selected = self.tree_productos.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto de la tabla")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?"):
            item = self.tree_productos.item(selected[0])
            producto_id = item["values"][0]

            try:
                products_service.deactivate_product(
                    self.conn, producto_id, self.current_user.get("id")
                )
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                self.limpiar_form_producto()
                self.cargar_productos()
                self.cargar_datos()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar producto: {str(e)}")

    def limpiar_form_producto(self):
        self.prod_codigo.delete(0, tk.END)
        self.prod_nombre.delete(0, tk.END)
        self.prod_precio.delete(0, tk.END)
        self.prod_stock.delete(0, tk.END)

    def seleccionar_producto_tabla(self, event):
        selected = self.tree_productos.selection()
        if selected:
            item = self.tree_productos.item(selected[0])
            values = item["values"]

            self.prod_codigo.delete(0, tk.END)
            self.prod_codigo.insert(0, values[1])

            self.prod_nombre.delete(0, tk.END)
            self.prod_nombre.insert(0, values[2])

            self.prod_precio.delete(0, tk.END)
            self.prod_precio.insert(0, values[3])

            self.prod_stock.delete(0, tk.END)
            self.prod_stock.insert(0, values[4])

    def cargar_productos(self):
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)

        for row in products_service.list_products(self.conn, self.prod_buscar.get()):
            self.tree_productos.insert("", tk.END, values=row)

    # Métodos de Clientes
    def agregar_cliente(self):
        if not self.require_permission("manage_customers"):
            return
        nombre = self.cli_nombre.get().strip()
        cedula = self.cli_cedula.get().strip()
        telefono = self.cli_telefono.get().strip()
        direccion = self.cli_direccion.get().strip()

        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return

        try:
            customers_service.create_customer(
                self.conn,
                nombre,
                cedula,
                telefono,
                direccion,
                self.current_user.get("id"),
            )
            messagebox.showinfo("Éxito", "Cliente agregado correctamente")
            self.limpiar_form_cliente()
            self.cargar_clientes()
            self.cargar_datos()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "La cédula ya está registrada")
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar cliente: {str(e)}")

    def actualizar_cliente(self):
        if not self.require_permission("manage_customers"):
            return
        selected = self.tree_clientes.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un cliente de la tabla")
            return

        item = self.tree_clientes.item(selected[0])
        cliente_id = item["values"][0]

        nombre = self.cli_nombre.get().strip()
        cedula = self.cli_cedula.get().strip()
        telefono = self.cli_telefono.get().strip()
        direccion = self.cli_direccion.get().strip()

        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return

        try:
            customers_service.update_customer(
                self.conn,
                cliente_id,
                nombre,
                cedula,
                telefono,
                direccion,
                self.current_user.get("id"),
            )
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
            self.limpiar_form_cliente()
            self.cargar_clientes()
            self.cargar_datos()

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar cliente: {str(e)}")

    def eliminar_cliente(self):
        if not self.require_permission("manage_customers"):
            return
        selected = self.tree_clientes.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un cliente de la tabla")
            return

        if messagebox.askyesno(
            "Confirmar",
            "¿Está seguro de desactivar este cliente?\n\n"
            "Se conservará su historial de facturas.",
        ):
            item = self.tree_clientes.item(selected[0])
            cliente_id = item["values"][0]

            try:
                customers_service.deactivate_customer(
                    self.conn, cliente_id, self.current_user.get("id")
                )
                messagebox.showinfo(
                    "Éxito",
                    "Cliente desactivado correctamente. Su historial se conserva.",
                )
                self.limpiar_form_cliente()
                self.cargar_clientes()
                self.cargar_datos()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar cliente: {str(e)}")

    def limpiar_form_cliente(self):
        self.cli_nombre.delete(0, tk.END)
        self.cli_cedula.delete(0, tk.END)
        self.cli_telefono.delete(0, tk.END)
        self.cli_direccion.delete(0, tk.END)

    def actualizar_producto(self):
        if not self.require_permission("manage_products"):
            return
        selected = self.tree_productos.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto de la tabla")
            return

        item = self.tree_productos.item(selected[0])
        producto_id = item["values"][0]

        codigo = self.prod_codigo.get().strip()
        nombre = self.prod_nombre.get().strip()
        precio = self.prod_precio.get().strip()
        stock = self.prod_stock.get().strip()

        if not all([codigo, nombre, precio, stock]):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return

        try:
            precio = float(precio)
            if precio <= 0:
                raise ValueError("El precio debe ser mayor a 0")

            stock = int(stock)
            if stock < 0:
                raise ValueError("El stock no puede ser negativo")

            products_service.update_product(
                self.conn,
                producto_id,
                codigo,
                nombre,
                precio,
                stock,
                self.current_user.get("id"),
            )
            messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            self.limpiar_form_producto()
            self.cargar_productos()
            self.cargar_datos()

        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe otro producto con ese código")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar producto: {str(e)}")

    def seleccionar_cliente_tabla(self, event):
        selected = self.tree_clientes.selection()
        if selected:
            item = self.tree_clientes.item(selected[0])
            values = item["values"]

            self.cli_nombre.delete(0, tk.END)
            self.cli_nombre.insert(0, values[1])

            self.cli_cedula.delete(0, tk.END)
            self.cli_cedula.insert(0, values[2])

            self.cli_telefono.delete(0, tk.END)
            self.cli_telefono.insert(0, values[3])

            self.cli_direccion.delete(0, tk.END)
            self.cli_direccion.insert(0, values[4])

    def cargar_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)

        for row in customers_service.list_customers(self.conn, self.cli_buscar.get()):
            self.tree_clientes.insert("", tk.END, values=row)

    # Métodos de Facturación
    def generar_numero_factura(self):
        return invoice_service.next_invoice_number(self.conn)

    def seleccionar_producto(self, event):
        producto_str = self.producto_var.get()
        if not producto_str:
            return

        # Extraer código del producto (formato: "CODIGO - Nombre")
        codigo = producto_str.split(" - ")[0]

        self.cursor.execute("SELECT precio FROM productos WHERE codigo=?", (codigo,))
        result = self.cursor.fetchone()

        if result:
            self.precio_var.set(f"{result[0]:.2f}")

    def agregar_item(self):
        producto_str = self.producto_var.get()
        precio_str = self.precio_var.get()
        cantidad_str = self.cantidad_var.get()

        if not all([producto_str, precio_str, cantidad_str]):
            messagebox.showwarning("Advertencia", "Complete todos los campos")
            return

        try:
            precio = float(precio_str)
            if precio <= 0:
                raise ValueError("El precio debe ser mayor a 0")

            cantidad = int(cantidad_str)
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")

            # Extraer código y nombre
            if " - " not in producto_str:
                raise ValueError("Seleccione un producto válido de la lista")

            codigo, nombre = producto_str.split(" - ", 1)

            # Verificar stock disponible
            self.cursor.execute(
                "SELECT stock FROM productos WHERE codigo = ?", (codigo,)
            )
            stock_actual = self.cursor.fetchone()
            if not stock_actual:
                raise ValueError("Producto no encontrado")
            if stock_actual[0] < cantidad:
                raise ValueError(f"Stock insuficiente. Disponible: {stock_actual[0]}")

            for item in self.items_factura:
                if item["codigo"] == codigo:
                    nueva_cantidad = item["cantidad"] + cantidad
                    if nueva_cantidad > stock_actual[0]:
                        raise ValueError(
                            f"Stock insuficiente. Disponible: {stock_actual[0]}"
                        )
                    item["cantidad"] = nueva_cantidad
                    item["subtotal"] = item["precio"] * nueva_cantidad
                    self._refrescar_items_factura()
                    self.actualizar_totales()
                    self.producto_var.set("")
                    self.precio_var.set("")
                    self.cantidad_var.set("1")
                    return

            subtotal = precio * cantidad

            # Agregar a la tabla
            self.tree_items.insert(
                "",
                tk.END,
                values=(
                    codigo,
                    nombre,
                    cantidad,
                    f"RD$ {precio:.2f}",
                    f"RD$ {subtotal:.2f}",
                ),
            )

            # Agregar a lista interna
            self.items_factura.append(
                {
                    "codigo": codigo,
                    "nombre": nombre,
                    "cantidad": cantidad,
                    "precio": precio,
                    "subtotal": subtotal,
                }
            )

            # Actualizar totales
            self.actualizar_totales()

            # Limpiar campos
            self.producto_var.set("")
            self.precio_var.set("")
            self.cantidad_var.set("1")

        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar ítem: {str(e)}")

    def eliminar_item(self):
        selected = self.tree_items.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un item para eliminar")
            return

        # Obtener índice del item
        index = self.tree_items.index(selected[0])

        # Eliminar de la tabla visual
        self.tree_items.delete(selected[0])

        # Eliminar de la lista interna
        del self.items_factura[index]

        # Actualizar totales
        self.actualizar_totales()

    def _refrescar_items_factura(self):
        for item_id in self.tree_items.get_children():
            self.tree_items.delete(item_id)
        for item in self.items_factura:
            self.tree_items.insert(
                "",
                tk.END,
                values=(
                    item["codigo"],
                    item["nombre"],
                    item["cantidad"],
                    f"RD$ {item['precio']:.2f}",
                    f"RD$ {item['subtotal']:.2f}",
                ),
            )

    def actualizar_totales(self):
        subtotal = sum(item["subtotal"] for item in self.items_factura)
        itbis = subtotal * 0.18
        total = subtotal + itbis

        self.subtotal_var.set(f"RD$ {subtotal:.2f}")
        self.itbis_var.set(f"RD$ {itbis:.2f}")
        self.total_var.set(f"RD$ {total:.2f}")

    def generar_factura(self):
        if not self.require_permission("create_invoices"):
            return
        if not self.items_factura:
            messagebox.showwarning(
                "Advertencia", "Agregue al menos un producto a la factura"
            )
            return

        cliente_str = self.cliente_var.get()
        if not cliente_str:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return

        pdf_path = None
        try:
            # Obtener ID del cliente
            cliente_id = invoice_service.find_customer(self.conn, cliente_str)
            if cliente_id is None:
                messagebox.showerror("Error", "Cliente no encontrado")
                return

            # Calcular totales
            subtotal, itbis, total = invoice_service.calculate_totals(
                self.items_factura
            )

            # Insertar factura
            numero = self.num_factura.get()
            fecha = invoice_service.invoice_date()
            metodo_pago = self.metodo_pago_var.get() or "EFECTIVO"
            estado = "PENDIENTE" if metodo_pago == "CREDITO" else "PAGADA"
            usuario_id = self.current_user.get("id")

            self.cursor.execute(
                """
                INSERT INTO facturas (numero, fecha, cliente_id, subtotal, itbis, total,
                                      estado, metodo_pago, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    numero,
                    fecha,
                    cliente_id,
                    subtotal,
                    itbis,
                    total,
                    estado,
                    metodo_pago,
                    usuario_id,
                ),
            )

            factura_id = self.cursor.lastrowid

            # Insertar items de la factura
            for item in self.items_factura:
                # Obtener ID del producto
                self.cursor.execute(
                    "SELECT id FROM productos WHERE codigo=?", (item["codigo"],)
                )
                producto_id = self.cursor.fetchone()[0]

                self.cursor.execute(
                    """
                    INSERT INTO factura_items (factura_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        factura_id,
                        producto_id,
                        item["cantidad"],
                        item["precio"],
                        item["subtotal"],
                    ),
                )

                # Actualizar stock
                self.cursor.execute(
                    """
                    UPDATE productos
                    SET stock = stock - ?
                    WHERE id = ? AND stock >= ?
                """,
                    (item["cantidad"], producto_id, item["cantidad"]),
                )
                if self.cursor.rowcount != 1:
                    raise ValueError(
                        f"Stock insuficiente para el producto {item['codigo']}"
                    )
                self.cursor.execute(
                    """INSERT INTO inventory_movements
                       (producto_id, tipo, cantidad, motivo, referencia, usuario_id)
                       VALUES (?, 'SALIDA', ?, ?, ?, ?)""",
                    (producto_id, -item["cantidad"], "Venta", numero, usuario_id),
                )

            if metodo_pago != "CREDITO":
                self.cursor.execute(
                    "SELECT id FROM payment_methods WHERE nombre=?", (metodo_pago,)
                )
                payment_method = self.cursor.fetchone()
                if not payment_method:
                    raise ValueError("Método de pago no válido")
                self.cursor.execute(
                    "INSERT INTO payments (factura_id, metodo_id, monto, usuario_id) VALUES (?, ?, ?, ?)",
                    (factura_id, payment_method[0], total, usuario_id),
                )
                self.cursor.execute(
                    "SELECT id FROM cash_registers WHERE estado='ABIERTA' ORDER BY id DESC LIMIT 1"
                )
                cash_register = self.cursor.fetchone()
                if not cash_register:
                    raise ValueError(
                        "Debe abrir una caja antes de registrar una venta pagada"
                    )
                self.cursor.execute(
                    """INSERT INTO cash_movements
                       (caja_id, tipo, monto, metodo_pago, referencia, usuario_id)
                       VALUES (?, 'VENTA', ?, ?, ?, ?)""",
                    (cash_register[0], total, metodo_pago, numero, usuario_id),
                )
            audit(
                self.conn, "CREAR_FACTURA", "facturas", factura_id, numero, usuario_id
            )

            # Generar PDF
            pdf_path = self.generar_pdf(factura_id)
            self.conn.commit()

            messagebox.showinfo(
                "Éxito",
                f"Factura {numero} generada correctamente\nPDF guardado exitosamente",
            )

            # Limpiar y preparar nueva factura
            self.nueva_factura()
            self.cargar_historial()
            self.cargar_productos()

        except Exception as e:
            self.conn.rollback()
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except OSError:
                    logging.exception(
                        "No se pudo limpiar el PDF de una factura revertida"
                    )
            messagebox.showerror("Error", f"Error al generar factura: {str(e)}")

    def generar_pdf(self, factura_id):
        try:
            self.cursor.execute(
                """
                SELECT f.numero, f.fecha, f.subtotal, f.itbis, f.total,
                       c.nombre, c.cedula, c.telefono, c.direccion
                FROM facturas f
                JOIN clientes c ON f.cliente_id = c.id
                WHERE f.id = ?
            """,
                (factura_id,),
            )
            factura_data = self.cursor.fetchone()
            if not factura_data:
                raise ValueError("Factura no encontrada")

            self.cursor.execute(
                """
                SELECT p.codigo, p.nombre, fi.cantidad, fi.precio_unitario, fi.subtotal
                FROM factura_items fi
                JOIN productos p ON fi.producto_id = p.id
                WHERE fi.factura_id = ?
            """,
                (factura_id,),
            )
            items_data = self.cursor.fetchall()
            if not items_data:
                raise ValueError("La factura no tiene items")

            self.cursor.execute("""
                SELECT nombre, rnc, direccion, telefono, email, website
                FROM empresa
                WHERE id = 1
            """)
            empresa_row = self.cursor.fetchone()
            if empresa_row:
                (
                    empresa_nombre,
                    empresa_rnc,
                    empresa_direccion,
                    empresa_telefono,
                    empresa_email,
                    empresa_website,
                ) = empresa_row
            else:
                (
                    empresa_nombre,
                    empresa_rnc,
                    empresa_direccion,
                    empresa_telefono,
                    empresa_email,
                    empresa_website,
                ) = (
                    "TU EMPRESA S.A.",
                    "000-00000-0",
                    "Tu dirección aquí",
                    "(809) 000-0000",
                    "",
                    "",
                )

            empresa_nombre = empresa_nombre or "TU EMPRESA S.A."
            empresa_rnc = empresa_rnc or "000-00000-0"
            empresa_direccion = empresa_direccion or "Tu dirección aquí"
            empresa_email = empresa_email or "example@gmail.com"
            empresa_telefono = empresa_telefono or "(809) 000-0000"

            facturas_dir = os.path.join(self.base_path, "facturas")
            try:
                os.makedirs(facturas_dir, exist_ok=True)
            except OSError as e:
                raise RuntimeError(f"No se pudo crear la carpeta de facturas: {str(e)}")

            filename = os.path.join(facturas_dir, f"{factura_data[0]}.pdf")
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            styles.add(
                ParagraphStyle(
                    name="InvoiceTitle",
                    fontSize=18,
                    leading=22,
                    alignment=1,
                    spaceAfter=10,
                    fontName="Helvetica-Bold",
                )
            )
            styles.add(
                ParagraphStyle(
                    name="InvoiceHeader", fontSize=11, leading=14, spaceAfter=8
                )
            )
            styles.add(
                ParagraphStyle(
                    name="Footer",
                    fontSize=8,
                    leading=10,
                    alignment=1,
                    textColor=colors.grey,
                )
            )

            titulo = Paragraph("FACTURA", styles["InvoiceTitle"])
            elements.append(titulo)
            elements.append(Spacer(1, 0.2 * inch))

            empresa_text = f"<b>{escape(str(empresa_nombre))}</b><br/>RNC: {escape(str(empresa_rnc))}<br/>Dirección: {escape(str(empresa_direccion))}<br/>Teléfono: {escape(str(empresa_telefono))}"
            if empresa_email:
                empresa_text += f"<br/>Email: {escape(str(empresa_email))}"
            if empresa_website:
                empresa_text += f"<br/>Web: {escape(str(empresa_website))}"

            empresa_info = Paragraph(empresa_text, styles["Normal"])
            elements.append(empresa_info)
            elements.append(Spacer(1, 0.3 * inch))

            info_data = [
                ["Factura No.:", factura_data[0], "Fecha:", factura_data[1]],
                ["Cliente:", factura_data[5], "Cédula:", factura_data[6] or "N/A"],
                [
                    "Teléfono:",
                    factura_data[7] or "N/A",
                    "Dirección:",
                    factura_data[8] or "N/A",
                ],
            ]
            info_table = Table(
                info_data, colWidths=[1.2 * inch, 2.5 * inch, 1.2 * inch, 2 * inch]
            )
            info_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ]
                )
            )
            elements.append(info_table)
            elements.append(Spacer(1, 0.3 * inch))

            productos_data = [
                ["Código", "Producto", "Cantidad", "Precio Unit.", "Subtotal"]
            ]
            for item in items_data:
                productos_data.append(
                    [
                        item[0],
                        escape(str(item[1])),
                        str(item[2]),
                        f"RD$ {item[3]:.2f}",
                        f"RD$ {item[4]:.2f}",
                    ]
                )

            productos_table = Table(
                productos_data,
                colWidths=[1 * inch, 3 * inch, 1 * inch, 1.2 * inch, 1.2 * inch],
            )
            productos_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ]
                )
            )
            elements.append(productos_table)
            elements.append(Spacer(1, 0.3 * inch))

            totales_data = [
                ["", "", "", "Subtotal:", f"RD$ {factura_data[2]:.2f}"],
                ["", "", "", "ITBIS (18%):", f"RD$ {factura_data[3]:.2f}"],
                ["", "", "", "TOTAL:", f"RD$ {factura_data[4]:.2f}"],
            ]
            totales_table = Table(
                totales_data,
                colWidths=[1 * inch, 3 * inch, 1 * inch, 1.2 * inch, 1.2 * inch],
            )
            totales_table.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
                        ("FONTNAME", (3, 0), (3, -1), "Helvetica-Bold"),
                        ("FONTNAME", (3, 2), (-1, 2), "Helvetica-Bold"),
                        ("FONTSIZE", (3, 2), (-1, 2), 12),
                        ("LINEABOVE", (3, 2), (-1, 2), 2, colors.black),
                        ("TEXTCOLOR", (3, 2), (-1, 2), colors.green),
                    ]
                )
            )
            elements.append(totales_table)
            elements.append(Spacer(1, 0.2 * inch))
            footer = Paragraph(
                "Gracias por su preferencia. Documento generado automáticamente.",
                styles["Footer"],
            )
            elements.append(footer)
            doc.build(elements)
            return filename
        except Exception as e:
            raise RuntimeError(f"Error al generar el PDF: {str(e)}") from e

    def nueva_factura(self):
        # Limpiar tabla de items
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)

        # Limpiar lista de items
        self.items_factura = []

        # Resetear totales
        self.subtotal_var.set("RD$ 0.00")
        self.itbis_var.set("RD$ 0.00")
        self.total_var.set("RD$ 0.00")

        # Nuevo número de factura
        self.num_factura.set(self.generar_numero_factura())

        # Nueva fecha
        self.fecha_factura.set(datetime.now().strftime("%d/%m/%Y"))

        # Limpiar selección de cliente
        self.cliente_var.set("")
        self.metodo_pago_var.set("EFECTIVO")

        # Limpiar campos de producto
        self.producto_var.set("")
        self.precio_var.set("")
        self.cantidad_var.set("1")

    def cargar_historial(self):
        for item in self.tree_historial.get_children():
            self.tree_historial.delete(item)

        buscar = self.hist_buscar.get().strip()

        if buscar:
            self.cursor.execute(
                """
                SELECT f.id, f.numero, f.fecha, c.nombre, f.subtotal, f.itbis, f.total, f.estado
                FROM facturas f
                JOIN clientes c ON f.cliente_id = c.id
                WHERE f.numero LIKE ? OR c.nombre LIKE ?
                ORDER BY f.id DESC
            """,
                (f"%{buscar}%", f"%{buscar}%"),
            )
        else:
            self.cursor.execute("""
                SELECT f.id, f.numero, f.fecha, c.nombre, f.subtotal, f.itbis, f.total, f.estado
                FROM facturas f
                JOIN clientes c ON f.cliente_id = c.id
                ORDER BY f.id DESC
            """)

        for row in self.cursor.fetchall():
            formatted_row = (
                row[0],
                row[1],
                row[2],
                row[3],
                f"RD$ {row[4]:.2f}",
                f"RD$ {row[5]:.2f}",
                f"RD$ {row[6]:.2f}",
                row[7],
            )
            self.tree_historial.insert("", tk.END, values=formatted_row)

    def ver_detalles_factura(self):
        selected = self.tree_historial.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una factura")
            return

        item = self.tree_historial.item(selected[0])
        factura_id = item["values"][0]

        # Crear ventana de detalles
        detalle_win = tk.Toplevel(self.root)
        detalle_win.title("Detalles de Factura")
        set_app_icon(detalle_win, self.base_path)
        detalle_win.geometry("700x500")
        detalle_win.configure(bg="white")

        # Obtener datos
        self.cursor.execute(
            """
            SELECT f.numero, f.fecha, f.subtotal, f.itbis, f.total,
                   c.nombre, c.cedula, c.telefono
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            WHERE f.id = ?
        """,
            (factura_id,),
        )

        factura_data = self.cursor.fetchone()

        # Información general
        info_frame = tk.Frame(detalle_win, bg="white", relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            info_frame,
            text=f"Factura: {factura_data[0]}",
            font=("Arial", 14, "bold"),
            bg="white",
        ).pack(pady=5)
        tk.Label(info_frame, text=f"Fecha: {factura_data[1]}", bg="white").pack()
        tk.Label(info_frame, text=f"Cliente: {factura_data[5]}", bg="white").pack()
        tk.Label(info_frame, text=f"Cédula: {factura_data[6]}", bg="white").pack()

        # Tabla de items
        tk.Label(
            detalle_win, text="Productos:", font=("Arial", 12, "bold"), bg="white"
        ).pack(pady=5)

        tree_frame = tk.Frame(detalle_win, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tree = ttk.Treeview(
            tree_frame,
            columns=("Código", "Producto", "Cant", "Precio", "Subtotal"),
            show="headings",
            height=8,
        )

        tree.heading("Código", text="Código")
        tree.heading("Producto", text="Producto")
        tree.heading("Cant", text="Cant")
        tree.heading("Precio", text="Precio")
        tree.heading("Subtotal", text="Subtotal")

        tree.column("Código", width=80)
        tree.column("Producto", width=250)
        tree.column("Cant", width=70)
        tree.column("Precio", width=100)
        tree.column("Subtotal", width=100)

        tree.pack(fill=tk.BOTH, expand=True)

        # Cargar items
        self.cursor.execute(
            """
            SELECT p.codigo, p.nombre, fi.cantidad, fi.precio_unitario, fi.subtotal
            FROM factura_items fi
            JOIN productos p ON fi.producto_id = p.id
            WHERE fi.factura_id = ?
        """,
            (factura_id,),
        )

        for row in self.cursor.fetchall():
            tree.insert(
                "",
                tk.END,
                values=(
                    row[0],
                    row[1],
                    row[2],
                    f"RD$ {row[3]:.2f}",
                    f"RD$ {row[4]:.2f}",
                ),
            )

        # Totales
        total_frame = tk.Frame(detalle_win, bg="white")
        total_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            total_frame,
            text=f"Subtotal: RD$ {factura_data[2]:.2f}",
            font=("Arial", 11),
            bg="white",
        ).pack()
        tk.Label(
            total_frame,
            text=f"ITBIS: RD$ {factura_data[3]:.2f}",
            font=("Arial", 11),
            bg="white",
        ).pack()
        tk.Label(
            total_frame,
            text=f"TOTAL: RD$ {factura_data[4]:.2f}",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#27ae60",
        ).pack()

    def regenerar_pdf(self):
        selected = self.tree_historial.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una factura")
            return

        item = self.tree_historial.item(selected[0])
        factura_id = item["values"][0]

        try:
            self.generar_pdf(factura_id)
            messagebox.showinfo("Éxito", "PDF generado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")

    def _factura_seleccionada(self):
        selected = self.tree_historial.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una factura")
            return None
        return self.tree_historial.item(selected[0])["values"][0]

    def registrar_abono(self):
        if not self.require_permission("create_invoices"):
            return
        factura_id = self._factura_seleccionada()
        if factura_id is None:
            return
        try:
            self.cursor.execute(
                "SELECT total, estado FROM facturas WHERE id=?", (factura_id,)
            )
            invoice = self.cursor.fetchone()
            if not invoice or invoice[1] == "ANULADA":
                messagebox.showwarning("Abono", "La factura no admite abonos.")
                return
            self.cursor.execute(
                "SELECT COALESCE(SUM(monto), 0) FROM payments WHERE factura_id=?",
                (factura_id,),
            )
            paid = self.cursor.fetchone()[0]
            balance = round(invoice[0] - paid, 2)
            if balance <= 0:
                messagebox.showinfo("Abono", "La factura ya está pagada.")
                return
            amount = simpledialog.askfloat(
                "Registrar abono",
                f"Saldo pendiente: RD$ {balance:.2f}\nMonto del abono:",
                minvalue=0.01,
                maxvalue=balance,
                parent=self.root,
            )
            if amount is None:
                return
            method = simpledialog.askstring(
                "Método de pago",
                "Efectivo, tarjeta, transferencia u otro:",
                initialvalue="EFECTIVO",
                parent=self.root,
            )
            method = (method or "EFECTIVO").strip().upper()
            self.cursor.execute(
                "SELECT id FROM payment_methods WHERE nombre=?", (method,)
            )
            payment_method = self.cursor.fetchone()
            if not payment_method:
                messagebox.showerror("Abono", "Método de pago no válido.")
                return
            new_paid = round(paid + amount, 2)
            state = "PAGADA" if new_paid >= invoice[0] else "PARCIAL"
            self.cursor.execute(
                "INSERT INTO payments (factura_id, metodo_id, monto, usuario_id) VALUES (?, ?, ?, ?)",
                (factura_id, payment_method[0], amount, self.current_user.get("id")),
            )
            self.cursor.execute(
                "UPDATE facturas SET estado=? WHERE id=?", (state, factura_id)
            )
            audit(
                self.conn,
                "REGISTRAR_ABONO",
                "facturas",
                factura_id,
                f"{amount:.2f}",
                self.current_user.get("id"),
            )
            self.conn.commit()
            self.cargar_historial()
            messagebox.showinfo(
                "Abono",
                f"Abono registrado. Saldo restante: RD$ {max(0, invoice[0] - new_paid):.2f}",
            )
        except (sqlite3.Error, ValueError) as exc:
            self.conn.rollback()
            messagebox.showerror("Error de abono", str(exc))

    def anular_factura(self):
        if not self.require_permission("create_invoices"):
            return
        factura_id = self._factura_seleccionada()
        if factura_id is None:
            return
        if not messagebox.askyesno(
            "Anular factura",
            "La factura quedará bloqueada y el stock será reintegrado. ¿Continuar?",
        ):
            return
        try:
            self.cursor.execute(
                "SELECT numero, estado FROM facturas WHERE id=?", (factura_id,)
            )
            invoice = self.cursor.fetchone()
            if not invoice or invoice[1] == "ANULADA":
                messagebox.showwarning(
                    "Anular factura", "La factura ya está anulada o no existe."
                )
                return
            self.cursor.execute(
                "SELECT producto_id, cantidad FROM factura_items WHERE factura_id=?",
                (factura_id,),
            )
            items = self.cursor.fetchall()
            for product_id, quantity in items:
                self.cursor.execute(
                    "UPDATE productos SET stock=stock+? WHERE id=?",
                    (quantity, product_id),
                )
                self.cursor.execute(
                    """INSERT INTO inventory_movements
                       (producto_id, tipo, cantidad, motivo, referencia, usuario_id)
                       VALUES (?, 'DEVOLUCION', ?, ?, ?, ?)""",
                    (
                        product_id,
                        quantity,
                        "Anulación de factura",
                        invoice[0],
                        self.current_user.get("id"),
                    ),
                )
            self.cursor.execute(
                "UPDATE facturas SET estado='ANULADA' WHERE id=?", (factura_id,)
            )
            audit(
                self.conn,
                "ANULAR_FACTURA",
                "facturas",
                factura_id,
                invoice[0],
                self.current_user.get("id"),
            )
            self.conn.commit()
            self.cargar_historial()
            self.cargar_productos()
            messagebox.showinfo(
                "Anular factura", "Factura anulada y stock reintegrado correctamente."
            )
        except sqlite3.Error as exc:
            self.conn.rollback()
            messagebox.showerror("Error de anulación", str(exc))

    def cargar_datos(self):
        """Carga los datos en los combobox"""
        # Cargar productos en combobox
        self.cursor.execute("SELECT codigo, nombre FROM productos ORDER BY nombre")
        productos = [f"{row[0]} - {row[1]}" for row in self.cursor.fetchall()]
        self.combo_producto["values"] = productos

        # Cargar clientes en combobox
        self.cursor.execute(
            "SELECT nombre, cedula FROM clientes WHERE activo=1 ORDER BY nombre"
        )
        clientes = [
            f"{row[0]} - {row[1]}" if row[1] else row[0]
            for row in self.cursor.fetchall()
        ]
        self.combo_cliente["values"] = clientes

        # Cargar tablas
        self.cargar_productos()
        self.cargar_clientes()
        self.cargar_historial()
        self.cargar_empresa()
