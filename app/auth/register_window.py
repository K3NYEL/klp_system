import logging
import sqlite3
import tkinter as tk
from typing import Optional

import customtkinter as ctk
from tkinter import messagebox

from app.core.ui import set_app_icon
from app.core.database import connect_database, audit
from app.auth.security import hash_password
from app.auth.password_window import PasswordWindow


class RegisterWindow:
    def __init__(self, root, login_window):
        self.root = root
        self.login_window = login_window
        self.base_path = login_window.base_path
        self.db_path = login_window.db_path

        self.window: Optional[tk.Toplevel] = None
        self.password = None
        self.password_status_var = None

    def open_register_window(self):
        try:
            return self._build_register_window()
        except Exception:
            logging.exception("Error construyendo la ventana de registro.")
            messagebox.showerror(
                "Error",
                "No se pudo abrir la ventana de registro. Revisa el log para más detalle.",
            )
            self.window = None
            return None

    def _build_register_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("Registro de Usuario")
        set_app_icon(self.window, self.base_path)

        self.window.geometry("500x470")
        self.window.resizable(False, False)
        self.window.configure(bg="#f0f0f0")
        self.window.transient(self.root)

        self.login_window.center_window(
            500,
            470,
            window=self.window,
        )

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.close_register_window,
        )

        # ==========================================================
        # TÍTULO
        # ==========================================================

        ctk.CTkLabel(
            self.window,
            text="Crear cuenta",
            font=("Roboto", 22, "bold"),
            text_color="#2d3436",
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            self.window,
            text="Registra un nuevo usuario en el sistema.",
            font=("Arial", 13),
            text_color="#636e72",
        ).pack(pady=(0, 20))

        # ==========================================================
        # FORMULARIO
        # ==========================================================

        form_frame = ctk.CTkFrame(
            self.window,
            fg_color="#ffffff",
            corner_radius=12,
        )

        form_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=(0, 20),
        )

        form_frame.columnconfigure(1, weight=1)

        # ==========================================================
        # USUARIO
        # ==========================================================

        ctk.CTkLabel(
            form_frame,
            text="Usuario",
            font=("Arial", 13, "bold"),
            text_color="#2d3436",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=22,
            pady=(25, 8),
        )

        new_user_var = tk.StringVar()

        username_entry = ctk.CTkEntry(
            form_frame,
            textvariable=new_user_var,
            font=("Arial", 13),
            height=32,
        )

        username_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 22),
            pady=(25, 8),
        )

        # ==========================================================
        # CONTRASEÑA
        # ==========================================================

        ctk.CTkLabel(
            form_frame,
            text="Contraseña",
            font=("Arial", 13, "bold"),
            text_color="#2d3436",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=22,
            pady=8,
        )

        self.password_status_var = tk.StringVar(value="No configurada")

        ctk.CTkButton(
            form_frame,
            textvariable=self.password_status_var,
            command=self.open_password_window,
            font=("Arial", 13, "bold"),
            width=180,
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=(0, 22),
            pady=8,
        )

        # ==========================================================
        # TIPO DE USUARIO
        # ==========================================================

        ctk.CTkLabel(
            form_frame,
            text="Tipo de usuario",
            font=("Arial", 13, "bold"),
            text_color="#2d3436",
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=22,
            pady=8,
        )

        ctk.CTkLabel(
            form_frame,
            text="Vendedor (o Administrador si es el primer usuario)",
            font=("Arial", 12),
            text_color="#636e72",
        ).grid(
            row=2,
            column=1,
            sticky="w",
            padx=(0, 22),
            pady=8,
        )

        # ==========================================================
        # BOTONES
        # ==========================================================

        button_frame = ctk.CTkFrame(
            form_frame,
            fg_color="transparent",
        )

        button_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=22,
            pady=(20, 20),
        )

        register_button = ctk.CTkButton(
            button_frame,
            text="Guardar cuenta",
            command=lambda: self.register_user(
                new_user_var.get().strip(),
            ),
            font=("Arial", 13, "bold"),
            width=170,
        )

        register_button.pack(
            side=tk.LEFT,
            padx=(0, 10),
        )

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.close_register_window,
            fg_color="#757575",
            hover_color="#616161",
            font=("Arial", 13, "bold"),
            width=130,
        )

        cancel_button.pack(
            side=tk.LEFT,
        )

        # ==========================================================
        # ATAJOS DE TECLADO
        # ==========================================================

        self.window.bind(
            "<Return>",
            lambda event: register_button.invoke(),
        )

        self.window.bind(
            "<Escape>",
            lambda event: self.close_register_window(),
        )

        username_entry.focus_set()

        # ==========================================================
        # MODAL
        # ==========================================================

        try:
            self.window.wait_visibility()
            self.window.grab_set()
        except tk.TclError:
            logging.warning("No se pudo hacer modal la ventana de registro (grab_set).")

        return self.window

    # ==============================================================
    # VENTANA DE CONTRASEÑA
    # ==============================================================

    def open_password_window(self):
        if self.window is None:
            return

        password_window = PasswordWindow(self.window)
        password = password_window.open()

        if password is not None:
            self.password = password

            if self.password_status_var is not None:
                self.password_status_var.set("Contraseña configurada")

    # ==============================================================
    # CERRAR VENTANA
    # ==============================================================

    def close_register_window(self):
        if self.window is not None:
            try:
                self.window.grab_release()
            except tk.TclError:
                pass

            try:
                self.window.destroy()
            except tk.TclError:
                pass

            self.window = None

        try:
            self.root.deiconify()
        except tk.TclError:
            pass

        try:
            self.root.lift()
            self.root.focus_force()
        except tk.TclError:
            pass

    # ==============================================================
    # REGISTRAR USUARIO
    # ==============================================================

    def register_user(self, usuario):
        window = self.window

        if window is None:
            return

        clave = self.password

        # ----------------------------------------------------------
        # VALIDACIÓN DE USUARIO
        # ----------------------------------------------------------

        if not usuario:
            messagebox.showwarning(
                "Advertencia",
                "Complete el campo de usuario",
                parent=window,
            )
            return

        # ----------------------------------------------------------
        # VALIDACIÓN DE CONTRASEÑA
        # ----------------------------------------------------------

        if not clave:
            messagebox.showwarning(
                "Advertencia",
                "Debe crear una contraseña antes de guardar la cuenta.",
                parent=window,
            )
            return

        # ----------------------------------------------------------
        # BASE DE DATOS
        # ----------------------------------------------------------

        try:
            with connect_database(self.db_path) as conn:
                cursor = conn.cursor()

                # Verificar si el usuario ya existe
                cursor.execute(
                    "SELECT id FROM usuarios WHERE usuario = ?",
                    (usuario,),
                )

                if cursor.fetchone():
                    messagebox.showwarning(
                        "Advertencia",
                        "El usuario ya existe",
                        parent=window,
                    )
                    return

                # Determinar si es el primer usuario
                cursor.execute("SELECT COUNT(*) FROM usuarios")

                first_user = cursor.fetchone()[0] == 0

                assigned_role = "Administrador" if first_user else "Vendedor"

                # Crear usuario
                cursor.execute(
                    """
                    INSERT INTO usuarios
                    (usuario, clave, role)
                    VALUES (?, ?, ?)
                    """,
                    (
                        usuario,
                        hash_password(clave),
                        assigned_role,
                    ),
                )

                user_id = cursor.lastrowid

                # Auditoría
                audit(
                    conn,
                    "CREAR_USUARIO",
                    "usuarios",
                    user_id,
                    usuario,
                    user_id,
                )

                conn.commit()

            # ------------------------------------------------------
            # REGISTRO EXITOSO
            # ------------------------------------------------------

            messagebox.showinfo(
                "Registro exitoso",
                f"Usuario registrado correctamente como {assigned_role}.\n"
                "Ahora puede iniciar sesión.",
                parent=window,
            )

            try:
                self.login_window.username_var.set(usuario)
            except Exception:
                pass

            self.close_register_window()

        except sqlite3.Error as e:
            logging.exception("Error de base de datos al registrar usuario.")

            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudo crear el usuario: {e}",
                parent=window,
            )
