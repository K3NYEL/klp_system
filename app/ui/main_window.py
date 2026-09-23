import logging
import os
import sqlite3
import sys
import tkinter as tk
import webbrowser
import customtkinter as ctk

from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog, ttk
from xml.sax.saxutils import escape

from reportlab.lib import colors  # type: ignore[reportMissingModuleSource]
from reportlab.lib.pagesizes import letter  # type: ignore[reportMissingModuleSource]
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)  # type: ignore[reportMissingModuleSource]
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)  # type: ignore[reportMissingModuleSource]

from app.auth.authorization import can
from app.core.backup import create_backup, restore_backup
from app.core.database import audit, connect_database
from app.core.paths import application_path
from app.services import (
    customers_service,
    invoice_service,
    products_service,
)
from app.ui import theme
from app.ui.components import cards, inputs, tables
from app.ui.components.buttons import AppButton
from app.ui.dashboard_cash_view import DashboardCajaView
from app.ui.inventory_view import InventoryMovementView
from app.ui.user_management_view import UserManagementView


# ``inch`` es la unidad fija de ReportLab (72 puntos).
inch = 72


class SistemaFacturacion:
    def __init__(
        self,
        root,
        on_logout=None,
        current_user=None,
    ):
        self.root = root
        self.on_logout = on_logout
        self.current_user = current_user or {}

        # ----------------------------------------------------
        # ESTADO GENERAL
        # ----------------------------------------------------

        self.tabs = {}
        self.tab_names = {
            "invoice": "Facturación",
            "products": "Inventario",
            "customers": "Clientes",
            "company": "Empresa",
            "history": "Facturas guardadas",
            "dashboard": "Caja y Dashboard",
        }

        self.base_path = self.get_base_path()

        self.items_factura = []
        self.total_factura = 0

        # ----------------------------------------------------
        # CONFIGURACIÓN DE LA VENTANA
        # ----------------------------------------------------

        self.root.title(
            f"{theme.APP_NAME} · Sistema de Facturación"
        )

        self.root.geometry("1240x740")
        self.root.minsize(1020, 640)

        if sys.platform == "win32":
            self.root.state("zoomed")
        else:
            try:
                self.root.attributes("-zoomed", True)
            except tk.TclError:
                pass

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.salir,
        )

        # ----------------------------------------------------
        # TEMA
        # ----------------------------------------------------

        theme.set_app_icon(
            self.root,
            self.base_path,
        )

        theme.remember(
            self.root,
            "plain",
            bg="window",
            fg="text",
        )

        self.theme_manager = theme.ThemeManager(
            self.root,
            theme=theme.DEFAULT_THEME,
        )

        # ----------------------------------------------------
        # BASE DE DATOS
        # ----------------------------------------------------

        self.init_db()

        # ----------------------------------------------------
        # INTERFAZ
        # ----------------------------------------------------

        self.crear_interfaz()
        self.cargar_datos()

    # ========================================================
    # BASE DE DATOS
    # ========================================================

    def init_db(self):
        """Abre la base y aplica las migraciones centralizadas."""

        try:
            db_path = os.path.join(
                self.base_path,
                "facturacion.db",
            )

            self.conn = connect_database(db_path)
            self.cursor = self.conn.cursor()

        except sqlite3.Error as exc:
            messagebox.showerror(
                "Error de Base de Datos",
                f"Error al inicializar la base de datos: {exc}",
            )

            if hasattr(self, "conn"):
                self.conn.close()

            raise

    def get_base_path(self):
        return application_path()

    # ========================================================
    # UTILIDADES DE VENTANA
    # ========================================================

    def center_window(
        self,
        width,
        height,
        window=None,
    ):
        if window is None:
            window = self.root

        window.update_idletasks()

        x = (
            window.winfo_screenwidth() - width
        ) // 2

        y = (
            window.winfo_screenheight() - height
        ) // 2

        window.geometry(
            f"{width}x{height}+{x}+{y}"
        )

    # ========================================================
    # PESTAÑA EMPRESA
    # ========================================================

    def crear_pestaña_admin(self):
        """Crea la pestaña de configuración de la empresa."""

        self.notebook.add(
            "Empresa"
        )

        tab = self.notebook.tab(
            "Empresa"
        )

        self.tabs["company"] = tab

        wrapper = ctk.CTkFrame(
            tab,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=12,
        )

        card = cards.Card(
            wrapper,
            title="Datos de la empresa",
            subtitle=(
                "Esta información aparece en el "
                "encabezado de las facturas PDF"
            ),
            padding=18,
        )

        card.pack(
            fill="x",
        )

        form = card.body

        form.columnconfigure(
            1,
            weight=1,
        )

        form.columnconfigure(
            3,
            weight=1,
        )

        # ----------------------------------------------------
        # VARIABLES
        # ----------------------------------------------------

        self.empresa_nombre_var = ctk.StringVar()
        self.empresa_rnc_var = ctk.StringVar()
        self.empresa_direccion_var = ctk.StringVar()
        self.empresa_telefono_var = ctk.StringVar()
        self.empresa_email_var = ctk.StringVar()
        self.empresa_website_var = ctk.StringVar()

        fields = (
            (
                "Nombre de la empresa",
                self.empresa_nombre_var,
                0,
                0,
            ),
            (
                "RNC",
                self.empresa_rnc_var,
                0,
                2,
            ),
            (
                "Dirección",
                self.empresa_direccion_var,
                1,
                0,
            ),
            (
                "Teléfono",
                self.empresa_telefono_var,
                1,
                2,
            ),
            (
                "Email",
                self.empresa_email_var,
                2,
                0,
            ),
            (
                "Sitio web",
                self.empresa_website_var,
                2,
                2,
            ),
        )

        for text, variable, row, column in fields:
            inputs.labeled_entry(
                form,
                text,
                textvariable=variable,
                row=row,
                column=column,
                label_column=column,
                entry_column=column + 1,
                background="surface",
            )

        # ----------------------------------------------------
        # ACCIONES
        # ----------------------------------------------------

        actions = ctk.CTkFrame(
            form,
            fg_color="transparent",
        )

        actions.grid(
            row=3,
            column=0,
            columnspan=4,
            sticky="ew",
            pady=(18, 0),
        )

        AppButton(
            actions,
            text="Guardar cambios",
            command=self.guardar_empresa,
            variant="primary",
            tooltip=(
                "Guarda los datos que se imprimen "
                "en las facturas"
            ),
        ).pack(
            side="left",
        )

        AppButton(
            actions,
            text="Abrir en ventana",
            command=self.ir_mi_empresa,
            variant="ghost",
            tooltip=(
                "Edita los datos de la empresa "
                "en una ventana aparte"
            ),
        ).pack(
            side="left",
            padx=6,
        )

    def cargar_empresa(self):
        self.cursor.execute(
            """
            SELECT
                nombre,
                rnc,
                direccion,
                telefono,
                email,
                website
            FROM empresa
            WHERE id = 1
            """
        )

        row = self.cursor.fetchone()

        if row:
            self.empresa_nombre_var.set(
                row[0] or ""
            )
            self.empresa_rnc_var.set(
                row[1] or ""
            )
            self.empresa_direccion_var.set(
                row[2] or ""
            )
            self.empresa_telefono_var.set(
                row[3] or ""
            )
            self.empresa_email_var.set(
                row[4] or ""
            )
            self.empresa_website_var.set(
                row[5] or ""
            )
        else:
            self.empresa_nombre_var.set("")
            self.empresa_rnc_var.set("")
            self.empresa_direccion_var.set("")
            self.empresa_telefono_var.set("")
            self.empresa_email_var.set("")
            self.empresa_website_var.set("")

    def guardar_empresa(self):
        if not self.require_permission(
            "manage_company"
        ):
            return

        nombre = self.empresa_nombre_var.get().strip()
        rnc = self.empresa_rnc_var.get().strip()
        direccion = self.empresa_direccion_var.get().strip()
        telefono = self.empresa_telefono_var.get().strip()
        email = self.empresa_email_var.get().strip()
        website = self.empresa_website_var.get().strip()

        self.cursor.execute(
            "SELECT id FROM empresa WHERE id = 1"
        )

        if self.cursor.fetchone():
            self.cursor.execute(
                """
                UPDATE empresa
                SET
                    nombre=?,
                    rnc=?,
                    direccion=?,
                    telefono=?,
                    email=?,
                    website=?
                WHERE id = 1
                """,
                (
                    nombre,
                    rnc,
                    direccion,
                    telefono,
                    email,
                    website,
                ),
            )
        else:
            self.cursor.execute(
                """
                INSERT INTO empresa (
                    id,
                    nombre,
                    rnc,
                    direccion,
                    telefono,
                    email,
                    website
                )
                VALUES (
                    1, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    nombre,
                    rnc,
                    direccion,
                    telefono,
                    email,
                    website,
                ),
            )

        self.conn.commit()

        self.set_status(
            "Datos de la empresa guardados."
        )

        messagebox.showinfo(
            "Éxito",
            "Información de la empresa "
            "guardada correctamente",
        )

    # ========================================================
    # INTERFAZ PRINCIPAL
    # ========================================================

    def crear_interfaz(self):
        """Crea menú, encabezado, pestañas y barra de estado."""

        self._crear_menu()

        shell = ctk.CTkFrame(
            self.root,
            fg_color=theme.color("window"),
            corner_radius=0,
        )

        shell.pack(
            fill="both",
            expand=True,
        )

        self._crear_encabezado(shell)

        # La barra de estado se crea antes del Tabview.
        self._crear_barra_estado(shell)

        self.notebook = ctk.CTkTabview(
            shell,
            corner_radius=8,
        )

        self.notebook.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(10, 4),
        )

        self.crear_pestaña_facturacion()
        self.crear_pestaña_productos()
        self.crear_pestaña_clientes()
        self.crear_pestaña_admin()
        self.crear_pestaña_historial()
        self._crear_pestaña_caja_dashboard()

    # ========================================================
    # MENÚ
    # ========================================================

    def _crear_menu(self):
        """Construye la barra de menús."""

        menu_bar = tk.Menu(
            self.root,
        )

        # ----------------------------------------------------
        # ARCHIVO
        # ----------------------------------------------------

        archivo = tk.Menu(
            menu_bar,
            tearoff=0,
        )

        archivo.add_command(
            label="Cerrar sesión",
            command=self.cerrar_sesion,
        )

        archivo.add_command(
            label="Crear copia de seguridad",
            command=self.crear_backup,
        )

        archivo.add_command(
            label="Restaurar copia de seguridad",
            command=self.restaurar_backup,
        )

        archivo.add_separator()

        archivo.add_command(
            label="Salir",
            command=self.salir,
        )

        menu_bar.add_cascade(
            label="Archivo",
            menu=archivo,
        )

        # ----------------------------------------------------
        # CAJA
        # ----------------------------------------------------

        caja = tk.Menu(
            menu_bar,
            tearoff=0,
        )

        caja.add_command(
            label="Ir a Caja y Dashboard",
            command=lambda: self.seleccionar_seccion(
                "dashboard"
            ),
        )

        caja.add_separator()

        caja.add_command(
            label="Abrir caja",
            command=self.abrir_caja,
        )

        caja.add_command(
            label="Cerrar caja",
            command=self.cerrar_caja,
        )

        caja.add_command(
            label="Registrar movimiento manual",
            command=self.abrir_movimiento_caja,
        )

        menu_bar.add_cascade(
            label="Caja",
            menu=caja,
        )

        # ----------------------------------------------------
        # OPCIONES
        # ----------------------------------------------------

        opciones = tk.Menu(
            menu_bar,
            tearoff=0,
        )

        opciones.add_command(
            label="Nueva factura",
            command=lambda: self.seleccionar_seccion(
                "invoice"
            ),
            accelerator="Ctrl+N",
        )

        opciones.add_command(
            label="Facturación rápida",
            command=self.abrir_facturacion_rapida,
            accelerator="F2",
        )

        opciones.add_command(
            label="Caja y Dashboard",
            command=lambda: self.seleccionar_seccion(
                "dashboard"
            ),
            accelerator="Ctrl+D",
        )

        opciones.add_command(
            label="Inventario",
            command=lambda: self.seleccionar_seccion(
                "products"
            ),
            accelerator="Ctrl+I",
        )

        opciones.add_command(
            label="Clientes",
            command=lambda: self.seleccionar_seccion(
                "customers"
            ),
            accelerator="Ctrl+L",
        )

        opciones.add_command(
            label="Facturas guardadas",
            command=lambda: self.seleccionar_seccion(
                "history"
            ),
            accelerator="Ctrl+H",
        )

        opciones.add_command(
            label="Mi empresa",
            command=self.ir_mi_empresa,
        )

        opciones.add_separator()

        opciones.add_command(
            label="Movimientos de inventario",
            command=self.abrir_movimientos_inventario,
        )

        opciones.add_command(
            label="Usuarios y permisos",
            command=self.abrir_usuarios,
        )

        opciones.add_separator()

        opciones.add_command(
            label="Acerca de",
            command=self.mostrar_acerca_de,
        )

        menu_bar.add_cascade(
            label="Opciones",
            menu=opciones,
        )

        # ----------------------------------------------------
        # AYUDA
        # ----------------------------------------------------

        ayuda = tk.Menu(
            menu_bar,
            tearoff=0,
        )

        ayuda.add_command(
            label="Atajos de teclado",
            command=self.mostrar_atajos,
        )

        ayuda.add_command(
            label="Acerca de",
            command=self.mostrar_acerca_de,
        )

        menu_bar.add_cascade(
            label="Ayuda",
            menu=ayuda,
        )

        self.root.config(
            menu=menu_bar,
        )

    # ========================================================
    # ENCABEZADO
    # ========================================================

    def _crear_encabezado(self, parent):
        """Crea la barra superior."""

        header = ctk.CTkFrame(
            parent,
            fg_color=theme.color("header"),
            corner_radius=0,
        )

        header.pack(
            fill="x",
        )

        left = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )

        left.pack(
            side="left",
            padx=18,
            pady=12,
        )

        ctk.CTkLabel(
            left,
            text=theme.APP_NAME,
            font=theme.font("title"),
            text_color=theme.color("header_text"),
            anchor="w",
        ).pack(
            anchor="w",
        )

        ctk.CTkLabel(
            left,
            text="Facturación · Caja · Inventario · Clientes",
            font=theme.font("small"),
            text_color=theme.color("header_text"),
            anchor="w",
        ).pack(
            anchor="w",
            pady=(2, 0),
        )

        right = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )

        right.pack(
            side="right",
            padx=18,
        )

        user_text = (
            f"{self.current_user.get('usuario', 'Usuario')} · "
            f"{self.current_user.get('role', 'Sin rol')}"
        )

        self.user_label = ctk.CTkLabel(
            right,
            text=user_text,
            font=theme.font("body_bold"),
            text_color=theme.color("header_text"),
            anchor="e",
        )

        self.user_label.pack(
            anchor="e",
            pady=(0, 6),
        )

        actions = ctk.CTkFrame(
            right,
            fg_color="transparent",
        )

        actions.pack(
            anchor="e",
        )

        AppButton(
            actions,
            text="Facturación rápida",
            command=self.abrir_facturacion_rapida,
            variant="primary",
            size="small",
            tooltip=(
                "Venta de mostrador con lector "
                "de códigos (F2)"
            ),
        ).pack(
            side="left",
            padx=3,
        )

        AppButton(
            actions,
            text="Caja y Dashboard",
            command=lambda: self.seleccionar_seccion(
                "dashboard"
            ),
            variant="ghost",
            size="small",
            tooltip=(
                "Indicadores del negocio y "
                "movimientos de caja"
            ),
        ).pack(
            side="left",
            padx=3,
        )

        AppButton(
            actions,
            text="Cerrar sesión",
            command=self.cerrar_sesion,
            variant="danger",
            size="small",
            tooltip=(
                "Volver a la pantalla de inicio "
                "de sesión"
            ),
        ).pack(
            side="left",
            padx=3,
        )

    # ========================================================
    # BARRA DE ESTADO
    # ========================================================

    def _crear_barra_estado(self, parent):
        """Crea la barra inferior de estado."""

        bar = ctk.CTkFrame(
            parent,
            fg_color=theme.color("surface_alt"),
            corner_radius=0,
            height=32,
        )

        bar.pack(
            fill="x",
            side="bottom",
        )

        bar.pack_propagate(False)

        self.status_var = ctk.StringVar(
            value="Listo."
        )

        ctk.CTkLabel(
            bar,
            textvariable=self.status_var,
            font=theme.font("small"),
            text_color=theme.color("text"),
            anchor="w",
        ).pack(
            side="left",
            padx=14,
        )

        self.status_right_var = ctk.StringVar(
            value=(
                f"{theme.APP_NAME} "
                f"v{theme.APP_VERSION} · base local"
            )
        )

        ctk.CTkLabel(
            bar,
            textvariable=self.status_right_var,
            font=theme.font("small"),
            text_color=theme.color("text_muted"),
            anchor="e",
        ).pack(
            side="right",
            padx=14,
        )


    def set_status(self, message):
        """Muestra un mensaje en la barra de estado."""

        if getattr(
            self,
            "status_var",
            None,
        ) is not None:
            self.status_var.set(message)
            
    # ========================================================
    # DASHBOARD + CAJA
    # ========================================================

    def _crear_pestaña_caja_dashboard(self):
        """Crea la pestaña unificada de dashboard y caja."""

        tab_name = "Caja y Dashboard"

        self.notebook.add(
            tab_name
        )

        tab = self.notebook.tab(
            tab_name
        )

        tab.configure(
            fg_color=theme.color("window")
        )

        self.dashboard_caja = DashboardCajaView(
            tab,
            self.conn,
            actor_id=self.current_user.get("id"),
            on_open_cash=self.abrir_caja,
            on_close_cash=self.cerrar_caja,
            can_manage_cash=can(
                self.conn,
                self.current_user.get("role"),
                "manage_cash",
            ),
            on_change=lambda: self.set_status(
                "Movimiento de caja registrado."
            ),
        )

        self.tabs["dashboard"] = tab


    # ========================================================
    # ATAJOS
    # ========================================================

    def mostrar_atajos(self):
        """Muestra los atajos disponibles."""

        messagebox.showinfo(
            "Atajos de teclado",
            "Ctrl+N  Nueva factura\n"
            "F2         Facturación rápida\n"
            "Ctrl+D  Caja y Dashboard\n"
            "Ctrl+I   Inventario\n"
            "Ctrl+L   Clientes\n"
            "Ctrl+H  Facturas guardadas\n\n"
            "Enter    Agrega el producto escrito "
            "en el formulario de factura",
        )

    def _limpiar_busqueda_producto(self):
        self.prod_buscar.delete(
            0,
            tk.END,
        )
        self.cargar_productos()

    def _limpiar_busqueda_cliente(self):
        self.cli_buscar.delete(
            0,
            tk.END,
        )
        self.cargar_clientes()

    def seleccionar_pestaña(self, index):
        """Activa una pestaña por índice."""

        try:
            tabs = self.notebook._segmented_button.cget(
                "values"
            )

            if 0 <= index < len(tabs):
                self.notebook.set(
                    tabs[index]
                )

        except (IndexError, TypeError, tk.TclError):
            pass

    def seleccionar_seccion(self, name):
        """Activa una pestaña y refresca sus datos."""

        tab_name = self.tab_names.get(name)

        if tab_name is None:
            return

        self.notebook.set(tab_name)

        if (
            name == "dashboard"
            and hasattr(self, "dashboard_caja")
        ):
            self.dashboard_caja.refresh()

        elif name == "products":
            self.cargar_productos()

        elif name == "customers":
            self.cargar_clientes()

    def _registrar_atajos(self):
            """Registra los atajos globales."""

            shortcuts = {
                "n": "invoice",
                "d": "dashboard",
                "i": "products",
                "l": "customers",
                "h": "history",
            }

            for key, section in shortcuts.items():
                self.root.bind_all(
                    f"<Control-KeyPress-{key}>",
                    lambda event, target=section:
                        self._atajo_pestaña(
                            event,
                            target,
                        ),
                    add="+",
                )

            self.root.bind_all(
                "<F2>",
                self._atajo_facturacion_rapida,
                add="+",
            )

    def _atajo_pestaña(self, event, section):
        """Cambia de sección."""

        self.seleccionar_seccion(
            section
        )

        self.root.focus_set()

        return "break"

    def _atajo_facturacion_rapida(self, event):
        self.abrir_facturacion_rapida()

        return "break"

    # ========================================================
    # FACTURACIÓN RÁPIDA
    # ========================================================

    def abrir_facturacion_rapida(self):
        """Abre una venta de mostrador."""

        if not self.require_permission(
            "create_invoices"
        ):
            return

        if (
            getattr(
                self,
                "quick_window",
                None,
            )
            and self.quick_window.winfo_exists()
        ):
            self.quick_window.deiconify()
            self.quick_code_entry.focus_set()
            return

        window = ctk.CTkToplevel(
            self.root
        )

        self.quick_window = window

        theme.prepare_toplevel(
            window,
            "Facturación rápida",
            (780, 580),
            self.base_path,
        )

        # ----------------------------------------------------
        # ENCABEZADO
        # ----------------------------------------------------

        header = ctk.CTkFrame(
            window,
            fg_color=theme.color("accent"),
            corner_radius=0,
        )

        header.pack(
            fill="x",
        )

        ctk.CTkLabel(
            header,
            text="FACTURACIÓN RÁPIDA",
            font=theme.font("title"),
            text_color=theme.color("text_on_accent"),
            anchor="w",
        ).pack(
            anchor="w",
            padx=18,
            pady=(14, 2),
        )

        ctk.CTkLabel(
            header,
            text=(
                "Escanee el código, confirme "
                "el pago y entregue el ticket"
            ),
            font=theme.font("small"),
            text_color=theme.color("text_on_accent"),
            anchor="w",
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 14),
        )

        # ----------------------------------------------------
        # CONTENEDOR
        # ----------------------------------------------------

        shell = ctk.CTkFrame(
            window,
            fg_color=theme.color("window"),
            corner_radius=0,
        )

        shell.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=12,
        )

        # ----------------------------------------------------
        # ESCANEAR PRODUCTO
        # ----------------------------------------------------

        scan_card = cards.Card(
            shell,
            title="Escanear producto",
            padding=12,
        )

        scan_card.pack(
            fill="x",
        )

        scan = scan_card.body

        cards.label(
            scan,
            "Código de barras / SKU",
            font_role="body_bold",
            background="surface",
        ).pack(
            side="left",
            padx=(0, 8),
        )

        self.quick_code_var = ctk.StringVar()

        self.quick_code_entry = inputs.make_entry(
            scan,
            textvariable=self.quick_code_var,
            width=26,
            font_role="body",
        )

        self.quick_code_entry.pack(
            side="left",
        )

        self.quick_code_entry.bind(
            "<Return>",
            lambda event:
                self.agregar_item_rapido(),
        )

        cards.label(
            scan,
            "Cantidad",
            font_role="body_bold",
            background="surface",
        ).pack(
            side="left",
            padx=(14, 8),
        )

        self.quick_quantity_var = (
            ctk.StringVar(value="1")
        )

        inputs.make_entry(
            scan,
            textvariable=self.quick_quantity_var,
            width=6,
        ).pack(
            side="left",
        )

        AppButton(
            scan,
            text="Agregar",
            command=self.agregar_item_rapido,
            variant="success",
            tooltip=(
                "Agrega el producto escaneado "
                "a la venta"
            ),
        ).pack(
            side="left",
            padx=12,
        )

        # ----------------------------------------------------
        # PRODUCTOS
        # ----------------------------------------------------

        items_card = cards.Card(
            shell,
            title="Productos de la venta",
            padding=12,
        )

        items_card.pack(
            fill="both",
            expand=True,
            pady=12,
        )

        self.quick_table = tables.DataTable(
            items_card.body,
            columns=(
                "Código",
                "Producto",
                "Cantidad",
                "Precio",
                "Total",
            ),
            widths=(
                120,
                300,
                90,
                110,
                120,
            ),
            anchors=(
                "w",
                "w",
                "e",
                "e",
                "e",
            ),
            height=9,
        )

        self.quick_table.pack(
            fill="both",
            expand=True,
        )

        self.quick_tree = self.quick_table.tree

        self.quick_tree.bind(
            "<Delete>",
            lambda event:
                self.eliminar_item_rapido(),
        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        footer_card = cards.Card(
            shell,
            padding=12,
        )

        footer_card.pack(
            fill="x",
        )

        footer = footer_card.body

        self.quick_total_var = ctk.StringVar(
            value="Total: RD$ 0.00"
        )

        ctk.CTkLabel(
            footer,
            textvariable=self.quick_total_var,
            font=theme.font("title"),
            text_color=theme.color("success"),
            anchor="w",
        ).pack(
            side="left",
        )

        self.quick_payment_var = (
            ctk.StringVar(value="EFECTIVO")
        )

        inputs.make_combobox(
            footer,
            values=(
                "EFECTIVO",
                "TARJETA",
                "TRANSFERENCIA",
                "OTRO",
            ),
            textvariable=self.quick_payment_var,
            width=16,
        ).pack(
            side="left",
            padx=18,
        )

        AppButton(
            footer,
            text="Cobrar e imprimir ticket",
            command=self.confirmar_factura_rapida,
            variant="primary",
            tooltip=(
                "Guarda la venta y genera "
                "el ticket en PDF"
            ),
        ).pack(
            side="right",
            padx=5,
        )

        AppButton(
            footer,
            text="Quitar seleccionado",
            command=self.eliminar_item_rapido,
            variant="danger",
            tooltip=(
                "Quita el producto seleccionado "
                "(Supr)"
            ),
        ).pack(
            side="right",
            padx=5,
        )

        # ----------------------------------------------------
        # ESTADO
        # ----------------------------------------------------

        self.quick_items = []

        window.protocol(
            "WM_DELETE_WINDOW",
            window.destroy,
        )

        window.after(
            100,
            lambda: (
                self.quick_code_entry.focus_set()
                if self.quick_code_entry.winfo_exists()
                else None
            ),
        )

    # ========================================================
    # AGREGAR PRODUCTO A FACTURACIÓN RÁPIDA
    # ========================================================

    def agregar_item_rapido(self):
        code = self.quick_code_var.get().strip()

        if not code:
            return

        try:
            quantity = int(
                self.quick_quantity_var.get()
            )

            if quantity <= 0:
                raise ValueError(
                    "La cantidad debe ser mayor "
                    "que cero"
                )

            self.cursor.execute(
                """
                SELECT
                    codigo,
                    nombre,
                    precio,
                    stock
                FROM productos
                WHERE activo=1
                  AND (
                      codigo=?
                      OR codigo_barras=?
                  )
                LIMIT 1
                """,
                (code, code),
            )

            product = self.cursor.fetchone()

            if not product:
                messagebox.showwarning(
                    "Producto no encontrado",
                    (
                        "No existe un producto "
                        f"con código: {code}"
                    ),
                    parent=self.quick_window,
                )
                return

            existing = next(
                (
                    item
                    for item in self.quick_items
                    if item["codigo"] == product[0]
                ),
                None,
            )

            current_quantity = (
                existing["cantidad"]
                if existing
                else 0
            )

            if (
                current_quantity + quantity
                > product[3]
            ):
                raise ValueError(
                    "Stock insuficiente. "
                    f"Disponible: {product[3]}"
                )

            if existing:
                existing["cantidad"] += quantity

                existing["subtotal"] = (
                    existing["cantidad"]
                    * existing["precio"]
                )

            else:
                self.quick_items.append(
                    {
                        "codigo": product[0],
                        "nombre": product[1],
                        "precio": product[2],
                        "cantidad": quantity,
                        "subtotal": (
                            product[2]
                            * quantity
                        ),
                    }
                )

            self._refrescar_factura_rapida()

            self.quick_code_var.set("")
            self.quick_quantity_var.set("1")

            self.quick_code_entry.focus_set()

        except ValueError as exc:
            messagebox.showwarning(
                "Validación",
                str(exc),
                parent=self.quick_window,
            )

        def _refrescar_factura_rapida(self):
            self.quick_table.clear()

            total = 0

            for item in self.quick_items:
                total += item["subtotal"]

                self.quick_table.add_row(
                    (
                        item["codigo"],
                        item["nombre"],
                        item["cantidad"],
                        f"RD$ {item['precio']:.2f}",
                        f"RD$ {item['subtotal']:.2f}",
                    )
                )
        self.quick_table.restripe()
        self.quick_total_var.set(f"Total: RD$ {total:.2f}")


    def eliminar_item_rapido(self):
        index = self.quick_table.remove_selected()

        if index is not None:
            del self.quick_items[index]
            self._refrescar_factura_rapida()


    def confirmar_factura_rapida(self):
        if not self.quick_items:
            messagebox.showwarning(
                "Venta vacía",
                "Escanea al menos un producto.",
                parent=self.quick_window,
            )
            return

        payment = self.quick_payment_var.get()
        invoice_number = self.generar_numero_factura()
        pdf_path = None

        try:
            self.cursor.execute(
                "SELECT id FROM clientes WHERE nombre=? LIMIT 1",
                ("CONSUMIDOR FINAL",),
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
                """
                INSERT INTO facturas (
                    numero,
                    fecha,
                    cliente_id,
                    subtotal,
                    itbis,
                    total,
                    estado,
                    metodo_pago,
                    usuario_id
                )
                VALUES (
                    ?,
                    DATE('now'),
                    ?,
                    ?,
                    ?,
                    ?,
                    'PAGADA',
                    ?,
                    ?
                )
                """,
                (
                    invoice_number,
                    customer_id,
                    subtotal,
                    tax,
                    total,
                    payment,
                    user_id,
                ),
            )

            invoice_id = self.cursor.lastrowid

            self.cursor.execute(
                "SELECT id FROM payment_methods WHERE nombre=?",
                (payment,),
            )
            payment_method = self.cursor.fetchone()

            if not payment_method:
                raise ValueError("Método de pago no válido")

            for item in self.quick_items:
                self.cursor.execute(
                    "SELECT id, stock FROM productos WHERE codigo=?",
                    (item["codigo"],),
                )

                product = self.cursor.fetchone()

                if not product:
                    raise ValueError(
                        f"Producto no encontrado: {item['codigo']}"
                    )

                product_id, stock = product

                self.cursor.execute(
                    """
                    UPDATE productos
                    SET stock = stock - ?
                    WHERE id = ?
                    AND stock >= ?
                    """,
                    (
                        item["cantidad"],
                        product_id,
                        item["cantidad"],
                    ),
                )

                if self.cursor.rowcount != 1:
                    raise ValueError(
                        f"Stock insuficiente para {item['nombre']}"
                    )

                self.cursor.execute(
                    """
                    INSERT INTO factura_items (
                        factura_id,
                        producto_id,
                        cantidad,
                        precio_unitario,
                        subtotal
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        invoice_id,
                        product_id,
                        item["cantidad"],
                        item["precio"],
                        item["subtotal"],
                    ),
                )

                # La cantidad se guarda siempre en positivo.
                # La columna ``tipo`` indica si entra o sale del inventario.
                self.cursor.execute(
                    """
                    INSERT INTO inventory_movements (
                        producto_id,
                        tipo,
                        cantidad,
                        motivo,
                        referencia,
                        usuario_id
                    )
                    VALUES (
                        ?,
                        'SALIDA',
                        ?,
                        'Venta rápida',
                        ?,
                        ?
                    )
                    """,
                    (
                        product_id,
                        item["cantidad"],
                        invoice_number,
                        user_id,
                    ),
                )

            self.cursor.execute(
                """
                INSERT INTO payments (
                    factura_id,
                    metodo_id,
                    monto,
                    usuario_id
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    invoice_id,
                    payment_method[0],
                    total,
                    user_id,
                ),
            )

            self.cursor.execute(
                """
                SELECT id
                FROM cash_registers
                WHERE estado='ABIERTA'
                ORDER BY id DESC
                LIMIT 1
                """
            )

            cash = self.cursor.fetchone()

            if not cash:
                raise ValueError("Debe abrir una caja antes de vender")

            self.cursor.execute(
                """
                INSERT INTO cash_movements (
                    caja_id,
                    tipo,
                    monto,
                    metodo_pago,
                    referencia,
                    usuario_id
                )
                VALUES (?, 'VENTA', ?, ?, ?, ?)
                """,
                (
                    cash[0],
                    total,
                    payment,
                    invoice_number,
                    user_id,
                ),
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
                "Error en venta rápida",
                str(exc),
                parent=self.quick_window,
            )


    def require_permission(self, permission):
        if can(
            self.conn,
            self.current_user.get("role"),
            permission,
        ):
            return True

        messagebox.showwarning(
            "Permiso insuficiente",
            "Su usuario no tiene permisos para realizar esta operación.",
        )

        return False

    def ir_mi_empresa(self):
        """Abre una ventana aparte para editar los datos de la empresa."""

        empresa_win = ctk.CTkToplevel(self.root)

        theme.prepare_toplevel(
            empresa_win,
            "Mi empresa",
            (640, 470),
            self.base_path,
            modal=True,
        )

        card = cards.Card(
            empresa_win,
            title="Datos de mi empresa",
            subtitle="Se imprimen en el encabezado de cada factura",
            padding=18,
        )

        card.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18,
        )

        form = card.body
        form.columnconfigure(1, weight=1)

        fields = (
            ("Nombre de la empresa", self.empresa_nombre_var),
            ("RNC", self.empresa_rnc_var),
            ("Dirección", self.empresa_direccion_var),
            ("Teléfono", self.empresa_telefono_var),
            ("Email", self.empresa_email_var),
            ("Sitio web", self.empresa_website_var),
        )

        entries = []

        for index, (text, variable) in enumerate(fields):
            _caption, entry = inputs.labeled_entry(
                form,
                text,
                textvariable=variable,
                row=index,
                column=0,
                label_column=0,
                entry_column=1,
                label_sticky="w",
                background="surface",
            )

            entries.append(entry)

        actions = ctk.CTkFrame(
            form,
            fg_color="transparent",
        )

        actions.grid(
            row=len(fields),
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(16, 0),
        )

        AppButton(
            actions,
            text="Guardar datos",
            command=self.guardar_empresa,
            variant="primary",
            tooltip="Guarda los datos de la empresa",
        ).pack(side="left")

        AppButton(
            actions,
            text="Cerrar",
            command=empresa_win.destroy,
            variant="neutral",
            tooltip="Cerrar sin guardar (Esc)",
        ).pack(side="left", padx=6)

        empresa_win.bind(
            "<Escape>",
            lambda event: empresa_win.destroy(),
        )

        if entries:
            entries[0].focus_set()


    def _cerrar_conexion(self):
        """Cierra la base de datos ignorando errores de cierre repetido."""

        conexion = getattr(self, "conn", None)

        if conexion is None:
            return

        try:
            conexion.close()
        except sqlite3.Error:
            logging.exception("No se pudo cerrar la base de datos")


    def cerrar_sesion(self):
        if messagebox.askyesno(
            "Cerrar sesión",
            "¿Desea cerrar sesión y volver al login?",
        ):
            self._cerrar_conexion()
            self.root.destroy()

            if self.on_logout:
                self.on_logout()


    def salir(self):
        if messagebox.askyesno(
            "Salir",
            "¿Desea salir del sistema?",
        ):
            self._cerrar_conexion()
            self.root.destroy()


    def crear_backup(self):
        if not self.require_permission("manage_company"):
            return

        try:
            backup_dir = os.path.join(
                self.base_path,
                "backups",
            )

            backup_path = create_backup(
                os.path.join(
                    self.base_path,
                    "facturacion.db",
                ),
                backup_dir,
            )

            self.cursor.execute(
                "INSERT INTO backups (ruta) VALUES (?)",
                (str(backup_path),),
            )

            audit(
                self.conn,
                "CREAR_BACKUP",
                "backups",
                self.cursor.lastrowid,
                str(backup_path),
                self.current_user.get("id"),
            )

            self.conn.commit()

            messagebox.showinfo(
                "Copia de seguridad",
                f"Backup creado correctamente:\n{backup_path}",
            )

        except Exception as exc:
            messagebox.showerror(
                "Error de backup",
                f"No se pudo crear la copia de seguridad:\n{exc}",
            )


    def abrir_usuarios(self):
        if self.require_permission("manage_users"):
            UserManagementView(
                self.root,
                self.conn,
                self.current_user.get("id"),
            )


    def abrir_movimientos_inventario(self):
        if self.require_permission("manage_products"):
            InventoryMovementView(
                self.root,
                self.conn,
                self.current_user.get("id"),
            )


    def abrir_movimiento_caja(self):
        """Lleva al usuario al panel de caja para registrar un movimiento manual."""

        if not self.require_permission("manage_cash"):
            return

        self.seleccionar_seccion("dashboard")
        self.notebook.set("Caja y Dashboard")

        self.dashboard_caja.focus_movement_form()

        self.set_status(
            "Registre el movimiento de caja en el formulario del panel."
        )


    def restaurar_backup(self):
        if not self.require_permission("manage_company"):
            return

        backup_path = filedialog.askopenfilename(
            title="Seleccionar copia de seguridad",
            initialdir=os.path.join(
                self.base_path,
                "backups",
            ),
            filetypes=(
                ("Bases SQLite", "*.db"),
                ("Todos los archivos", "*.*"),
            ),
        )

        if not backup_path:
            return

        if not messagebox.askyesno(
            "Restaurar copia",
            "Se guardará una copia de la base actual antes de restaurar. "
            "¿Continuar?",
        ):
            return

        database_path = os.path.join(
            self.base_path,
            "facturacion.db",
        )

        try:
            self.conn.close()

            restore_backup(
                backup_path,
                database_path,
                os.path.join(
                    self.base_path,
                    "backups",
                ),
            )

            self.conn = connect_database(database_path)
            self.cursor = self.conn.cursor()

            # Las vistas hijas guardan la conexión que recibieron
            # al crearse. Debemos reemplazarla después de restaurar.
            self._propagar_conexion()

            self.cargar_datos()
            self.dashboard_caja.refresh()

            self.set_status(
                "Copia de seguridad restaurada."
            )

            messagebox.showinfo(
                "Restauración",
                "La copia de seguridad fue restaurada correctamente.",
            )

        except Exception as exc:
            try:
                self.conn = connect_database(database_path)
                self.cursor = self.conn.cursor()
                self._propagar_conexion()

            except sqlite3.Error:
                logging.exception(
                    "No se pudo reabrir la base tras un fallo al restaurar"
                )

            messagebox.showerror(
                "Error de restauración",
                str(exc),
            )


    def _propagar_conexion(self):
        """Reparte la conexión activa entre las vistas que la conservan."""

        for vista in (
            getattr(self, "dashboard_caja", None),
        ):
            if vista is not None and hasattr(vista, "conn"):
                vista.conn = self.conn


    def abrir_caja(self):
        if not self.require_permission("manage_cash"):
            return

        self.cursor.execute(
            "SELECT id FROM cash_registers WHERE estado='ABIERTA'"
        )

        if self.cursor.fetchone():
            messagebox.showwarning(
                "Caja",
                "Ya existe una caja abierta.",
            )
            return

        amount = simpledialog.askfloat(
            "Abrir caja",
            "Monto inicial:",
            minvalue=0,
            parent=self.root,
        )

        if amount is None:
            return

        self.cursor.execute(
            """
            INSERT INTO cash_registers (
                usuario_apertura,
                monto_inicial
            )
            VALUES (?, ?)
            """,
            (
                self.current_user.get("id"),
                amount,
            ),
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

        self.dashboard_caja.refresh()
        self.set_status("Caja abierta correctamente.")

        messagebox.showinfo(
            "Caja",
            "Caja abierta correctamente.",
        )


    def cerrar_caja(self):
        if not self.require_permission("manage_cash"):
            return

        self.cursor.execute(
            """
            SELECT id, monto_inicial
            FROM cash_registers
            WHERE estado='ABIERTA'
            ORDER BY id DESC
            LIMIT 1
            """
        )

        cash = self.cursor.fetchone()

        if not cash:
            messagebox.showwarning(
                "Caja",
                "No hay una caja abierta.",
            )
            return

        self.cursor.execute(
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
            WHERE caja_id=?
            AND (
                tipo <> 'VENTA'
                OR metodo_pago='EFECTIVO'
            )
            """,
            (cash[0],),
        )

        expected = round(
            cash[1] + self.cursor.fetchone()[0],
            2,
        )

        counted = simpledialog.askfloat(
            "Cerrar caja",
            f"Efectivo esperado: RD$ {expected:.2f}\n"
            "Monto contado:",
            minvalue=0,
            parent=self.root,
        )

        if counted is None:
            return

        difference = round(
            counted - expected,
            2,
        )

        self.cursor.execute(
            """
            UPDATE cash_registers
            SET fecha_cierre=CURRENT_TIMESTAMP,
                monto_esperado=?,
                monto_contado=?,
                diferencia=?,
                estado='CERRADA'
            WHERE id=?
            """,
            (
                expected,
                counted,
                difference,
                cash[0],
            ),
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

        self.dashboard_caja.refresh()

        self.set_status(
            f"Caja cerrada. Diferencia: RD$ {difference:.2f}"
        )

        messagebox.showinfo(
            "Caja",
            f"Caja cerrada. Diferencia: RD$ {difference:.2f}",
        )


    def mostrar_acerca_de(self):
        """Ventana «Acerca de» con la versión, autor y enlace del proyecto."""

        about = ctk.CTkToplevel(self.root)

        theme.prepare_toplevel(
            about,
            "Acerca de",
            (460, 340),
            self.base_path,
            modal=True,
        )

        about.attributes("-topmost", True)
        about.after(
            150,
            lambda: (
                about.attributes("-topmost", False)
                if about.winfo_exists()
                else None
            ),
        )

        about.focus_force()

        card = cards.Card(
            about,
            padding=20,
        )

        card.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18,
        )

        title = ctk.CTkLabel(
            card.body,
            text=theme.APP_NAME,
            font=theme.font("display"),
            text_color=theme.color("accent"),
        )

        title.pack(pady=(6, 2))

        subtitle = ctk.CTkLabel(
            card.body,
            text="Sistema de gestión y facturación de escritorio",
            text_color=theme.color("text_muted"),
        )

        subtitle.pack(pady=(0, 10))

        version = ctk.CTkLabel(
            card.body,
            text=(
                f"Versión {theme.APP_VERSION} · "
                "Desarrollado por K.A.R.M."
            ),
            text_color=theme.color("text"),
        )

        version.pack(pady=(0, 4))

        stack = ctk.CTkLabel(
            card.body,
            text="CustomTkinter · SQLite · ReportLab",
            text_color=theme.color("text_muted"),
        )

        stack.pack(pady=(0, 14))

        link = ctk.CTkLabel(
            card.body,
            text=theme.CREATOR_URL,
            font=theme.font("link"),
            text_color=theme.color("accent"),
            cursor="hand2",
        )

        link.pack(pady=(0, 16))

        link.bind(
            "<Button-1>",
            lambda event: webbrowser.open_new_tab(
                theme.CREATOR_URL
            ),
        )

        AppButton(
            card.body,
            text="Cerrar",
            command=about.destroy,
            variant="primary",
            width=12,
        ).pack()

        about.bind(
            "<Escape>",
            lambda event: about.destroy(),
        )


    def crear_pestaña_facturacion(self):
        """Crea la pestaña de facturación."""

        self.notebook.add(
            "Facturación"
        )

        tab = self.notebook.tab(
            "Facturación"
        )

        self.tabs["invoice"] = tab

        # ----------------------------------------------------
        # CONTENEDOR CON SCROLL
        # ----------------------------------------------------

        inner = ctk.CTkScrollableFrame(
            tab,
            fg_color=theme.color("window"),
            corner_radius=0,
            scrollbar_button_color=theme.color("scroll_thumb"),
            scrollbar_button_hover_color=theme.color("scroll_hover"),
        )

        inner.pack(
            fill="both",
            expand=True,
        )

        columns = ctk.CTkFrame(
            inner,
            fg_color="transparent",
        )

        columns.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12,
        )

        columns.columnconfigure(
            0,
            minsize=360,
        )

        columns.columnconfigure(
            1,
            weight=1,
        )

        self._build_invoice_form(columns)
        self._build_invoice_detail(columns)


    def _build_invoice_form(self, parent):
        """Columna izquierda de la factura."""

        card = cards.Card(
            parent,
            title="Datos del comprobante",
            subtitle="Cliente, número y método de pago",
            padding=14,
        )

        card.grid(
            row=0,
            column=0,
            sticky="new",
            padx=(0, 10),
        )

        body = card.body

        head = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        head.pack(
            fill="x",
        )

        head.columnconfigure(
            1,
            weight=1,
        )

        self.num_factura = tk.StringVar(
            value=self.generar_numero_factura()
        )

        inputs.labeled_entry(
            head,
            "Factura No.",
            textvariable=self.num_factura,
            state="readonly",
            row=0,
            background="surface",
        )

        self.fecha_factura = tk.StringVar(
            value=datetime.now().strftime("%d/%m/%Y")
        )

        inputs.labeled_entry(
            head,
            "Fecha",
            textvariable=self.fecha_factura,
            state="readonly",
            row=1,
            background="surface",
        )

        self.cliente_var = tk.StringVar()

        _caption, self.combo_cliente = inputs.labeled_combobox(
            head,
            "Cliente",
            textvariable=self.cliente_var,
            width=34,
            row=2,
            background="surface",
        )

        self.metodo_pago_var = tk.StringVar(
            value="EFECTIVO"
        )

        _caption, self.combo_metodo_pago = inputs.labeled_combobox(
            head,
            "Método de pago",
            values=(
                "EFECTIVO",
                "TARJETA",
                "TRANSFERENCIA",
                "CREDITO",
                "OTRO",
            ),
            textvariable=self.metodo_pago_var,
            width=18,
            row=3,
            background="surface",
        )

        theme.separator(
            body,
            fill=tk.X,
            pady=10,
        )

        cards.label(
            body,
            "Agregar producto",
            font_role="body_bold",
            background="surface",
        ).pack(
            anchor="w",
        )

        form = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        form.pack(
            fill="x",
            pady=(6, 0),
        )

        form.columnconfigure(
            1,
            weight=1,
        )

        self.producto_var = tk.StringVar()

        _caption, self.combo_producto = inputs.labeled_combobox(
            form,
            "Producto",
            textvariable=self.producto_var,
            width=28,
            row=0,
            on_select=self.seleccionar_producto,
            background="surface",
        )

        self.precio_var = tk.StringVar()

        inputs.labeled_entry(
            form,
            "Precio",
            textvariable=self.precio_var,
            width=12,
            row=1,
            background="surface",
        )

        self.cantidad_var = tk.StringVar(
            value="1"
        )

        _caption, cantidad_entry = inputs.labeled_entry(
            form,
            "Cantidad",
            textvariable=self.cantidad_var,
            width=12,
            row=2,
            background="surface",
        )

        cantidad_entry.bind(
            "<Return>",
            lambda event: self.agregar_item(),
        )

        AppButton(
            form,
            text="Agregar producto",
            command=self.agregar_item,
            variant="success",
            tooltip="Agrega el producto a la factura (Enter)",
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(12, 2),
        )

        theme.separator(
            body,
            fill=tk.X,
            pady=10,
        )

        cards.label(
            body,
            "Productos disponibles",
            font_role="body_bold",
            background="surface",
        ).pack(
            anchor="w",
        )

        search = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        search.pack(
            fill="x",
            pady=(6, 4),
        )

        self.invoice_search = inputs.make_entry(
            search,
        )

        self.invoice_search.pack(
            side="left",
            fill="x",
            expand=True,
        )

        self.invoice_search.bind(
            "<KeyRelease>",
            lambda event: self.cargar_catalogo_factura(),
        )

        AppButton(
            search,
            text="Limpiar",
            command=self._limpiar_busqueda_catalogo,
            variant="ghost",
            size="small",
            width=8,
        ).pack(
            side="left",
            padx=8,
        )

        self.catalogo_table = tables.DataTable(
            body,
            columns=(
                "Código",
                "Producto",
                "Precio",
                "Stock",
            ),
            widths=(
                90,
                180,
                90,
                60,
            ),
            anchors=(
                "w",
                "w",
                "e",
                "e",
            ),
            height=7,
        )

        self.catalogo_table.pack(
            fill="both",
            expand=True,
        )

        self.tree_catalogo = self.catalogo_table.tree

        self.tree_catalogo.bind(
            "<Double-1>",
            self.seleccionar_producto_catalogo,
        )

        self.tree_catalogo.bind(
            "<Return>",
            lambda event: self.seleccionar_producto_catalogo(event),
        )

        theme.Tooltip(
            self.tree_catalogo,
            "Doble clic sobre un producto para cargarlo en el formulario",
        )


    def _limpiar_busqueda_catalogo(self):
        self.invoice_search.delete(
            0,
            tk.END,
        )

        self.cargar_catalogo_factura()


    def cargar_catalogo_factura(self):
        """Refresca el catálogo auxiliar de la pestaña de facturación."""

        if getattr(
            self,
            "catalogo_table",
            None,
        ) is None:
            return

        termino = self.invoice_search.get().strip()

        self.catalogo_table.clear()

        try:
            if termino:
                patron = f"%{termino}%"

                self.cursor.execute(
                    """
                    SELECT codigo, nombre, precio, stock
                    FROM productos
                    WHERE activo=1
                    AND (
                        codigo LIKE ?
                        OR nombre LIKE ?
                    )
                    ORDER BY nombre
                    LIMIT 200
                    """,
                    (
                        patron,
                        patron,
                    ),
                )

            else:
                self.cursor.execute(
                    """
                    SELECT codigo, nombre, precio, stock
                    FROM productos
                    WHERE activo=1
                    ORDER BY nombre
                    LIMIT 200
                    """
                )

            for codigo, nombre, precio, stock in self.cursor.fetchall():
                self.catalogo_table.add_row(
                    (
                        codigo,
                        nombre,
                        f"RD$ {precio:.2f}",
                        stock,
                    )
                )

            self.catalogo_table.restripe()

        except sqlite3.Error:
            logging.exception(
                "No se pudo cargar el catálogo de la factura"
            )


    def seleccionar_producto_catalogo(self, event=None):
        """Carga en el formulario el producto elegido en el catálogo."""

        selected = self.tree_catalogo.selection()

        if not selected:
            return

        valores = self.tree_catalogo.item(
            selected[0]
        )["values"]

        if not valores:
            return

        self.producto_var.set(
            f"{valores[0]} - {valores[1]}"
        )

        precio = str(
            valores[2]
        ).replace(
            "RD$",
            "",
        ).strip()

        self.precio_var.set(precio)
        self.cantidad_var.set("1")

        self.combo_producto.focus_set()


    def _build_invoice_detail(self, parent):
        """Columna derecha: detalle, totales y acciones."""

        card = cards.Card(
            parent,
            title="Detalle de la factura",
            subtitle="Productos, impuestos y total",
            padding=14,
        )

        card.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        body = card.body

        self.items_table = tables.DataTable(
            body,
            columns=(
                "Código",
                "Producto",
                "Cantidad",
                "Precio",
                "Subtotal",
            ),
            headings=(
                "Código",
                "Producto",
                "Cantidad",
                "Precio unit.",
                "Subtotal",
            ),
            widths=(
                130,
                320,
                90,
                120,
                130,
            ),
            anchors=(
                "w",
                "w",
                "e",
                "e",
                "e",
            ),
            height=10,
            hscroll=True,
        )

        self.items_table.pack(
            fill="both",
            expand=True,
        )

        self.tree_items = self.items_table.tree

        self.tree_items.bind(
            "<Delete>",
            lambda event: self.eliminar_item(),
        )

        totals = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        totals.pack(
            fill="x",
            pady=(14, 0),
        )

        self.subtotal_var = tk.StringVar(
            value="RD$ 0.00"
        )

        self.itbis_var = tk.StringVar(
            value="RD$ 0.00"
        )

        self.total_var = tk.StringVar(
            value="RD$ 0.00"
        )

        blocks = (
            (
                "Subtotal",
                self.subtotal_var,
                "text",
                "title",
            ),
            (
                "ITBIS (18%)",
                self.itbis_var,
                "text",
                "title",
            ),
            (
                "Total a pagar",
                self.total_var,
                "success",
                "metric",
            ),
        )

        for title, variable, tone, font_role in blocks:
            block = ctk.CTkFrame(
                totals,
                fg_color="transparent",
            )

            block.pack(
                side="left",
                padx=(0, 28),
            )

            cards.label(
                block,
                title.upper(),
                font_role="metric_title",
                tone="text_muted",
                background="surface",
            ).pack(
                anchor="w",
            )

            value = ctk.CTkLabel(
                block,
                textvariable=variable,
                font=theme.font(font_role),
                anchor="w",
                text_color=theme.color(tone),
            )

            value.pack(
                anchor="w",
            )

        actions = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        actions.pack(
            fill="x",
            pady=(16, 2),
        )

        AppButton(
            actions,
            text="Guardar factura y crear PDF",
            command=self.generar_factura,
            variant="primary",
            tooltip="Registra la factura, descuenta el stock y genera el PDF",
        ).pack(
            side="left",
            padx=(0, 6),
        )

        AppButton(
            actions,
            text="Nueva factura",
            command=self.nueva_factura,
            variant="neutral",
            tooltip="Limpia el formulario para una nueva venta (Ctrl+N)",
        ).pack(
            side="left",
            padx=6,
        )

        AppButton(
            actions,
            text="Quitar producto",
            command=self.eliminar_item,
            variant="danger",
            tooltip="Quita el producto seleccionado del detalle (Supr)",
        ).pack(
            side="left",
            padx=6,
        )

        hint = cards.label(
            actions,
            "Enter agrega el producto seleccionado en la lista",
            font_role="small",
            tone="text_muted",
            background="surface",
        )

        hint.pack(
            side="right",
        )


    def crear_pestaña_productos(self):
        """Crea la pestaña de gestión de productos."""

        self.notebook.add(
            "Inventario"
        )

        tab = self.notebook.tab(
            "Inventario"
        )

        self.tabs["products"] = tab

        wrapper = ctk.CTkFrame(
            tab,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=12,
        )

        card = cards.Card(
            wrapper,
            title="Productos",
            subtitle=(
                "Registre, actualice o desactive."
            ),
            padding=14,
        )

        card.pack(
            fill="both",
            expand=True,
        )

        body = card.body

        form = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        form.pack(
            fill="x",
        )

        form.columnconfigure(
            1,
            weight=1,
        )

        form.columnconfigure(
            3,
            weight=1,
        )

        self.prod_codigo = inputs.labeled_entry(
            form,
            "Código",
            row=0,
            column=0,
            entry_sticky="ew",
        )[1]

        self.prod_nombre = inputs.labeled_entry(
            form,
            "Nombre",
            row=0,
            column=2,
            entry_sticky="ew",
        )[1]

        self.prod_precio = inputs.labeled_entry(
            form,
            "Precio",
            row=1,
            column=0,
            entry_sticky="ew",
        )[1]

        self.prod_stock = inputs.labeled_entry(
            form,
            "Stock",
            row=1,
            column=2,
            entry_sticky="ew",
        )[1]

        actions = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        actions.pack(
            fill="x",
            pady=(12, 0),
        )

        AppButton(
            actions,
            text="Agregar",
            command=self.agregar_producto,
            variant="success",
            tooltip="Registra un producto nuevo",
        ).pack(
            side="left",
            padx=(0, 6),
        )

        AppButton(
            actions,
            text="Actualizar",
            command=self.actualizar_producto,
            variant="warning",
            tooltip="Actualiza el producto seleccionado en la tabla",
        ).pack(
            side="left",
            padx=6,
        )

        AppButton(
            actions,
            text="Desactivar",
            command=self.eliminar_producto,
            variant="danger",
            tooltip="Desactiva el producto seleccionado",
        ).pack(
            side="left",
            padx=6,
        )

        AppButton(
            actions,
            text="Limpiar",
            command=self.limpiar_form_producto,
            variant="neutral",
            tooltip="Vacía el formulario",
        ).pack(
            side="left",
            padx=6,
        )

        AppButton(
            actions,
            text="Movimientos de inventario",
            command=self.abrir_movimientos_inventario,
            variant="ghost",
            tooltip="Registra entradas, ajustes y devoluciones",
        ).pack(
            side="right",
        )

        search = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        search.pack(
            fill="x",
            pady=(14, 6),
        )

        cards.label(
            search,
            "Buscar por código o nombre",
            font_role="body_bold",
            background="surface",
        ).pack(
            side="left",
            padx=(0, 8),
        )

        self.prod_buscar = inputs.make_entry(
            search,
        )

        self.prod_buscar.pack(
            side="left",
            fill="x",
            expand=True,
        )

        self.prod_buscar.bind(
            "<KeyRelease>",
            lambda event: self.cargar_productos(),
        )

        AppButton(
            search,
            text="Limpiar",
            command=self._limpiar_busqueda_producto,
            variant="ghost",
            size="small",
            width=8,
        ).pack(
            side="left",
            padx=8,
        )

        self.products_count = cards.Badge(
            search,
            text="0 productos",
            tone="neutral",
        )

        self.products_count.pack(
            side="right",
        )

        self.table_productos = tables.DataTable(
            body,
            columns=(
                "ID",
                "Código",
                "Nombre",
                "Precio",
                "Stock",
            ),
            widths=(
                60,
                120,
                320,
                120,
                90,
            ),
            anchors=(
                "w",
                "w",
                "w",
                "e",
                "e",
            ),
            height=12,
            hscroll=True,
        )

        self.table_productos.pack(
            fill="both",
            expand=True,
        )

        self.tree_productos = self.table_productos.tree

        self.tree_productos.bind(
            "<ButtonRelease-1>",
            self.seleccionar_producto_tabla,
        )

        theme.Tooltip(
            self.tree_productos,
            "Seleccione una fila para cargarla en el formulario",
        )

    def crear_pestaña_clientes(self):
        """Crea la pestaña de gestión de clientes."""

        self.notebook.add(
            "Clientes"
        )

        tab = self.notebook.tab(
            "Clientes"
        )

        self.tabs["customers"] = tab

        wrapper = ctk.CTkFrame(
            tab,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=12,
        )

        card = cards.Card(
            wrapper,
            title="Clientes",
            subtitle="Datos de contacto que se imprimen en la factura",
            padding=14,
        )

        card.pack(
            fill="both",
            expand=True,
        )

        body = card.body

        # ==========================================================
        # FORMULARIO
        # ==========================================================

        form = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        form.pack(
            fill="x",
        )

        form.columnconfigure(
            1,
            weight=1,
        )

        form.columnconfigure(
            3,
            weight=1,
        )

        self.cli_nombre = inputs.labeled_entry(
            form,
            "Nombre",
            row=0,
            column=0,
            entry_sticky="ew",
        )[1]

        self.cli_cedula = inputs.labeled_entry(
            form,
            "Cédula",
            row=0,
            column=2,
            entry_sticky="ew",
        )[1]

        self.cli_telefono = inputs.labeled_entry(
            form,
            "Teléfono",
            row=1,
            column=0,
            entry_sticky="ew",
        )[1]

        self.cli_direccion = inputs.labeled_entry(
            form,
            "Dirección",
            row=1,
            column=2,
            entry_sticky="ew",
        )[1]

        # ==========================================================
        # ACCIONES
        # ==========================================================

        actions = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        actions.pack(
            fill="x",
            pady=(12, 0),
        )

        AppButton(
            actions,
            text="Agregar",
            command=self.agregar_cliente,
            variant="success",
            tooltip="Registra un cliente nuevo",
        ).pack(
            side="left",
            padx=(0, 6),
        )

        AppButton(
            actions,
            text="Actualizar",
            command=self.actualizar_cliente,
            variant="warning",
            tooltip="Actualiza el cliente seleccionado",
        ).pack(
            side="left",
            padx=6,
        )

        AppButton(
            actions,
            text="Desactivar",
            command=self.eliminar_cliente,
            variant="danger",
            tooltip="Desactiva el cliente conservando su historial",
        ).pack(
            side="left",
            padx=6,
        )

        AppButton(
            actions,
            text="Limpiar",
            command=self.limpiar_form_cliente,
            variant="neutral",
            tooltip="Vacía el formulario",
        ).pack(
            side="left",
            padx=6,
        )

        # ==========================================================
        # BUSCADOR
        # ==========================================================

        search = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        search.pack(
            fill="x",
            pady=(14, 6),
        )

        cards.label(
            search,
            "Buscar por nombre o cédula",
            font_role="body_bold",
            background="surface",
        ).pack(
            side="left",
            padx=(0, 8),
        )

        self.cli_buscar = inputs.make_entry(
            search,
        )

        self.cli_buscar.pack(
            side="left",
            fill="x",
            expand=True,
        )

        self.cli_buscar.bind(
            "<KeyRelease>",
            lambda event: self.cargar_clientes(),
        )

        AppButton(
            search,
            text="Limpiar",
            command=self._limpiar_busqueda_cliente,
            variant="ghost",
            size="small",
            width=8,
        ).pack(
            side="left",
            padx=8,
        )

        self.customers_count = cards.Badge(
            search,
            text="0 clientes",
            tone="neutral",
        )

        self.customers_count.pack(
            side="right",
        )

        # ==========================================================
        # TABLA
        # ==========================================================

        self.table_clientes = tables.DataTable(
            body,
            columns=(
                "ID",
                "Nombre",
                "Cédula",
                "Teléfono",
                "Dirección",
            ),
            widths=(
                60,
                230,
                140,
                140,
                280,
            ),
            anchors=(
                "w",
                "w",
                "w",
                "w",
                "w",
            ),
            height=12,
            hscroll=True,
        )

        self.table_clientes.pack(
            fill="both",
            expand=True,
        )

        self.tree_clientes = self.table_clientes.tree

        self.tree_clientes.bind(
            "<ButtonRelease-1>",
            self.seleccionar_cliente_tabla,
        )

        theme.Tooltip(
            self.tree_clientes,
            "Seleccione una fila para cargarla en el formulario",
        )


    def crear_pestaña_historial(self):
        """Crea la pestaña de historial de facturas."""

        self.notebook.add(
            "Facturas guardadas"
        )

        tab = self.notebook.tab(
            "Facturas guardadas"
        )

        self.tabs["history"] = tab

        wrapper = ctk.CTkFrame(
            tab,
            fg_color="transparent",
        )

        wrapper.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=12,
        )

        card = cards.Card(
            wrapper,
            title="Facturas guardadas",
            subtitle="Consulte, cobre o anule comprobantes ya emitidos",
            padding=14,
        )

        card.pack(
            fill="both",
            expand=True,
        )

        body = card.body

        # ==========================================================
        # ACCIONES
        # ==========================================================

        actions = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        actions.pack(
            fill="x",
        )

        AppButton(
            actions,
            text="Ver detalles",
            command=self.ver_detalles_factura,
            variant="primary",
            tooltip="Muestra los productos y totales de la factura",
        ).pack(
            side="left",
            padx=(0, 6),
        )

        AppButton(
            actions,
            text="Crear PDF de nuevo",
            command=self.regenerar_pdf,
            variant="success",
            tooltip="Vuelve a generar el PDF de la factura seleccionada",
        ).pack(
            side="left",
            padx=6,
        )

        AppButton(
            actions,
            text="Registrar abono",
            command=self.registrar_abono,
            variant="warning",
            tooltip="Registra un pago parcial o total",
        ).pack(
            side="left",
            padx=6,
        )

        AppButton(
            actions,
            text="Anular factura",
            command=self.anular_factura,
            variant="danger",
            tooltip="Anula la factura y reintegra el stock",
        ).pack(
            side="left",
            padx=6,
        )

        # ==========================================================
        # BUSCADOR
        # ==========================================================

        search = ctk.CTkFrame(
            body,
            fg_color="transparent",
        )

        search.pack(
            fill="x",
            pady=(14, 6),
        )

        cards.label(
            search,
            "Buscar factura o cliente",
            font_role="body_bold",
            background="surface",
        ).pack(
            side="left",
            padx=(0, 8),
        )

        self.hist_buscar = inputs.make_entry(
            search,
        )

        self.hist_buscar.pack(
            side="left",
            fill="x",
            expand=True,
        )

        self.hist_buscar.bind(
            "<KeyRelease>",
            lambda event: self.cargar_historial(),
        )

        AppButton(
            search,
            text="Limpiar",
            command=self._limpiar_busqueda_historial,
            variant="ghost",
            size="small",
            width=8,
        ).pack(
            side="left",
            padx=8,
        )

        self.invoices_count = cards.Badge(
            search,
            text="0 facturas",
            tone="neutral",
        )

        self.invoices_count.pack(
            side="right",
        )

        # ==========================================================
        # TABLA DE HISTORIAL
        # ==========================================================

        self.table_historial = tables.DataTable(
            body,
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
            widths=(
                50,
                120,
                100,
                240,
                110,
                110,
                110,
                100,
            ),
            anchors=(
                "w",
                "w",
                "w",
                "w",
                "e",
                "e",
                "e",
                "w",
            ),
            height=12,
            hscroll=True,
        )

        self.table_historial.pack(
            fill="both",
            expand=True,
        )

        self.tree_historial = self.table_historial.tree

        self.tree_historial.bind(
            "<Double-1>",
            lambda event: self.ver_detalles_factura(),
        )

        theme.Tooltip(
            self.tree_historial,
            "Doble clic para ver el detalle de la factura",
        )


    def _limpiar_busqueda_historial(self):
        self.hist_buscar.delete(
            0,
            tk.END,
        )

        self.cargar_historial()


    # ==============================================================
    # MÉTODOS DE PRODUCTOS
    # ==============================================================

    def agregar_producto(self):
        if not self.require_permission("manage_products"):
            return

        codigo = self.prod_codigo.get().strip()
        nombre = self.prod_nombre.get().strip()
        precio = self.prod_precio.get().strip()
        stock = self.prod_stock.get().strip()

        if not all([codigo, nombre, precio, stock]):
            messagebox.showwarning(
                "Advertencia",
                "Todos los campos son obligatorios",
            )
            return

        try:
            try:
                precio = float(precio)
                stock = int(stock)
            except ValueError:
                raise ValueError(
                    "Precio y Stock deben ser números válidos"
                ) from None

            if precio <= 0:
                raise ValueError(
                    "El precio debe ser mayor a 0"
                )

            if stock < 0:
                raise ValueError(
                    "El stock no puede ser negativo"
                )

            products_service.create_product(
                self.conn,
                codigo,
                nombre,
                precio,
                stock,
                self.current_user.get("id"),
            )

            messagebox.showinfo(
                "Éxito",
                "Producto agregado correctamente",
            )

            self.limpiar_form_producto()
            self.cargar_productos()
            self.cargar_datos()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Error",
                "El código del producto ya existe",
            )

        except ValueError as exc:
            messagebox.showerror(
                "Error de validación",
                str(exc),
            )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Error al agregar producto: {exc}",
            )

    def actualizar_producto(self):
        if not self.require_permission("manage_products"):
            return

        selected_items = self.tree_productos.selection()

        if not selected_items:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione un producto de la tabla",
            )
            return

        codigo = self.prod_codigo.get().strip()
        nombre = self.prod_nombre.get().strip()
        precio = self.prod_precio.get().strip()
        stock = self.prod_stock.get().strip()

        if not all([codigo, nombre, precio, stock]):
            messagebox.showwarning(
                "Advertencia",
                "Todos los campos son obligatorios",
            )
            return

        
        selected_item = selected_items[0]

        item = self.tree_productos.item(
            selected_item
        )

        values = item["values"]
        producto_id = int(values[0])

        try:
            try:
                precio = float(precio)
                stock = int(stock)
            except ValueError:
                raise ValueError(
                    "Precio y Stock deben ser números válidos"
                ) from None

            if precio <= 0:
                raise ValueError(
                    "El precio debe ser mayor a 0"
                )

            if stock < 0:
                raise ValueError(
                    "El stock no puede ser negativo"
                )

            products_service.update_product(
                self.conn,
                producto_id,
                codigo,
                nombre,
                precio,
                stock,
                self.current_user.get("id"),
            )

            messagebox.showinfo(
                "Éxito",
                "Producto actualizado correctamente",
            )

            self.limpiar_form_producto()
            self.cargar_productos()
            self.cargar_datos()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Error",
                "El código del producto ya existe",
            )

        except ValueError as exc:
            messagebox.showerror(
                "Error de validación",
                str(exc),
            )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Error al actualizar producto: {exc}",
            )

    def eliminar_producto(self):
        if not self.require_permission("manage_products"):
            return

        selected_items = self.tree_productos.selection()

        if not selected_items:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione un producto de la tabla",
            )
            return

        if messagebox.askyesno(
            "Confirmar",
            "¿Está seguro de eliminar este producto?",
        ):
            selected_item = selected_items[0]

            item = self.tree_productos.item(
                selected_item
            )

            producto_id = int(item["values"][0])

            try:
                products_service.deactivate_product(
                    self.conn,
                    producto_id,
                    self.current_user.get("id"),
                )

                messagebox.showinfo(
                    "Éxito",
                    "Producto eliminado correctamente",
                )

                self.limpiar_form_producto()
                self.cargar_productos()
                self.cargar_datos()

            except Exception as exc:
                messagebox.showerror(
                    "Error",
                    f"Error al eliminar producto: {exc}",
                )


    def limpiar_form_producto(self):
        self.prod_codigo.delete(0, tk.END)
        self.prod_nombre.delete(0, tk.END)
        self.prod_precio.delete(0, tk.END)
        self.prod_stock.delete(0, tk.END)


    def seleccionar_producto_tabla(self, event=None):
        selected_items = self.tree_productos.selection()

        if not selected_items:
            return

        selected_item = selected_items[0]

        item = self.tree_productos.item(
            selected_item
        )

        values = item["values"]

        self.prod_codigo.delete(0, tk.END)
        self.prod_codigo.insert(0, values[1])

        self.prod_nombre.delete(0, tk.END)
        self.prod_nombre.insert(0, values[2])

        self.prod_precio.delete(0, tk.END)
        self.prod_precio.insert(0, values[3])

        self.prod_stock.delete(0, tk.END)
        self.prod_stock.insert(0, values[4])


    def _actualizar_badge(self, badge, texto, tone=None):
        """Actualiza el contador de una insignia sin romper si cambia su API."""

        if badge is None:
            return

        try:
            if tone is not None:
                badge.configure(
                    text=texto,
                    tone=tone,
                )
            else:
                badge.configure(
                    text=texto,
                )

        except (tk.TclError, TypeError):
            etiqueta = getattr(
                badge,
                "label",
                None,
            )

            if etiqueta is not None:
                etiqueta.configure(
                    text=texto,
                )


    def cargar_productos(self):
        self.table_productos.clear()

        filas = list(
            products_service.list_products(
                self.conn,
                self.prod_buscar.get(),
            )
        )

        for row in filas:
            self.table_productos.add_row(row)

        self.table_productos.restripe()

        self._actualizar_badge(
            getattr(
                self,
                "products_count",
                None,
            ),
            f"{len(filas)} producto{'s' if len(filas) != 1 else ''}",
        )

        # El catálogo de la pestaña de factura
        # lee la misma tabla.
        self.cargar_catalogo_factura()


    # ==============================================================
    # MÉTODOS DE CLIENTES
    # ==============================================================

    def agregar_cliente(self):
        if not self.require_permission("manage_customers"):
            return

        nombre = self.cli_nombre.get().strip()
        cedula = self.cli_cedula.get().strip()
        telefono = self.cli_telefono.get().strip()
        direccion = self.cli_direccion.get().strip()

        if not nombre:
            messagebox.showwarning(
                "Advertencia",
                "El nombre es obligatorio",
            )
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

            messagebox.showinfo(
                "Éxito",
                "Cliente agregado correctamente",
            )

            self.limpiar_form_cliente()
            self.cargar_clientes()
            self.cargar_datos()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Error",
                "La cédula ya está registrada",
            )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Error al agregar cliente: {exc}",
            )


    def actualizar_cliente(self):
        if not self.require_permission("manage_customers"):
            return

        selected = self.tree_clientes.selection()

        if not selected:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione un cliente de la tabla",
            )
            return

        item = self.tree_clientes.item(
            selected[0]
        )

        cliente_id = item["values"][0]

        nombre = self.cli_nombre.get().strip()
        cedula = self.cli_cedula.get().strip()
        telefono = self.cli_telefono.get().strip()
        direccion = self.cli_direccion.get().strip()

        if not nombre:
            messagebox.showwarning(
                "Advertencia",
                "El nombre es obligatorio",
            )
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

            messagebox.showinfo(
                "Éxito",
                "Cliente actualizado correctamente",
            )

            self.limpiar_form_cliente()
            self.cargar_clientes()
            self.cargar_datos()

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Error al actualizar cliente: {exc}",
            )


    def eliminar_cliente(self):
        if not self.require_permission("manage_customers"):
            return

        selected = self.tree_clientes.selection()

        if not selected:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione un cliente de la tabla",
            )
            return

        if not messagebox.askyesno(
            "Confirmar",
            "¿Está seguro de desactivar este cliente?\n\n"
            "Se conservará su historial de facturas.",
        ):
            return

        item = self.tree_clientes.item(
            selected[0]
        )

        cliente_id = item["values"][0]

        try:
            customers_service.deactivate_customer(
                self.conn,
                cliente_id,
                self.current_user.get("id"),
            )

            messagebox.showinfo(
                "Éxito",
                "Cliente desactivado correctamente. "
                "Su historial se conserva.",
            )

            self.limpiar_form_cliente()
            self.cargar_clientes()
            self.cargar_datos()

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Error al eliminar cliente: {exc}",
            )


    def limpiar_form_cliente(self):
        self.cli_nombre.delete(0, tk.END)
        self.cli_cedula.delete(0, tk.END)
        self.cli_telefono.delete(0, tk.END)
        self.cli_direccion.delete(0, tk.END)


    def seleccionar_cliente_tabla(self, event=None):
        selected = self.tree_clientes.selection()

        if not selected:
            return

        item = self.tree_clientes.item(
            selected[0]
        )

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
        self.table_clientes.clear()

        filas = list(
            customers_service.list_customers(
                self.conn,
                self.cli_buscar.get(),
            )
        )

        for row in filas:
            self.table_clientes.add_row(row)

        self.table_clientes.restripe()

        self._actualizar_badge(
            getattr(
                self,
                "customers_count",
                None,
            ),
            f"{len(filas)} cliente{'s' if len(filas) != 1 else ''}",
        )


    # ==============================================================
    # MÉTODOS DE FACTURACIÓN
    # ==============================================================

    def generar_numero_factura(self):
        return invoice_service.next_invoice_number(
            self.conn
        )


    def seleccionar_producto(self, event=None):
        producto_str = self.producto_var.get()

        if not producto_str:
            return

        # Formato:
        # CODIGO - Nombre
        codigo = producto_str.split(
            " - ",
            1,
        )[0]

        self.cursor.execute(
            "SELECT precio FROM productos WHERE codigo=?",
            (codigo,),
        )

        result = self.cursor.fetchone()

        if result:
            self.precio_var.set(
                f"{result[0]:.2f}"
            )


    def agregar_item(self):
        producto_str = self.producto_var.get()
        precio_str = self.precio_var.get()
        cantidad_str = self.cantidad_var.get()

        if not all(
            [
                producto_str,
                precio_str,
                cantidad_str,
            ]
        ):
            messagebox.showwarning(
                "Advertencia",
                "Complete todos los campos",
            )
            return

        try:
            precio = float(precio_str)

            if precio <= 0:
                raise ValueError(
                    "El precio debe ser mayor a 0"
                )

            cantidad = int(cantidad_str)

            if cantidad <= 0:
                raise ValueError(
                    "La cantidad debe ser mayor a 0"
                )

            # Extraer código y nombre.
            if " - " not in producto_str:
                raise ValueError(
                    "Seleccione un producto válido de la lista"
                )

            codigo, nombre = producto_str.split(
                " - ",
                1,
            )

            # Verificar stock disponible.
            self.cursor.execute(
                """
                SELECT stock
                FROM productos
                WHERE codigo = ?
                """,
                (codigo,),
            )

            stock_actual = self.cursor.fetchone()

            if not stock_actual:
                raise ValueError(
                    "Producto no encontrado"
                )

            if stock_actual[0] < cantidad:
                raise ValueError(
                    f"Stock insuficiente. "
                    f"Disponible: {stock_actual[0]}"
                )

            # Si el producto ya está en la factura,
            # aumentar su cantidad.
            for item in self.items_factura:
                if item["codigo"] == codigo:
                    nueva_cantidad = (
                        item["cantidad"] + cantidad
                    )

                    if nueva_cantidad > stock_actual[0]:
                        raise ValueError(
                            f"Stock insuficiente. "
                            f"Disponible: {stock_actual[0]}"
                        )

                    item["cantidad"] = nueva_cantidad
                    item["subtotal"] = (
                        item["precio"] * nueva_cantidad
                    )

                    self._refrescar_items_factura()
                    self.actualizar_totales()

                    self.producto_var.set("")
                    self.precio_var.set("")
                    self.cantidad_var.set("1")

                    return

            subtotal = precio * cantidad

            # Agregar a la tabla.
            self.items_table.add_row(
                (
                    codigo,
                    nombre,
                    cantidad,
                    f"RD$ {precio:.2f}",
                    f"RD$ {subtotal:.2f}",
                )
            )

            self.items_table.restripe()

            # Agregar a la lista interna.
            self.items_factura.append(
                {
                    "codigo": codigo,
                    "nombre": nombre,
                    "cantidad": cantidad,
                    "precio": precio,
                    "subtotal": subtotal,
                }
            )

            self.actualizar_totales()

            # Limpiar campos.
            self.producto_var.set("")
            self.precio_var.set("")
            self.cantidad_var.set("1")

        except ValueError as exc:
            messagebox.showerror(
                "Error de validación",
                str(exc),
            )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Error al agregar ítem: {exc}",
            )


    def eliminar_item(self):
        if not self.tree_items.selection():
            messagebox.showwarning(
                "Advertencia",
                "Seleccione un item para eliminar",
            )
            return

        # remove_selected borra la fila y devuelve
        # su posición.
        index = self.items_table.remove_selected()

        if index is None:
            return

        del self.items_factura[index]

        self.items_table.restripe()

        self.actualizar_totales()


    def _refrescar_items_factura(self):
        self.items_table.clear()

        for item in self.items_factura:
            self.items_table.add_row(
                (
                    item["codigo"],
                    item["nombre"],
                    item["cantidad"],
                    f"RD$ {item['precio']:.2f}",
                    f"RD$ {item['subtotal']:.2f}",
                )
            )

        self.items_table.restripe()


    def actualizar_totales(self):
        subtotal = sum(
            item["subtotal"]
            for item in self.items_factura
        )

        itbis = subtotal * 0.18
        total = subtotal + itbis

        self.subtotal_var.set(
            f"RD$ {subtotal:.2f}"
        )

        self.itbis_var.set(
            f"RD$ {itbis:.2f}"
        )

        self.total_var.set(
            f"RD$ {total:.2f}"
        )


    def generar_factura(self):
        if not self.require_permission("create_invoices"):
            return

        if not self.items_factura:
            messagebox.showwarning(
                "Advertencia",
                "Agregue al menos un producto a la factura",
            )
            return

        cliente_str = self.cliente_var.get()

        if not cliente_str:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione un cliente",
            )
            return

        pdf_path = None

        try:
            # Obtener ID del cliente.
            cliente_id = invoice_service.find_customer(
                self.conn,
                cliente_str,
            )

            if cliente_id is None:
                messagebox.showerror(
                    "Error",
                    "Cliente no encontrado",
                )
                return

            # Calcular totales.
            subtotal, itbis, total = (
                invoice_service.calculate_totals(
                    self.items_factura
                )
            )

            numero = self.num_factura.get()
            fecha = invoice_service.invoice_date()
            metodo_pago = (
                self.metodo_pago_var.get()
                or "EFECTIVO"
            )

            estado = (
                "PENDIENTE"
                if metodo_pago == "CREDITO"
                else "PAGADA"
            )

            usuario_id = self.current_user.get("id")

            # ======================================================
            # INSERTAR FACTURA
            # ======================================================

            self.cursor.execute(
                """
                INSERT INTO facturas (
                    numero,
                    fecha,
                    cliente_id,
                    subtotal,
                    itbis,
                    total,
                    estado,
                    metodo_pago,
                    usuario_id
                )
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

            # ======================================================
            # INSERTAR ITEMS Y ACTUALIZAR STOCK
            # ======================================================

            for item in self.items_factura:

                self.cursor.execute(
                    """
                    SELECT id
                    FROM productos
                    WHERE codigo=?
                    """,
                    (item["codigo"],),
                )

                producto = self.cursor.fetchone()

                if not producto:
                    raise ValueError(
                        f"Producto no encontrado: {item['codigo']}"
                    )

                producto_id = producto[0]

                self.cursor.execute(
                    """
                    INSERT INTO factura_items (
                        factura_id,
                        producto_id,
                        cantidad,
                        precio_unitario,
                        subtotal
                    )
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

                self.cursor.execute(
                    """
                    UPDATE productos
                    SET stock = stock - ?
                    WHERE id = ?
                    AND stock >= ?
                    """,
                    (
                        item["cantidad"],
                        producto_id,
                        item["cantidad"],
                    ),
                )

                if self.cursor.rowcount != 1:
                    raise ValueError(
                        f"Stock insuficiente para el producto "
                        f"{item['codigo']}"
                    )

                self.cursor.execute(
                    """
                    INSERT INTO inventory_movements (
                        producto_id,
                        tipo,
                        cantidad,
                        motivo,
                        referencia,
                        usuario_id
                    )
                    VALUES (
                        ?,
                        'SALIDA',
                        ?,
                        ?,
                        ?,
                        ?
                    )
                    """,
                    (
                        producto_id,
                        item["cantidad"],
                        "Venta",
                        numero,
                        usuario_id,
                    ),
                )

            # ======================================================
            # PAGO
            # ======================================================

            if metodo_pago != "CREDITO":

                self.cursor.execute(
                    """
                    SELECT id
                    FROM payment_methods
                    WHERE nombre=?
                    """,
                    (metodo_pago,),
                )

                payment_method = self.cursor.fetchone()

                if not payment_method:
                    raise ValueError(
                        "Método de pago no válido"
                    )

                self.cursor.execute(
                    """
                    INSERT INTO payments (
                        factura_id,
                        metodo_id,
                        monto,
                        usuario_id
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        factura_id,
                        payment_method[0],
                        total,
                        usuario_id,
                    ),
                )

                # ==================================================
                # CAJA
                # ==================================================

                self.cursor.execute(
                    """
                    SELECT id
                    FROM cash_registers
                    WHERE estado='ABIERTA'
                    ORDER BY id DESC
                    LIMIT 1
                    """
                )

                cash_register = self.cursor.fetchone()

                if not cash_register:
                    raise ValueError(
                        "Debe abrir una caja antes de registrar "
                        "una venta pagada"
                    )

                self.cursor.execute(
                    """
                    INSERT INTO cash_movements (
                        caja_id,
                        tipo,
                        monto,
                        metodo_pago,
                        referencia,
                        usuario_id
                    )
                    VALUES (?, 'VENTA', ?, ?, ?, ?)
                    """,
                    (
                        cash_register[0],
                        total,
                        metodo_pago,
                        numero,
                        usuario_id,
                    ),
                )

            # ======================================================
            # AUDITORÍA
            # ======================================================

            audit(
                self.conn,
                "CREAR_FACTURA",
                "facturas",
                factura_id,
                numero,
                usuario_id,
            )

            # ======================================================
            # PDF
            # ======================================================

            pdf_path = self.generar_pdf(
                factura_id
            )

            self.conn.commit()

            messagebox.showinfo(
                "Éxito",
                f"Factura {numero} generada correctamente\n"
                "PDF guardado exitosamente",
            )

            self.nueva_factura()
            self.cargar_historial()
            self.cargar_productos()

        except Exception as exc:
            self.conn.rollback()

            if (
                pdf_path
                and os.path.exists(pdf_path)
            ):
                try:
                    os.remove(pdf_path)
                except OSError:
                    logging.exception(
                        "No se pudo limpiar el PDF "
                        "de una factura revertida"
                    )

            messagebox.showerror(
                "Error",
                f"Error al generar factura: {exc}",
            )


    def generar_pdf(self, factura_id):
        try:
            self.cursor.execute(
                """
                SELECT
                    f.numero,
                    f.fecha,
                    f.subtotal,
                    f.itbis,
                    f.total,
                    c.nombre,
                    c.cedula,
                    c.telefono,
                    c.direccion
                FROM facturas f
                JOIN clientes c
                    ON f.cliente_id = c.id
                WHERE f.id = ?
                """,
                (factura_id,),
            )

            factura_data = self.cursor.fetchone()

            if not factura_data:
                raise ValueError(
                    "Factura no encontrada"
                )

            self.cursor.execute(
                """
                SELECT
                    p.codigo,
                    p.nombre,
                    fi.cantidad,
                    fi.precio_unitario,
                    fi.subtotal
                FROM factura_items fi
                JOIN productos p
                    ON fi.producto_id = p.id
                WHERE fi.factura_id = ?
                """,
                (factura_id,),
            )

            items_data = self.cursor.fetchall()

            if not items_data:
                raise ValueError(
                    "La factura no tiene items"
                )

            self.cursor.execute(
                """
                SELECT
                    nombre,
                    rnc,
                    direccion,
                    telefono,
                    email,
                    website
                FROM empresa
                WHERE id = 1
                """
            )

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

            empresa_nombre = (
                empresa_nombre
                or "TU EMPRESA S.A."
            )

            empresa_rnc = (
                empresa_rnc
                or "000-00000-0"
            )

            empresa_direccion = (
                empresa_direccion
                or "Tu dirección aquí"
            )

            empresa_email = (
                empresa_email
                or "example@gmail.com"
            )

            empresa_telefono = (
                empresa_telefono
                or "(809) 000-0000"
            )

            facturas_dir = os.path.join(
                self.base_path,
                "facturas",
            )

            try:
                os.makedirs(
                    facturas_dir,
                    exist_ok=True,
                )
            except OSError as exc:
                raise RuntimeError(
                    "No se pudo crear la carpeta de facturas: "
                    f"{exc}"
                ) from exc

            # Limpiar el número para usarlo como
            # nombre de archivo.
            nombre_seguro = "".join(
                c
                if c.isalnum() or c in "-_"
                else "_"
                for c in str(factura_data[0])
            )

            filename = os.path.join(
                facturas_dir,
                f"{nombre_seguro}.pdf",
            )

            doc = SimpleDocTemplate(
                filename,
                pagesize=letter,
            )

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
                    name="InvoiceHeader",
                    fontSize=11,
                    leading=14,
                    spaceAfter=8,
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

            # ======================================================
            # TÍTULO
            # ======================================================

            elements.append(
                Paragraph(
                    "FACTURA",
                    styles["InvoiceTitle"],
                )
            )

            elements.append(
                Spacer(
                    1,
                    0.2 * inch,
                )
            )

            # ======================================================
            # EMPRESA
            # ======================================================

            empresa_text = (
                f"<b>{escape(str(empresa_nombre))}</b><br/>"
                f"RNC: {escape(str(empresa_rnc))}<br/>"
                f"Dirección: {escape(str(empresa_direccion))}<br/>"
                f"Teléfono: {escape(str(empresa_telefono))}"
            )

            if empresa_email:
                empresa_text += (
                    f"<br/>Email: "
                    f"{escape(str(empresa_email))}"
                )

            if empresa_website:
                empresa_text += (
                    f"<br/>Web: "
                    f"{escape(str(empresa_website))}"
                )

            elements.append(
                Paragraph(
                    empresa_text,
                    styles["Normal"],
                )
            )

            elements.append(
                Spacer(
                    1,
                    0.3 * inch,
                )
            )

            # ======================================================
            # INFORMACIÓN DE FACTURA
            # ======================================================

            info_data = [
                [
                    "Factura No.:",
                    factura_data[0],
                    "Fecha:",
                    factura_data[1],
                ],
                [
                    "Cliente:",
                    factura_data[5],
                    "Cédula:",
                    factura_data[6] or "N/A",
                ],
                [
                    "Teléfono:",
                    factura_data[7] or "N/A",
                    "Dirección:",
                    factura_data[8] or "N/A",
                ],
            ]

            info_table = Table(
                info_data,
                colWidths=[
                    1.2 * inch,
                    2.5 * inch,
                    1.2 * inch,
                    2 * inch,
                ],
            )

            info_table.setStyle(
                TableStyle(
                    [
                        (
                            "FONTNAME",
                            (0, 0),
                            (0, -1),
                            "Helvetica-Bold",
                        ),
                        (
                            "FONTNAME",
                            (2, 0),
                            (2, -1),
                            "Helvetica-Bold",
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            9,
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "MIDDLE",
                        ),
                    ]
                )
            )

            elements.append(info_table)

            elements.append(
                Spacer(
                    1,
                    0.3 * inch,
                )
            )

            # ======================================================
            # PRODUCTOS
            # ======================================================

            productos_data = [
                [
                    "Código",
                    "Producto",
                    "Cantidad",
                    "Precio Unit.",
                    "Subtotal",
                ]
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
                colWidths=[
                    1 * inch,
                    3 * inch,
                    1 * inch,
                    1.2 * inch,
                    1.2 * inch,
                ],
            )

            productos_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.grey,
                        ),
                        (
                            "TEXTCOLOR",
                            (0, 0),
                            (-1, 0),
                            colors.whitesmoke,
                        ),
                        (
                            "ALIGN",
                            (0, 0),
                            (-1, -1),
                            "CENTER",
                        ),
                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 0),
                            "Helvetica-Bold",
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, 0),
                            10,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, 0),
                            12,
                        ),
                        (
                            "BACKGROUND",
                            (0, 1),
                            (-1, -1),
                            colors.beige,
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            1,
                            colors.black,
                        ),
                        (
                            "FONTSIZE",
                            (0, 1),
                            (-1, -1),
                            9,
                        ),
                    ]
                )
            )

            elements.append(
                productos_table
            )

            elements.append(
                Spacer(
                    1,
                    0.3 * inch,
                )
            )

            # ======================================================
            # TOTALES
            # ======================================================

            totales_data = [
                [
                    "",
                    "",
                    "",
                    "Subtotal:",
                    f"RD$ {factura_data[2]:.2f}",
                ],
                [
                    "",
                    "",
                    "",
                    "ITBIS (18%):",
                    f"RD$ {factura_data[3]:.2f}",
                ],
                [
                    "",
                    "",
                    "",
                    "TOTAL:",
                    f"RD$ {factura_data[4]:.2f}",
                ],
            ]

            totales_table = Table(
                totales_data,
                colWidths=[
                    1 * inch,
                    3 * inch,
                    1 * inch,
                    1.2 * inch,
                    1.2 * inch,
                ],
            )

            totales_table.setStyle(
                TableStyle(
                    [
                        (
                            "ALIGN",
                            (3, 0),
                            (-1, -1),
                            "RIGHT",
                        ),
                        (
                            "FONTNAME",
                            (3, 0),
                            (3, -1),
                            "Helvetica-Bold",
                        ),
                        (
                            "FONTNAME",
                            (3, 2),
                            (-1, 2),
                            "Helvetica-Bold",
                        ),
                        (
                            "FONTSIZE",
                            (3, 2),
                            (-1, 2),
                            12,
                        ),
                        (
                            "LINEABOVE",
                            (3, 2),
                            (-1, 2),
                            2,
                            colors.black,
                        ),
                        (
                            "TEXTCOLOR",
                            (3, 2),
                            (-1, 2),
                            colors.green,
                        ),
                    ]
                )
            )

            elements.append(
                totales_table
            )

            elements.append(
                Spacer(
                    1,
                    0.2 * inch,
                )
            )

            # ======================================================
            # FOOTER
            # ======================================================

            elements.append(
                Paragraph(
                    "Gracias por su preferencia. "
                    "Documento generado automáticamente.",
                    styles["Footer"],
                )
            )

            doc.build(elements)

            return filename

        except Exception as exc:
            raise RuntimeError(
                f"Error al generar el PDF: {exc}"
            ) from exc


    def nueva_factura(self):
        # Limpiar tabla de items.
        self.items_table.clear()

        # Limpiar lista interna.
        self.items_factura = []

        # Resetear totales.
        self.subtotal_var.set(
            "RD$ 0.00"
        )

        self.itbis_var.set(
            "RD$ 0.00"
        )

        self.total_var.set(
            "RD$ 0.00"
        )

        # Nuevo número de factura.
        self.num_factura.set(
            self.generar_numero_factura()
        )

        # Nueva fecha.
        self.fecha_factura.set(
            datetime.now().strftime(
                "%d/%m/%Y"
            )
        )

        # Limpiar cliente.
        self.cliente_var.set("")

        self.metodo_pago_var.set(
            "EFECTIVO"
        )

        # Limpiar producto.
        self.producto_var.set("")
        self.precio_var.set("")
        self.cantidad_var.set("1")


    def cargar_historial(self):
        self.table_historial.clear()

        buscar = self.hist_buscar.get().strip()

        if buscar:
            self.cursor.execute(
                """
                SELECT
                    f.id,
                    f.numero,
                    f.fecha,
                    c.nombre,
                    f.subtotal,
                    f.itbis,
                    f.total,
                    f.estado
                FROM facturas f
                JOIN clientes c
                    ON f.cliente_id = c.id
                WHERE f.numero LIKE ?
                OR c.nombre LIKE ?
                ORDER BY f.id DESC
                """,
                (
                    f"%{buscar}%",
                    f"%{buscar}%",
                ),
            )

        else:
            self.cursor.execute(
                """
                SELECT
                    f.id,
                    f.numero,
                    f.fecha,
                    c.nombre,
                    f.subtotal,
                    f.itbis,
                    f.total,
                    f.estado
                FROM facturas f
                JOIN clientes c
                    ON f.cliente_id = c.id
                ORDER BY f.id DESC
                """
            )

        filas = self.cursor.fetchall()

        for row in filas:
            self.table_historial.add_row(
                (
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    f"RD$ {row[4]:.2f}",
                    f"RD$ {row[5]:.2f}",
                    f"RD$ {row[6]:.2f}",
                    row[7],
                )
            )

        self.table_historial.restripe()

        self._actualizar_badge(
            getattr(
                self,
                "invoices_count",
                None,
            ),
            f"{len(filas)} factura{'s' if len(filas) != 1 else ''}",
        )


    def ver_detalles_factura(self):
        selected = self.tree_historial.selection()

        if not selected:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione una factura",
            )
            return

        item = self.tree_historial.item(
            selected[0]
        )

        factura_id = item["values"][0]

        # Obtener datos antes de abrir la ventana.
        self.cursor.execute(
            """
            SELECT
                f.numero,
                f.fecha,
                f.subtotal,
                f.itbis,
                f.total,
                c.nombre,
                c.cedula,
                c.telefono
            FROM facturas f
            JOIN clientes c
                ON f.cliente_id = c.id
            WHERE f.id = ?
            """,
            (factura_id,),
        )

        factura_data = self.cursor.fetchone()

        if not factura_data:
            messagebox.showerror(
                "Detalles",
                "La factura ya no existe en la base.",
            )

            self.cargar_historial()
            return

        # ==========================================================
        # VENTANA DE DETALLES
        # ==========================================================

        detalle_win = ctk.CTkToplevel(
            self.root
        )

        theme.prepare_toplevel(
            detalle_win,
            "Detalles de Factura",
            (700, 500),
            self.base_path,
        )

        detalle_win.bind(
            "<Escape>",
            lambda event: detalle_win.destroy(),
        )

        # ==========================================================
        # INFORMACIÓN GENERAL
        # ==========================================================

        info_card = cards.Card(
            detalle_win,
            title=f"Factura {factura_data[0]}",
            padding=14,
        )

        info_card.pack(
            fill="x",
            padx=14,
            pady=(14, 8),
        )

        for etiqueta, valor in (
            ("Fecha", factura_data[1]),
            ("Cliente", factura_data[5]),
            ("Cédula", factura_data[6] or "N/A"),
            ("Teléfono", factura_data[7] or "N/A"),
        ):
            cards.label(
                info_card.body,
                f"{etiqueta}: {valor}",
                font_role="body",
                background="surface",
            ).pack(
                anchor="w"
            )

        # ==========================================================
        # TABLA DE ITEMS
        # ==========================================================

        items_card = cards.Card(
            detalle_win,
            title="Productos",
            padding=14,
        )

        items_card.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=8,
        )

        tabla = tables.DataTable(
            items_card.body,
            columns=(
                "Código",
                "Producto",
                "Cantidad",
                "Precio",
                "Subtotal",
            ),
            headings=(
                "Código",
                "Producto",
                "Cantidad",
                "Precio unit.",
                "Subtotal",
            ),
            widths=(
                90,
                260,
                80,
                110,
                110,
            ),
            anchors=(
                "w",
                "w",
                "e",
                "e",
                "e",
            ),
            height=8,
            hscroll=True,
        )

        tabla.pack(
            fill="both",
            expand=True,
        )

        # Cargar items.
        self.cursor.execute(
            """
            SELECT
                p.codigo,
                p.nombre,
                fi.cantidad,
                fi.precio_unitario,
                fi.subtotal
            FROM factura_items fi
            JOIN productos p
                ON fi.producto_id = p.id
            WHERE fi.factura_id = ?
            """,
            (factura_id,),
        )

        for row in self.cursor.fetchall():
            tabla.add_row(
                (
                    row[0],
                    row[1],
                    row[2],
                    f"RD$ {row[3]:.2f}",
                    f"RD$ {row[4]:.2f}",
                )
            )

        tabla.restripe()

        # ==========================================================
        # TOTALES
        # ==========================================================

        total_card = cards.Card(
            detalle_win,
            padding=14,
        )

        total_card.pack(
            fill="x",
            padx=14,
            pady=(8, 14),
        )

        cards.label(
            total_card.body,
            f"Subtotal: RD$ {factura_data[2]:.2f}",
            font_role="body",
            background="surface",
        ).pack(
            anchor="e"
        )

        cards.label(
            total_card.body,
            f"ITBIS: RD$ {factura_data[3]:.2f}",
            font_role="body",
            background="surface",
        ).pack(
            anchor="e"
        )

        total_label = ctk.CTkLabel(
            total_card.body,
            text=f"TOTAL: RD$ {factura_data[4]:.2f}",
            font=theme.font("metric"),
            text_color=theme.color("success"),
            anchor="e",
        )

        total_label.pack(
            anchor="e",
            pady=(4, 0),
        )


    def regenerar_pdf(self):
        selected = self.tree_historial.selection()

        if not selected:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione una factura",
            )
            return

        item = self.tree_historial.item(
            selected[0]
        )

        factura_id = item["values"][0]

        try:
            self.generar_pdf(
                factura_id
            )

            messagebox.showinfo(
                "Éxito",
                "PDF generado correctamente",
            )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Error al generar PDF: {exc}",
            )


    def _factura_seleccionada(self):
        selected = self.tree_historial.selection()

        if not selected:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione una factura",
            )
            return None

        return self.tree_historial.item(
            selected[0]
        )["values"][0]


    def registrar_abono(self):
        if not self.require_permission("create_invoices"):
            return

        factura_id = self._factura_seleccionada()

        if factura_id is None:
            return

        try:
            self.cursor.execute(
                """
                SELECT total, estado
                FROM facturas
                WHERE id=?
                """,
                (factura_id,),
            )

            invoice = self.cursor.fetchone()

            if (
                not invoice
                or invoice[1] == "ANULADA"
            ):
                messagebox.showwarning(
                    "Abono",
                    "La factura no admite abonos.",
                )
                return

            self.cursor.execute(
                """
                SELECT COALESCE(SUM(monto), 0)
                FROM payments
                WHERE factura_id=?
                """,
                (factura_id,),
            )

            paid = self.cursor.fetchone()[0]

            balance = round(
                invoice[0] - paid,
                2,
            )

            if balance <= 0:
                messagebox.showinfo(
                    "Abono",
                    "La factura ya está pagada.",
                )
                return

            amount = simpledialog.askfloat(
                "Registrar abono",
                (
                    f"Saldo pendiente: "
                    f"RD$ {balance:.2f}\n"
                    "Monto del abono:"
                ),
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

            method = (
                method or "EFECTIVO"
            ).strip().upper()

            self.cursor.execute(
                """
                SELECT id
                FROM payment_methods
                WHERE nombre=?
                """,
                (method,),
            )

            payment_method = self.cursor.fetchone()

            if not payment_method:
                messagebox.showerror(
                    "Abono",
                    "Método de pago no válido.",
                )
                return

            new_paid = round(
                paid + amount,
                2,
            )

            state = (
                "PAGADA"
                if new_paid >= invoice[0]
                else "PARCIAL"
            )

            self.cursor.execute(
                """
                INSERT INTO payments (
                    factura_id,
                    metodo_id,
                    monto,
                    usuario_id
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    factura_id,
                    payment_method[0],
                    amount,
                    self.current_user.get("id"),
                ),
            )

            self.cursor.execute(
                """
                UPDATE facturas
                SET estado=?
                WHERE id=?
                """,
                (
                    state,
                    factura_id,
                ),
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
                (
                    "Abono registrado. "
                    f"Saldo restante: RD$ "
                    f"{max(0, invoice[0] - new_paid):.2f}"
                ),
            )

        except (
            sqlite3.Error,
            ValueError,
        ) as exc:
            self.conn.rollback()

            messagebox.showerror(
                "Error de abono",
                str(exc),
            )


    def anular_factura(self):
        if not self.require_permission("create_invoices"):
            return

        factura_id = self._factura_seleccionada()

        if factura_id is None:
            return

        if not messagebox.askyesno(
            "Anular factura",
            "La factura quedará bloqueada y "
            "el stock será reintegrado. ¿Continuar?",
        ):
            return

        try:
            self.cursor.execute(
                """
                SELECT numero, estado
                FROM facturas
                WHERE id=?
                """,
                (factura_id,),
            )

            invoice = self.cursor.fetchone()

            if (
                not invoice
                or invoice[1] == "ANULADA"
            ):
                messagebox.showwarning(
                    "Anular factura",
                    "La factura ya está anulada o no existe.",
                )
                return

            self.cursor.execute(
                """
                SELECT producto_id, cantidad
                FROM factura_items
                WHERE factura_id=?
                """,
                (factura_id,),
            )

            items = self.cursor.fetchall()

            for product_id, quantity in items:

                self.cursor.execute(
                    """
                    UPDATE productos
                    SET stock=stock+?
                    WHERE id=?
                    """,
                    (
                        quantity,
                        product_id,
                    ),
                )

                self.cursor.execute(
                    """
                    INSERT INTO inventory_movements (
                        producto_id,
                        tipo,
                        cantidad,
                        motivo,
                        referencia,
                        usuario_id
                    )
                    VALUES (
                        ?,
                        'DEVOLUCION',
                        ?,
                        ?,
                        ?,
                        ?
                    )
                    """,
                    (
                        product_id,
                        quantity,
                        "Anulación de factura",
                        invoice[0],
                        self.current_user.get("id"),
                    ),
                )

            self.cursor.execute(
                """
                UPDATE facturas
                SET estado='ANULADA'
                WHERE id=?
                """,
                (factura_id,),
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
                "Anular factura",
                "Factura anulada y stock reintegrado correctamente.",
            )

        except sqlite3.Error as exc:
            self.conn.rollback()

            messagebox.showerror(
                "Error de anulación",
                str(exc),
            )


    def cargar_datos(self):
        """Carga los datos en los combobox."""

        # ==========================================================
        # PRODUCTOS
        # ==========================================================

        self.cursor.execute(
            """
            SELECT codigo, nombre
            FROM productos
            WHERE activo=1
            ORDER BY nombre
            """
        )

        productos = [
            f"{row[0]} - {row[1]}"
            for row in self.cursor.fetchall()
        ]

        self.combo_producto.configure(
            values=productos
        )

        # ==========================================================
        # CLIENTES
        # ==========================================================

        self.cursor.execute(
            """
            SELECT nombre, cedula
            FROM clientes
            WHERE activo=1
            ORDER BY nombre
            """
        )

        clientes = [
            (
                f"{row[0]} - {row[1]}"
                if row[1]
                else row[0]
            )
            for row in self.cursor.fetchall()
        ]

        self.combo_cliente.configure(
            values=clientes
        )

        # ==========================================================
        # TABLAS
        # ==========================================================

        self.cargar_productos()
        self.cargar_clientes()
        self.cargar_historial()
        self.cargar_empresa()