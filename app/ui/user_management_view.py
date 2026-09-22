from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from app.auth.authorization import PERMISSIONS, ROLE_PERMISSIONS
from app.core.user_management import (
    activate_user,
    create_user,
    deactivate_user,
    list_users,
)
from app.ui import theme
from app.ui.components import cards, inputs, tables
from app.ui.components.buttons import AppButton


class UserManagementView:
    """Ventana de administración de usuarios de KLP SYSTEM."""

    def __init__(self, parent, connection, actor_id):
        self.connection = connection
        self.actor_id = actor_id

        self.window = ctk.CTkToplevel(parent)
        self.window.title("Usuarios y permisos")
        self.window.geometry("900x680")
        self.window.minsize(800, 600)
        self.window.transient(parent)
        self.window.grab_set()

        self.selected_user_id = None
        self.selected_user_role = None
        self.selected_user_active = None

        self._build()
        self.refresh()

    # ==========================================================
    # CONSTRUCCIÓN
    # ==========================================================

    def _build(self):
        """Construye la interfaz."""

        self.main_frame = ctk.CTkFrame(
            self.window,
            fg_color=theme.color("window"),
            corner_radius=0,
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
        )

        # ======================================================
        # ENCABEZADO
        # ======================================================

        header = cards.Card(
            self.main_frame,
            title="Usuarios y permisos",
            subtitle=(
                "Administra los usuarios, roles y acceso "
                "al sistema."
            ),
        )

        header.pack(
            fill="x",
            padx=20,
            pady=(20, 10),
        )

        # ======================================================
        # CREAR USUARIO
        # ======================================================

        self._build_create_user_card()

        # ======================================================
        # TABLA
        # ======================================================

        self._build_users_table()

        # ======================================================
        # DETALLES / PERMISOS
        # ======================================================

        self._build_permissions_card()

    # ==========================================================
    # CREAR USUARIO
    # ==========================================================

    def _build_create_user_card(self):
        form_card = cards.Card(
            self.main_frame,
            title="Crear usuario",
        )

        form_card.pack(
            fill="x",
            padx=20,
            pady=(0, 10),
        )

        content = form_card.body

        content.grid_columnconfigure(
            0,
            weight=1,
        )

        content.grid_columnconfigure(
            1,
            weight=1,
        )

        content.grid_columnconfigure(
            2,
            weight=1,
        )

        self.username = ctk.StringVar()
        self.password = ctk.StringVar()
        self.role = ctk.StringVar(
            value="Vendedor",
        )

        # ------------------------------------------------------
        # Usuario
        # ------------------------------------------------------

        _, username_entry = inputs.labeled_entry(
            content,
            "Usuario",
            placeholder="Nombre de usuario",
            textvariable=self.username,
        )
        username_entry.grid(
            row=0,
            column=0,
            padx=(0, 8),
            pady=5,
            sticky="ew",
        )

        # ------------------------------------------------------
        # Contraseña
        # ------------------------------------------------------

        _, password_entry = inputs.labeled_entry(
            content,
            "Contraseña",
            placeholder="Mínimo 8 caracteres",
            textvariable=self.password,
            show="*",
        )
        password_entry.grid(
            row=0,
            column=1,
            padx=8,
            pady=5,
            sticky="ew",
        )

        # ------------------------------------------------------
        # Rol
        # ------------------------------------------------------

        _, role_combobox = inputs.labeled_combobox(
            content,
            "Rol",
            variable=self.role,
            values=(
                "Administrador",
                "Vendedor",
                "Cajero",
                "Contador",
            ),
        )
        role_combobox.grid(
            row=0,
            column=2,
            padx=8,
            pady=5,
            sticky="ew",
        )

        # ------------------------------------------------------
        # Botón
        # ------------------------------------------------------

        self.create_button = AppButton(
            content,
            text="Crear usuario",
            command=self.create,
            variant="success",
            size="medium",
        )

        self.create_button.grid(
            row=0,
            column=3,
            padx=(8, 0),
            pady=5,
        )

    # ==========================================================
    # TABLA DE USUARIOS
    # ==========================================================

    def _build_users_table(self):
        table_card = cards.Card(
            self.main_frame,
            title="Usuarios registrados",
            subtitle=(
                "Selecciona un usuario para consultar "
                "su rol y permisos."
            ),
        )

        table_card.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 10),
        )

        self.tree = tables.DataTable(
            table_card.body,
            columns=(
                "ID",
                "Usuario",
                "Rol",
                "Estado",
                "Último acceso",
            ),
            widths=(
                55,
                180,
                140,
                90,
                180,
            ),
            anchors=(
                "center",
                "w",
                "w",
                "center",
                "center",
            ),
            height=8,
            selectmode="browse",
            state_tags={
                "Activo": "ok",
                "Inactivo": "danger",
            },
        )

        self.tree.pack(
            fill="both",
            expand=True,
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self._on_user_selected,
        )

    # ==========================================================
    # PERMISOS
    # ==========================================================

    def _build_permissions_card(self):
        permissions_card = cards.Card(
            self.main_frame,
            title="Permisos",
            subtitle="Permisos correspondientes al rol seleccionado.",
        )

        permissions_card.pack(
            fill="x",
            padx=20,
            pady=(0, 10),
        )

        content = permissions_card.body

        content.grid_columnconfigure(
            0,
            weight=1,
        )

        content.grid_columnconfigure(
            1,
            weight=1,
        )

        # ------------------------------------------------------
        # Información del usuario
        # ------------------------------------------------------

        self.selected_user_label = ctk.CTkLabel(
            content,
            text="Ningún usuario seleccionado",
            font=theme.font("body_bold"),
            text_color=theme.color("text"),
            anchor="w",
        )

        self.selected_user_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 8),
        )

        # ------------------------------------------------------
        # Contenedor de permisos
        # ------------------------------------------------------

        self.permissions_frame = ctk.CTkFrame(
            content,
            fg_color="transparent",
        )

        self.permissions_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
        )

        self.permissions_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        self.permissions_frame.grid_columnconfigure(
            1,
            weight=1,
        )

        # ------------------------------------------------------
        # Acciones
        # ------------------------------------------------------

        actions = ctk.CTkFrame(
            content,
            fg_color="transparent",
        )

        actions.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(10, 0),
        )

        self.activate_button = AppButton(
            actions,
            text="Activar usuario",
            command=self.activate,
            variant="success",
            size="medium",
        )

        self.activate_button.pack(
            side="left",
            padx=(0, 8),
        )

        self.deactivate_button = AppButton(
            actions,
            text="Desactivar usuario",
            command=self.deactivate,
            variant="danger",
            size="medium",
        )

        self.deactivate_button.pack(
            side="left",
        )

        self._set_action_state(False)

    # ==========================================================
    # REFRESH
    # ==========================================================

    def refresh(self):
        """Actualiza la tabla de usuarios."""

        rows = []

        for row in list_users(self.connection):
            user_id, username, role, active, last_access = row

            rows.append(
                (
                    user_id,
                    username,
                    role,
                    "Activo" if active else "Inactivo",
                    last_access or "",
                )
            )

        self.tree.set_rows(rows)

        self._clear_selection()

    # ==========================================================
    # SELECCIÓN
    # ==========================================================

    def _on_user_selected(self, _event=None):
        selected = self.tree.selected_values()

        if not selected:
            self._clear_selection()
            return

        try:
            user_id = int(selected[0])
        except (TypeError, ValueError):
            self._clear_selection()
            return

        username = selected[1]
        role = selected[2]
        state = selected[3]

        self.selected_user_id = user_id
        self.selected_user_role = role
        self.selected_user_active = state == "Activo"

        self.selected_user_label.configure(
            text=(
                f"Usuario: {username}    •    "
                f"Rol: {role}    •    "
                f"Estado: {state}"
            )
        )

        self._render_permissions(role)

        self._set_action_state(True)

    def _clear_selection(self):
        self.selected_user_id = None
        self.selected_user_role = None
        self.selected_user_active = None

        self.selected_user_label.configure(
            text="Ningún usuario seleccionado",
        )

        self._clear_permissions()
        self._set_action_state(False)

    # ==========================================================
    # PERMISOS
    # ==========================================================

    def _render_permissions(self, role):
        self._clear_permissions()

        permissions = ROLE_PERMISSIONS.get(
            role,
            set(),
        )

        permission_items = list(
            PERMISSIONS.items()
        )

        for index, (code, description) in enumerate(
            permission_items
        ):
            row = index % 4
            column = index // 4

            allowed = code in permissions

            text = (
                f"✓ {description}"
                if allowed
                else f"✕ {description}"
            )

            label = ctk.CTkLabel(
                self.permissions_frame,
                text=text,
                anchor="w",
                justify="left",
                font=theme.font("small"),
                text_color=(
                    theme.color("success")
                    if allowed
                    else theme.color("muted")
                ),
            )

            label.grid(
                row=row,
                column=column,
                sticky="w",
                padx=(0, 20),
                pady=2,
            )

    def _clear_permissions(self):
        for widget in self.permissions_frame.winfo_children():
            widget.destroy()

    # ==========================================================
    # ESTADO DE BOTONES
    # ==========================================================

    def _set_action_state(self, enabled):
        if not enabled:
            self.activate_button.configure(
                state="disabled",
            )

            self.deactivate_button.configure(
                state="disabled",
            )

            return

        if self.selected_user_active:
            self.activate_button.configure(
                state="disabled",
            )

            self.deactivate_button.configure(
                state="normal",
            )

        else:
            self.activate_button.configure(
                state="normal",
            )

            self.deactivate_button.configure(
                state="disabled",
            )

    # ==========================================================
    # CREAR USUARIO
    # ==========================================================

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

    # ==========================================================
    # ACTIVAR
    # ==========================================================

    def activate(self):
        """Activa el usuario seleccionado."""

        if self.selected_user_id is None:
            return

        confirmed = messagebox.askyesno(
            "Usuarios",
            "¿Activar el usuario seleccionado?",
            parent=self.window,
        )

        if not confirmed:
            return

        try:
            self.activate_button.set_loading(
                True,
                "Activando...",
            )

            self.window.update_idletasks()

            activate_user(
                self.connection,
                self.selected_user_id,
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
            self.activate_button.set_loading(False)

    # ==========================================================
    # DESACTIVAR
    # ==========================================================

    def deactivate(self):
        """Desactiva el usuario seleccionado."""

        if self.selected_user_id is None:
            return

        if self.selected_user_id == self.actor_id:
            messagebox.showwarning(
                "Usuarios",
                "No puedes desactivar tu propio usuario.",
                parent=self.window,
            )
            return

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
                self.selected_user_id,
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