import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import customtkinter as ctk

from app.core.user_management import (
    create_user,
    deactivate_user,
    list_users,
)

from app.ui.components.buttons import AppButton
from app.ui.styles import Colors, Fonts


class UserManagementView:
    """Ventana de administración de usuarios de KLP SYSTEM."""

    def __init__(self, parent, connection, actor_id):
        self.connection = connection
        self.actor_id = actor_id

        self.window = ctk.CTkToplevel(parent)
        self.window.title("Usuarios y permisos")
        self.window.geometry("760x500")
        self.window.minsize(700, 450)

        self.window.transient(parent)
        self.window.grab_set()

        self._build()
        self.refresh()

    # ========================================================
    # CONSTRUCCIÓN
    # ========================================================

    def _build(self):
        """Construye la interfaz."""

        # ----------------------------------------------------
        # CONTENEDOR PRINCIPAL
        # ----------------------------------------------------

        self.main_frame = ctk.CTkFrame(
            self.window,
            fg_color=Colors.BACKGROUND,
            corner_radius=0,
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=0,
            pady=0,
        )

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        title_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )

        title_frame.pack(
            fill="x",
            padx=20,
            pady=(20, 5),
        )

        ctk.CTkLabel(
            title_frame,
            text="Usuarios y permisos",
            font=Fonts.TITLE,
            text_color=Colors.TEXT,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            title_frame,
            text="Administra los usuarios y sus roles dentro del sistema.",
            font=Fonts.BODY,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
        ).pack(
            fill="x",
            pady=(2, 0),
        )

        # ----------------------------------------------------
        # FORMULARIO
        # ----------------------------------------------------

        form = ctk.CTkFrame(
            self.main_frame,
            fg_color=Colors.CARD,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=10,
        )

        form.pack(
            fill="x",
            padx=20,
            pady=15,
        )

        ctk.CTkLabel(
            form,
            text="Crear usuario",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT,
        ).grid(
            row=0,
            column=0,
            columnspan=6,
            sticky="w",
            padx=15,
            pady=(12, 10),
        )

        # Variables
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.role = tk.StringVar(value="Vendedor")

        # ----------------------------------------------------
        # USUARIO
        # ----------------------------------------------------

        ctk.CTkLabel(
            form,
            text="Usuario",
            font=Fonts.SMALL_BOLD,
            text_color=Colors.TEXT_SECONDARY,
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(15, 5),
            pady=(0, 5),
        )

        self.username_entry = ctk.CTkEntry(
            form,
            textvariable=self.username,
            width=135,
            height=36,
            placeholder_text="Nombre de usuario",
            fg_color=Colors.INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT,
        )

        self.username_entry.grid(
            row=2,
            column=0,
            padx=(15, 5),
            pady=(0, 15),
        )

        # ----------------------------------------------------
        # CONTRASEÑA
        # ----------------------------------------------------

        ctk.CTkLabel(
            form,
            text="Contraseña",
            font=Fonts.SMALL_BOLD,
            text_color=Colors.TEXT_SECONDARY,
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=5,
            pady=(0, 5),
        )

        self.password_entry = ctk.CTkEntry(
            form,
            textvariable=self.password,
            show="*",
            width=135,
            height=36,
            placeholder_text="Contraseña",
            fg_color=Colors.INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT,
        )

        self.password_entry.grid(
            row=2,
            column=1,
            padx=5,
            pady=(0, 15),
        )

        # ----------------------------------------------------
        # ROL
        # ----------------------------------------------------

        ctk.CTkLabel(
            form,
            text="Rol",
            font=Fonts.SMALL_BOLD,
            text_color=Colors.TEXT_SECONDARY,
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=5,
            pady=(0, 5),
        )

        self.role_combo = ctk.CTkComboBox(
            form,
            variable=self.role,
            values=(
                "Administrador",
                "Vendedor",
                "Cajero",
                "Contador",
            ),
            state="readonly",
            width=135,
            height=36,
            fg_color=Colors.INPUT,
            border_color=Colors.BORDER,
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.TEXT,
            dropdown_fg_color=Colors.SURFACE,
            dropdown_hover_color=Colors.SURFACE_HOVER,
            dropdown_text_color=Colors.TEXT,
        )

        self.role_combo.grid(
            row=2,
            column=2,
            padx=5,
            pady=(0, 15),
        )

        # ----------------------------------------------------
        # BOTÓN CREAR
        # ----------------------------------------------------

        self.create_button = AppButton(
            form,
            text="Crear usuario",
            command=self.create,
            variant="success",
            size="medium",
        )

        self.create_button.grid(
            row=2,
            column=3,
            padx=(10, 15),
            pady=(0, 15),
        )

        # ----------------------------------------------------
        # CONFIGURACIÓN DEL GRID
        # ----------------------------------------------------

        form.grid_columnconfigure(4, weight=1)

        # ----------------------------------------------------
        # TABLA
        # ----------------------------------------------------

        table_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=Colors.CARD,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=10,
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 10),
        )

        ctk.CTkLabel(
            table_frame,
            text="Usuarios registrados",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT,
            anchor="w",
        ).pack(
            fill="x",
            padx=15,
            pady=(12, 8),
        )

        # ----------------------------------------------------
        # TREEVIEW
        # ----------------------------------------------------

        tree_container = ctk.CTkFrame(
            table_frame,
            fg_color="transparent",
        )

        tree_container.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 10),
        )

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "KLP.Treeview",
            background=Colors.INPUT,
            foreground=Colors.TEXT,
            fieldbackground=Colors.INPUT,
            borderwidth=0,
            rowheight=34,
            font=(Fonts.FAMILY, 10),
        )

        style.configure(
            "KLP.Treeview.Heading",
            background=Colors.SURFACE,
            foreground=Colors.TEXT,
            borderwidth=0,
            relief="flat",
            font=(Fonts.FAMILY, 10, "bold"),
        )

        style.map(
            "KLP.Treeview",
            background=[
                ("selected", Colors.PRIMARY)
            ],
            foreground=[
                ("selected", Colors.TEXT)
            ],
        )

        self.tree = ttk.Treeview(
            tree_container,
            columns=(
                "ID",
                "Usuario",
                "Rol",
                "Activo",
                "Último acceso",
            ),
            show="headings",
            style="KLP.Treeview",
            selectmode="browse",
        )

        # Encabezados
        columns = (
            "ID",
            "Usuario",
            "Rol",
            "Activo",
            "Último acceso",
        )

        for column in columns:
            self.tree.heading(
                column,
                text=column,
            )

        # Tamaños
        self.tree.column(
            "ID",
            width=55,
            minwidth=55,
            anchor="center",
        )

        self.tree.column(
            "Usuario",
            width=160,
            minwidth=120,
            anchor="w",
        )

        self.tree.column(
            "Rol",
            width=130,
            minwidth=100,
            anchor="w",
        )

        self.tree.column(
            "Activo",
            width=80,
            minwidth=70,
            anchor="center",
        )

        self.tree.column(
            "Último acceso",
            width=160,
            minwidth=130,
            anchor="center",
        )

        self.tree.pack(
            fill="both",
            expand=True,
            side="left",
        )

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(
            tree_container,
            command=self.tree.yview,
        )

        scrollbar.pack(
            side="right",
            fill="y",
            padx=(5, 0),
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        # ----------------------------------------------------
        # BOTÓN DESACTIVAR
        # ----------------------------------------------------

        bottom_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )

        bottom_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 15),
        )

        self.deactivate_button = AppButton(
            bottom_frame,
            text="Desactivar seleccionado",
            command=self.deactivate,
            variant="danger",
            size="medium",
        )

        self.deactivate_button.pack(
            side="right",
        )

    # ========================================================
    # ACTUALIZAR TABLA
    # ========================================================

    def refresh(self):
        """Actualiza la lista de usuarios."""

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in list_users(self.connection):
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row[0],
                    row[1],
                    row[2],
                    "Sí" if row[3] else "No",
                    row[4] or "",
                ),
            )

    # ========================================================
    # CREAR USUARIO
    # ========================================================

    def create(self):
        """Crea un nuevo usuario."""

        username = self.username.get().strip()
        password = self.password.get()
        role = self.role.get()

        try:
            self.create_button.set_loading(
                True,
                "Creando...",
            )

            self.window.update_idletasks()

            create_user(
                self.connection,
                username,
                password,
                role,
                self.actor_id,
            )

            self.username.set("")
            self.password.set("")

            self.refresh()

            messagebox.showinfo(
                "Usuarios",
                "Usuario creado correctamente.",
                parent=self.window,
            )

        except Exception as exc:
            messagebox.showerror(
                "Usuarios",
                str(exc),
                parent=self.window,
            )

        finally:
            self.create_button.set_loading(False)

    # ========================================================
    # DESACTIVAR USUARIO
    # ========================================================

    def deactivate(self):
        """Desactiva el usuario seleccionado."""

        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Usuarios",
                "Selecciona un usuario primero.",
                parent=self.window,
            )
            return

        user_id = self.tree.item(
            selected[0]
        )["values"][0]

        confirmed = messagebox.askyesno(
            "Usuarios",
            "¿Desactivar el usuario seleccionado?",
            parent=self.window,
        )

        if not confirmed:
            return

        try:
            self.deactivate_button.set_loading(
                True,
                "Desactivando...",
            )

            self.window.update_idletasks()

            deactivate_user(
                self.connection,
                int(user_id),
                self.actor_id,
            )

            self.refresh()

        except Exception as exc:
            messagebox.showerror(
                "Usuarios",
                str(exc),
                parent=self.window,
            )

        finally:
            self.deactivate_button.set_loading(False)