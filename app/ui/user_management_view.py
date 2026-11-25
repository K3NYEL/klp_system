from __future__ import annotations

from app.ui import tk_widgets as tkui
from tkinter import messagebox

from app.core.user_management import (
    activate_role,
    activate_user,
    change_user_password,
    change_user_role,
    create_role,
    create_user,
    deactivate_role,
    deactivate_user,
    get_role_permissions,
    list_permissions,
    list_roles,
    list_users,
    rename_role,
    set_role_permissions,
)
from app.ui import theme
from app.ui.components import cards, inputs, tables
from app.ui.components.buttons import AppButton


class UserManagementView:
    """Módulo de administración de usuarios, roles y permisos."""

    def __init__(self, parent, connection, actor_id):
        self.connection = connection
        self.actor_id = actor_id

        self.window = tkui.Toplevel(parent)
        self.window.title("Usuarios y permisos")
        self.window.geometry("1000x720")
        self.window.minsize(900, 650)
        self.window.transient(parent)
        self.window.grab_set()

        self.selected_user_id = None
        self.selected_user_role = None
        self.selected_user_active = None

        self.selected_role_id = None
        self.selected_role_name = None
        self.selected_role_active = None

        self.permission_vars: dict[str, tkui.BooleanVar] = {}

        self._build()
        self.refresh()

    # ==========================================================
    # CONSTRUCCIÓN PRINCIPAL
    # ==========================================================

    def _build(self):
        self.main_frame = tkui.Frame(
            self.window,
            fg_color=theme.color("window"),
            corner_radius=0,
        )
        self.main_frame.pack(
            fill="both",
            expand=True,
        )

        # ------------------------------------------------------
        # Encabezado
        # ------------------------------------------------------

        header = tkui.Frame(
            self.main_frame,
            fg_color="transparent",
        )
        header.pack(
            fill="x",
            padx=20,
            pady=(20, 10),
        )

        title = tkui.Label(
            header,
            text="Usuarios y permisos",
            font=theme.font("title"),
            text_color=theme.color("text"),
            anchor="w",
        )
        title.pack(fill="x")

        subtitle = tkui.Label(
            header,
            text="Administra usuarios, roles y permisos de acceso.",
            font=theme.font("small"),
            text_color=theme.color("muted"),
            anchor="w",
        )
        subtitle.pack(
            fill="x",
            pady=(2, 0),
        )

        # ------------------------------------------------------
        # Pestañas
        # ------------------------------------------------------

        self.tabs = tkui.Tabview(
            self.main_frame,
            corner_radius=10,
        )
        self.tabs.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20),
        )

        self.users_tab = self.tabs.add("Usuarios")
        self.roles_tab = self.tabs.add("Roles y permisos")

        self._build_users_tab()
        self._build_roles_tab()

    # ==========================================================
    # TAB USUARIOS
    # ==========================================================

    def _build_users_tab(self):
        self._build_create_user_card()
        self._build_users_table()
        self._build_user_actions()

    # ==========================================================
    # CREAR USUARIO
    # ==========================================================

    def _build_create_user_card(self):
        form_card = cards.Card(
            self.users_tab,
            title="Crear usuario",
            subtitle="Registra un nuevo usuario y asigna su rol.",
        )
        form_card.pack(
            fill="x",
            padx=10,
            pady=(10, 8),
        )

        content = form_card.body

        for column in range(3):
            content.grid_columnconfigure(
                column,
                weight=1,
            )

        content.grid_columnconfigure(
            3,
            weight=0,
        )

        self.username = tkui.StringVar()
        self.password = tkui.StringVar()
        self.role = tkui.StringVar()

        # ------------------------------------------------------
        # Usuario
        # ------------------------------------------------------

        username_frame = tkui.Frame(
            content,
            fg_color="transparent",
        )
        username_frame.grid(
            row=0,
            column=0,
            padx=(0, 8),
            pady=5,
            sticky="ew",
        )
        username_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        tkui.Label(
            username_frame,
            text="Usuario",
            font=theme.font("body_bold"),
            text_color=theme.color("text"),
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4),
        )

        self.username_entry = inputs.make_entry(
            username_frame,
            textvariable=self.username,
            placeholder_text="Nombre de usuario",
            expand=True,
        )
        self.username_entry.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        # ------------------------------------------------------
        # Contraseña
        # ------------------------------------------------------

        password_frame = tkui.Frame(
            content,
            fg_color="transparent",
        )
        password_frame.grid(
            row=0,
            column=1,
            padx=8,
            pady=5,
            sticky="ew",
        )
        password_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        tkui.Label(
            password_frame,
            text="Contraseña",
            font=theme.font("body_bold"),
            text_color=theme.color("text"),
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4),
        )

        self.password_entry = inputs.make_entry(
            password_frame,
            textvariable=self.password,
            placeholder_text="Mínimo 8 caracteres",
            show="*",
            expand=True,
        )
        self.password_entry.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        # ------------------------------------------------------
        # Rol
        # ------------------------------------------------------

        role_frame = tkui.Frame(
            content,
            fg_color="transparent",
        )
        role_frame.grid(
            row=0,
            column=2,
            padx=8,
            pady=5,
            sticky="ew",
        )
        role_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        tkui.Label(
            role_frame,
            text="Rol",
            font=theme.font("body_bold"),
            text_color=theme.color("text"),
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4),
        )

        self.role_combobox = inputs.make_combobox(
            role_frame,
            values=(),
            textvariable=self.role,
            state="readonly",
        )
        self.role_combobox.grid(
            row=1,
            column=0,
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
            pady=(25, 5),
        )

    # ==========================================================
    # TABLA DE USUARIOS
    # ==========================================================

    def _build_users_table(self):
        table_card = cards.Card(
            self.users_tab,
            title="Usuarios registrados",
            subtitle="Selecciona un usuario para administrar su cuenta.",
        )
        table_card.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 8),
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
                200,
                160,
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
            height=7,
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
    # ACCIONES DE USUARIO
    # ==========================================================

    def _build_user_actions(self):
        actions_card = cards.Card(
            self.users_tab,
            title="Administrar usuario",
            subtitle="Modifica la cuenta del usuario seleccionado.",
        )
        actions_card.pack(
            fill="x",
            padx=10,
            pady=(0, 10),
        )

        actions = tkui.Frame(
            actions_card.body,
            fg_color="transparent",
        )
        actions.pack(
            fill="x",
        )

        self.change_role_button = AppButton(
            actions,
            text="Cambiar rol",
            command=self.change_role,
            variant="primary",
            size="medium",
        )
        self.change_role_button.pack(
            side="left",
            padx=(0, 8),
        )

        self.change_password_button = AppButton(
            actions,
            text="Cambiar contraseña",
            command=self.change_password,
            variant="secondary",
            size="medium",
        )
        self.change_password_button.pack(
            side="left",
            padx=(0, 8),
        )

        self.activate_button = AppButton(
            actions,
            text="Activar",
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
            text="Desactivar",
            command=self.deactivate,
            variant="danger",
            size="medium",
        )
        self.deactivate_button.pack(
            side="left",
        )

        self.selected_user_label = tkui.Label(
            actions_card.body,
            text="Ningún usuario seleccionado",
            font=theme.font("small"),
            text_color=theme.color("muted"),
            anchor="w",
        )
        self.selected_user_label.pack(
            fill="x",
            pady=(8, 0),
        )

        self._set_user_action_state(False)

    # ==========================================================
    # TAB ROLES
    # ==========================================================

    def _build_roles_tab(self):
        container = tkui.Frame(
            self.roles_tab,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        container.grid_columnconfigure(
            0,
            weight=0,
            minsize=320,
        )
        container.grid_columnconfigure(
            1,
            weight=1,
        )
        container.grid_rowconfigure(
            0,
            weight=1,
        )

        self._build_roles_list(container)
        self._build_role_permissions(container)

    # ==========================================================
    # LISTA DE ROLES
    # ==========================================================

    def _build_roles_list(self, parent):
        role_card = cards.Card(
            parent,
            title="Roles",
            subtitle="Administra los roles disponibles.",
        )
        role_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )

        self.roles_tree = tables.DataTable(
            role_card.body,
            columns=(
                "ID",
                "Rol",
                "Estado",
            ),
            widths=(
                50,
                150,
                90,
            ),
            anchors=(
                "center",
                "w",
                "center",
            ),
            height=12,
            selectmode="browse",
            state_tags={
                "Activo": "ok",
                "Inactivo": "danger",
            },
        )

        self.roles_tree.pack(
            fill="both",
            expand=True,
        )

        self.roles_tree.bind_tree(
            "<<TreeviewSelect>>",
            self._on_role_selected,
        )

        actions = tkui.Frame(
            role_card.body,
            fg_color="transparent",
        )
        actions.pack(
            fill="x",
            pady=(10, 0),
        )

        self.create_role_button = AppButton(
            actions,
            text="Crear rol",
            command=self.create_role,
            variant="success",
            size="small",
        )
        self.create_role_button.pack(
            side="left",
            padx=(0, 5),
        )

        self.rename_role_button = AppButton(
            actions,
            text="Editar",
            command=self.rename_role,
            variant="secondary",
            size="small",
        )
        self.rename_role_button.pack(
            side="left",
            padx=(0, 5),
        )

        self.activate_role_button = AppButton(
            actions,
            text="Activar",
            command=self.activate_selected_role,
            variant="success",
            size="small",
        )
        self.activate_role_button.pack(
            side="left",
            padx=(0, 5),
        )

        self.deactivate_role_button = AppButton(
            actions,
            text="Desactivar",
            command=self.deactivate_selected_role,
            variant="danger",
            size="small",
        )
        self.deactivate_role_button.pack(
            side="left",
        )

        self._set_role_action_state(False)

    # ==========================================================
    # PERMISOS DE ROL
    # ==========================================================

    def _build_role_permissions(self, parent):
        permissions_card = cards.Card(
            parent,
            title="Permisos del rol",
            subtitle="Selecciona los permisos que tendrá el rol.",
        )
        permissions_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
        )

        content = permissions_card.body

        self.selected_role_label = tkui.Label(
            content,
            text="Ningún rol seleccionado",
            font=theme.font("body_bold"),
            text_color=theme.color("text"),
            anchor="w",
        )
        self.selected_role_label.pack(
            fill="x",
            pady=(0, 10),
        )

        self.permissions_scroll = tkui.ScrollableFrame(
            content,
            fg_color="transparent",
        )
        self.permissions_scroll.pack(
            fill="both",
            expand=True,
        )

        self.save_permissions_button = AppButton(
            content,
            text="Guardar permisos",
            command=self.save_permissions,
            variant="success",
            size="medium",
        )
        self.save_permissions_button.pack(
            fill="x",
            pady=(10, 0),
        )

        self._set_permissions_state(False)

    # ==========================================================
    # REFRESH GENERAL
    # ==========================================================

    def refresh(self):
        self._refresh_users()
        self._refresh_roles()
        self._refresh_create_role_options()

    def _refresh_users(self):
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
        self._clear_user_selection()

    def _refresh_roles(self):
        rows = []

        for role_id, name, active, active_users in list_roles(
            self.connection,
            include_inactive=True,
        ):
            rows.append(
                (
                    role_id,
                    name,
                    "Activo" if active else "Inactivo",
                )
            )

        self.roles_tree.set_rows(rows)
        self._clear_role_selection()

    def _refresh_create_role_options(self):
        roles = list_roles(
            self.connection,
            include_inactive=False,
        )

        names = tuple(
            role[1]
            for role in roles
        )

        self.role_combobox.configure(
            values=names,
        )

        if names:
            if self.role.get() not in names:
                self.role.set(names[0])
        else:
            self.role.set("")

    # ==========================================================
    # SELECCIÓN DE USUARIO
    # ==========================================================

    def _on_user_selected(self, _event=None):
        selected = self.tree.selected_values()

        if not selected:
            self._clear_user_selection()
            return

        try:
            user_id = int(selected[0])
        except (TypeError, ValueError):
            self._clear_user_selection()
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

        self._set_user_action_state(True)

    def _clear_user_selection(self):
        self.selected_user_id = None
        self.selected_user_role = None
        self.selected_user_active = None

        self.selected_user_label.configure(
            text="Ningún usuario seleccionado",
        )

        self._set_user_action_state(False)

    # ==========================================================
    # SELECCIÓN DE ROL
    # ==========================================================

    def _on_role_selected(self, _event=None):
        selected = self.roles_tree.selected_values()

        if not selected:
            self._clear_role_selection()
            return

        try:
            role_id = int(selected[0])
        except (TypeError, ValueError):
            self._clear_role_selection()
            return

        role_name = selected[1]
        state = selected[2]

        self.selected_role_id = role_id
        self.selected_role_name = role_name
        self.selected_role_active = state == "Activo"

        self.selected_role_label.configure(
            text=(
                f"Rol: {role_name}    •    "
                f"Estado: {state}"
            )
        )

        self._render_role_permissions(role_id)

        self._set_role_action_state(True)

    def _clear_role_selection(self):
        self.selected_role_id = None
        self.selected_role_name = None
        self.selected_role_active = None

        self.selected_role_label.configure(
            text="Ningún rol seleccionado",
        )

        self._clear_permission_checkboxes()
        self._set_role_action_state(False)
        self._set_permissions_state(False)

    # ==========================================================
    # PERMISOS
    # ==========================================================

    def _render_role_permissions(self, role_id):
        self._clear_permission_checkboxes()

        permissions = list_permissions(
            self.connection,
        )

        assigned = get_role_permissions(
            self.connection,
            role_id,
        )

        for permission_id, code, description in permissions:
            variable = tkui.BooleanVar(
                value=code in assigned,
            )

            self.permission_vars[code] = variable

            checkbox = tkui.CheckBox(
                self.permissions_scroll,
                text=description,
                variable=variable,
                font=theme.font("body"),
                text_color=theme.color("text"),
                hover_color=theme.color("accent"),
            )

            checkbox.pack(
                fill="x",
                padx=8,
                pady=7,
            )

        self._set_permissions_state(
            self.selected_role_active is True,
        )

    def _clear_permission_checkboxes(self):
        for widget in self.permissions_scroll.winfo_children():
            widget.destroy()

        self.permission_vars.clear()

    # ==========================================================
    # ESTADOS
    # ==========================================================

    def _set_user_action_state(self, enabled):
        state = "normal" if enabled else "disabled"

        self.change_role_button.configure(
            state=state,
        )

        self.change_password_button.configure(
            state=state,
        )

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

    def _set_role_action_state(self, enabled):
        state = "normal" if enabled else "disabled"

        self.rename_role_button.configure(
            state=state,
        )

        if not enabled:
            self.activate_role_button.configure(
                state="disabled",
            )
            self.deactivate_role_button.configure(
                state="disabled",
            )
            return

        if self.selected_role_active:
            self.activate_role_button.configure(
                state="disabled",
            )
            self.deactivate_role_button.configure(
                state="normal",
            )
        else:
            self.activate_role_button.configure(
                state="normal",
            )
            self.deactivate_role_button.configure(
                state="disabled",
            )

    def _set_permissions_state(self, enabled):
        state = "normal" if enabled else "disabled"

        self.save_permissions_button.configure(
            state=state,
        )

        for widget in self.permissions_scroll.winfo_children():
            try:
                widget.configure(state=state)
            except Exception:
                pass

    # ==========================================================
    # CREAR USUARIO
    # ==========================================================

    def create(self):
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
    # CAMBIAR ROL
    # ==========================================================

    def change_role(self):
        if self.selected_user_id is None:
            return

        roles = list_roles(
            self.connection,
            include_inactive=False,
        )

        names = tuple(
            role[1]
            for role in roles
        )

        if not names:
            return

        dialog = tkui.Toplevel(self.window)
        dialog.title("Cambiar rol")
        dialog.geometry("420x230")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        container = tkui.Frame(
            dialog,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25,
        )

        tkui.Label(
            container,
            text="Nuevo rol",
            font=theme.font("body_bold"),
            text_color=theme.color("text"),
            anchor="w",
        ).pack(
            fill="x",
            pady=(0, 6),
        )

        role_var = tkui.StringVar(
            value=self.selected_user_role
            if self.selected_user_role in names
            else names[0]
        )

        combo = inputs.make_combobox(
            container,
            values=names,
            textvariable=role_var,
            state="readonly",
        )
        combo.pack(
            fill="x",
        )

        buttons = tkui.Frame(
            container,
            fg_color="transparent",
        )
        buttons.pack(
            fill="x",
            pady=(25, 0),
        )

        def save():
            try:
                change_user_role(
                    self.connection,
                    self.selected_user_id,
                    role_var.get(),
                    self.actor_id,
                )

                dialog.destroy()
                self.refresh()

                messagebox.showinfo(
                    "Usuarios",
                    "Rol actualizado correctamente.",
                    parent=self.window,
                )

            except Exception as exc:
                messagebox.showerror(
                    "Usuarios",
                    str(exc),
                    parent=dialog,
                )

        AppButton(
            buttons,
            text="Cancelar",
            command=dialog.destroy,
            variant="secondary",
            size="medium",
        ).pack(
            side="right",
            padx=(8, 0),
        )

        AppButton(
            buttons,
            text="Guardar",
            command=save,
            variant="success",
            size="medium",
        ).pack(
            side="right",
        )

    # ==========================================================
    # CAMBIAR CONTRASEÑA
    # ==========================================================

    def change_password(self):
        if self.selected_user_id is None:
            return

        dialog = tkui.Toplevel(self.window)
        dialog.title("Cambiar contraseña")
        dialog.geometry("430x300")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        container = tkui.Frame(
            dialog,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25,
        )

        tkui.Label(
            container,
            text="Nueva contraseña",
            font=theme.font("body_bold"),
            text_color=theme.color("text"),
            anchor="w",
        ).pack(
            fill="x",
            pady=(0, 6),
        )

        password_var = tkui.StringVar()

        password_entry = inputs.make_entry(
            container,
            textvariable=password_var,
            placeholder_text="Mínimo 8 caracteres",
            show="*",
            expand=True,
        )
        password_entry.pack(
            fill="x",
        )

        tkui.Label(
            container,
            text="Confirmar contraseña",
            font=theme.font("body_bold"),
            text_color=theme.color("text"),
            anchor="w",
        ).pack(
            fill="x",
            pady=(15, 6),
        )

        confirm_var = tkui.StringVar()

        confirm_entry = inputs.make_entry(
            container,
            textvariable=confirm_var,
            placeholder_text="Repite la contraseña",
            show="*",
            expand=True,
        )
        confirm_entry.pack(
            fill="x",
        )

        buttons = tkui.Frame(
            container,
            fg_color="transparent",
        )
        buttons.pack(
            fill="x",
            pady=(20, 0),
        )

        def save():
            password = password_var.get()
            confirmation = confirm_var.get()

            if password != confirmation:
                messagebox.showerror(
                    "Contraseña",
                    "Las contraseñas no coinciden.",
                    parent=dialog,
                )
                return

            try:
                change_user_password(
                    self.connection,
                    self.selected_user_id,
                    password,
                    self.actor_id,
                )

                dialog.destroy()

                messagebox.showinfo(
                    "Contraseña",
                    "Contraseña actualizada correctamente.",
                    parent=self.window,
                )

            except Exception as exc:
                messagebox.showerror(
                    "Contraseña",
                    str(exc),
                    parent=dialog,
                )

        AppButton(
            buttons,
            text="Cancelar",
            command=dialog.destroy,
            variant="secondary",
            size="medium",
        ).pack(
            side="right",
            padx=(8, 0),
        )

        AppButton(
            buttons,
            text="Guardar",
            command=save,
            variant="success",
            size="medium",
        ).pack(
            side="right",
        )

        password_entry.focus_set()

    # ==========================================================
    # ACTIVAR USUARIO
    # ==========================================================

    def activate(self):
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
    # DESACTIVAR USUARIO
    # ==========================================================

    def deactivate(self):
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

    # ==========================================================
    # CREAR ROL
    # ==========================================================

    def create_role(self):
        dialog = tkui.Toplevel(self.window)
        dialog.title("Crear rol")
        dialog.geometry("420x220")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        container = tkui.Frame(
            dialog,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25,
        )

        tkui.Label(
            container,
            text="Nombre del rol",
            font=theme.font("body_bold"),
            text_color=theme.color("text"),
            anchor="w",
        ).pack(
            fill="x",
            pady=(0, 6),
        )

        name_var = tkui.StringVar()

        entry = inputs.make_entry(
            container,
            textvariable=name_var,
            placeholder_text="Ej. Supervisor",
            expand=True,
        )
        entry.pack(
            fill="x",
        )

        buttons = tkui.Frame(
            container,
            fg_color="transparent",
        )
        buttons.pack(
            fill="x",
            pady=(20, 0),
        )

        def save():
            try:
                create_role(
                    self.connection,
                    name_var.get(),
                    self.actor_id,
                )

                dialog.destroy()
                self.refresh()

                messagebox.showinfo(
                    "Roles",
                    "Rol creado correctamente.",
                    parent=self.window,
                )

            except Exception as exc:
                messagebox.showerror(
                    "Roles",
                    str(exc),
                    parent=dialog,
                )

        AppButton(
            buttons,
            text="Cancelar",
            command=dialog.destroy,
            variant="secondary",
            size="medium",
        ).pack(
            side="right",
            padx=(8, 0),
        )

        AppButton(
            buttons,
            text="Crear",
            command=save,
            variant="success",
            size="medium",
        ).pack(
            side="right",
        )

        entry.focus_set()

    # ==========================================================
    # RENOMBRAR ROL
    # ==========================================================

    def rename_role(self):
        if self.selected_role_id is None:
            return

        dialog = tkui.Toplevel(self.window)
        dialog.title("Editar rol")
        dialog.geometry("420x220")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        container = tkui.Frame(
            dialog,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25,
        )

        tkui.Label(
            container,
            text="Nombre del rol",
            font=theme.font("body_bold"),
            text_color=theme.color("text"),
            anchor="w",
        ).pack(
            fill="x",
            pady=(0, 6),
        )

        name_var = tkui.StringVar(
            value=self.selected_role_name or "",
        )

        entry = inputs.make_entry(
            container,
            textvariable=name_var,
            expand=True,
        )
        entry.pack(
            fill="x",
        )

        buttons = tkui.Frame(
            container,
            fg_color="transparent",
        )
        buttons.pack(
            fill="x",
            pady=(20, 0),
        )

        def save():
            try:
                rename_role(
                    self.connection,
                    self.selected_role_id,
                    name_var.get(),
                    self.actor_id,
                )

                dialog.destroy()
                self.refresh()

                messagebox.showinfo(
                    "Roles",
                    "Rol actualizado correctamente.",
                    parent=self.window,
                )

            except Exception as exc:
                messagebox.showerror(
                    "Roles",
                    str(exc),
                    parent=dialog,
                )

        AppButton(
            buttons,
            text="Cancelar",
            command=dialog.destroy,
            variant="secondary",
            size="medium",
        ).pack(
            side="right",
            padx=(8, 0),
        )

        AppButton(
            buttons,
            text="Guardar",
            command=save,
            variant="success",
            size="medium",
        ).pack(
            side="right",
        )

    # ==========================================================
    # ACTIVAR ROL
    # ==========================================================

    def activate_selected_role(self):
        if self.selected_role_id is None:
            return

        confirmed = messagebox.askyesno(
            "Roles",
            "¿Activar el rol seleccionado?",
            parent=self.window,
        )

        if not confirmed:
            return

        try:
            activate_role(
                self.connection,
                self.selected_role_id,
                self.actor_id,
            )

            self.refresh()

        except Exception as exc:
            messagebox.showerror(
                "Roles",
                str(exc),
                parent=self.window,
            )

    # ==========================================================
    # DESACTIVAR ROL
    # ==========================================================

    def deactivate_selected_role(self):
        if self.selected_role_id is None:
            return

        confirmed = messagebox.askyesno(
            "Roles",
            "¿Desactivar el rol seleccionado?",
            parent=self.window,
        )

        if not confirmed:
            return

        try:
            deactivate_role(
                self.connection,
                self.selected_role_id,
                self.actor_id,
            )

            self.refresh()

        except Exception as exc:
            messagebox.showerror(
                "Roles",
                str(exc),
                parent=self.window,
            )

    # ==========================================================
    # GUARDAR PERMISOS
    # ==========================================================

    def save_permissions(self):
        if self.selected_role_id is None:
            return

        if not self.selected_role_active:
            return

        selected_permissions = {
            code
            for code, variable in self.permission_vars.items()
            if variable.get()
        }

        confirmed = messagebox.askyesno(
            "Permisos",
            (
                "¿Guardar los permisos seleccionados "
                f"para el rol «{self.selected_role_name}»?"
            ),
            parent=self.window,
        )

        if not confirmed:
            return

        try:
            self.save_permissions_button.set_loading(
                True,
                "Guardando...",
            )
            self.window.update_idletasks()

            set_role_permissions(
                self.connection,
                self.selected_role_id,
                selected_permissions,
                self.actor_id,
            )

            self._render_role_permissions(
                self.selected_role_id,
            )

            messagebox.showinfo(
                "Permisos",
                "Permisos actualizados correctamente.",
                parent=self.window,
            )

        except Exception as exc:
            messagebox.showerror(
                "Permisos",
                str(exc),
                parent=self.window,
            )

        finally:
            self.save_permissions_button.set_loading(False)