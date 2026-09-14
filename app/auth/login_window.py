import logging
import os
import sqlite3
import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

from app.core.ui import CREATOR_URL, configure_app_style, set_app_icon
from app.core.paths import application_path
from app.core.database import connect_database, audit
from app.auth.security import hash_password, verify_password
from app.auth.register_window import RegisterWindow


class LoginWindow:
    creator = CREATOR_URL

    def __init__(self, root, on_success):
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self.root = root
        self.on_success = on_success
        self.root.title("Sistema de Facturacion")

        self.base_path = self.get_base_path()
        self.db_path = os.path.join(self.base_path, "facturacion.db")

        set_app_icon(self.root, self.base_path)
        configure_app_style()

        self.root.geometry("460x430")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        self.center_window(460, 430)

        self.configure_logs()

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.show_password_var = tk.BooleanVar(value=False)
        self.remember_var = tk.BooleanVar(value=False)

        # Referencia a la ventana de registro para no abrir varias a
        # la vez y para poder reutilizarla si ya está abierta.
        self.register_window = None

        # -----------------------------------------------------------
        # RED DE SEGURIDAD: si algo revienta dentro de un callback de
        # Tkinter (por ejemplo, dentro de open_register_window(), que
        # se ejecuta como reacción al click del botón), Tkinter por
        # defecto NO cierra el programa: solo imprime el traceback en
        # stderr y el mainloop sigue corriendo. Si eso pasa justo
        # después de un self.root.withdraw() (como en RegisterWindow),
        # el resultado es exactamente lo que estás viendo: la ventana
        # desaparece y el proceso queda vivo en segundo plano, sin
        # ningún mensaje visible.
        #
        # Con esto: el error queda logueado, se muestra en pantalla, y
        # si el root había quedado oculto, se vuelve a mostrar.
        # -----------------------------------------------------------
        self.root.report_callback_exception = self._handle_callback_exception

        self.ensure_user_table()
        self.load_remembered_user()
        self.create_widgets()
        self.root.bind("<Return>", lambda event: self.login())

    def configure_logs(self):
        logs_path = os.path.join(self.base_path, "logs")
        os.makedirs(logs_path, exist_ok=True)

        date_now = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(logs_path, f"{date_now}.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding="utf-8",
        )

        logging.info("=== FACTURING SYSTEM STARTED ===")

    def register_accion(self, mensaje, nivel="info"):
        nivel = nivel.lower()
        if nivel == "info":
            logging.info(mensaje)
        elif nivel == "warning":
            logging.warning(mensaje)
        elif nivel == "error":
            logging.error(mensaje)
        else:
            logging.debug(mensaje)

    def get_base_path(self):
        return application_path()

    def _handle_callback_exception(self, exc, val, tb):
        """
        Handler global para excepciones no controladas dentro de
        callbacks de Tkinter (clicks de botones, binds, etc.).
        """
        logging.exception(
            "Excepción no controlada en un callback de Tkinter",
            exc_info=(exc, val, tb),
        )

        try:
            if self.root.winfo_exists() and self.root.state() == "withdrawn":
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
        except tk.TclError:
            pass

        messagebox.showerror(
            "Error inesperado",
            f"Ocurrió un error inesperado:\n\n{val}\n\n"
            "Revisa el archivo de log en la carpeta 'logs' para más detalle.",
        )

    def ensure_user_table(self):
        """
        BUG QUE HABÍA ACÁ: esta función abría un cursor y no hacía
        nada más. Nunca se creaban las tablas "usuarios" ni "config",
        así que en una base de datos nueva, login()/register_user()/
        load_remembered_user() fallaban (o fallaban en silencio,
        porque atrapan sqlite3.Error con "pass").
        """
        try:
            with connect_database(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT NOT NULL UNIQUE,
                        clave TEXT NOT NULL,
                        role TEXT NOT NULL DEFAULT 'Vendedor',
                        activo INTEGER NOT NULL DEFAULT 1,
                        ultimo_acceso TIMESTAMP,
                        intentos_fallidos INTEGER NOT NULL DEFAULT 0
                    )
                    """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS config (
                        clave TEXT PRIMARY KEY,
                        valor TEXT
                    )
                    """
                )

                conn.commit()

        except sqlite3.Error as e:
            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudo inicializar la tabla de usuarios: {e}",
            )

    def hash_password(self, password):
        return hash_password(password)

    def center_window(self, width, height, window=None):
        if window is None:
            window = self.root
        window.update_idletasks()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def load_remembered_user(self):
        try:
            with connect_database(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT valor FROM config WHERE clave = ?", ("remembered_user",)
                )
                row = cursor.fetchone()
                if row and row[0]:
                    self.username_var.set(row[0])
                    self.remember_var.set(True)
        except sqlite3.Error as e:
            logging.warning(f"No se pudo cargar el usuario recordado: {e}")

    def save_remembered_user(self):
        try:
            with connect_database(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "REPLACE INTO config (clave, valor) VALUES (?, ?)",
                    ("remembered_user", self.username_var.get().strip()),
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.warning(f"No se pudo guardar el usuario recordado: {e}")

    def clear_remembered_user(self):
        try:
            with connect_database(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM config WHERE clave = ?", ("remembered_user",))
                conn.commit()
        except sqlite3.Error as e:
            logging.warning(f"No se pudo eliminar el usuario recordado: {e}")

    def toggle_password_visibility(self):
        show_char = "" if self.show_password_var.get() else "*"
        self.password_entry.configure(show=show_char)

    def create_widgets(self):
        login_frame = tk.Frame(self.root, bg="#ffffff", width=400, height=300)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        header_frame = tk.Frame(login_frame, bg="#3498db")
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame,
            text="Acceso al sistema",
            bg="#3498db",
            fg="white",
            font=("Arial", 17, "bold"),
        ).pack(pady=(14, 4))

        ctk.CTkLabel(
            login_frame,
            text="Ingrese sus datos para continuar",
            text_color="#555",
            font=("Arial", 15),
        ).pack(pady=(16, 14))

        ctk.CTkLabel(
            login_frame, text="Usuario", font=("Roboto", 15, "bold"), text_color="#2d3436"
        ).pack(anchor="w", padx=36)
        self.username_entry = ctk.CTkEntry(
            login_frame,
            textvariable=self.username_var,
            font=("Arial", 15, "bold"),
            height=34,
            border_width=1,
        )
        self.username_entry.pack(fill=tk.X, padx=36, pady=(4, 12))

        ctk.CTkLabel(
            login_frame, text="Contraseña", font=("Arial", 15, "bold"), text_color="#2d3436"
        ).pack(anchor="w", padx=36)
        self.password_entry = ctk.CTkEntry(
            login_frame,
            textvariable=self.password_var,
            font=("Arial", 15, "bold"),
            show="*",
            height=34,
            border_width=1,
        )
        self.password_entry.pack(fill=tk.X, padx=36, pady=(4, 12))

        options_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        options_frame.pack(fill=tk.X, padx=34, pady=(0, 12))

        ctk.CTkCheckBox(
            options_frame,
            text="Mostrar contraseña",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            text_color="#2d3436",
            font=("Arial", 13),
        ).pack(side=tk.LEFT)
        ctk.CTkCheckBox(
            options_frame,
            text="Recordar usuario",
            variable=self.remember_var,
            text_color="#2d3436",
            font=("Arial", 13),
        ).pack(side=tk.RIGHT)

        btn_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=36, pady=(4, 15))

        ctk.CTkButton(
            btn_frame,
            text="Entrar",
            command=self.login,
            font=("Arial", 15, "bold"),
            height=36,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        ctk.CTkButton(
            btn_frame,
            text="Crear cuenta",
            command=self.open_register_window,
            fg_color="#43a047",
            hover_color="#388e3c",
            font=("Arial", 15, "bold"),
            height=36,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        if self.username_var.get().strip():
            self.password_entry.focus_set()
        else:
            self.username_entry.focus_set()

    def open_register_window(self):
        """
        Este método no estaba definido en el archivo que compartiste
        (el botón "Crear cuenta" lo llamaba pero no existía). Además de
        agregarlo, se guarda la referencia en self.register_window
        para no permitir abrir dos ventanas de registro al mismo
        tiempo.
        """
        if self.register_window is not None and self.register_window.winfo_exists():
            self.register_window.lift()
            self.register_window.focus_force()
            return

        register_controller = RegisterWindow(self.root, self)
        result = register_controller.open_register_window()

        # Si _build_register_window() falló, open_register_window()
        # ya restauró el root y avisó del error; no dejamos una
        # referencia inválida guardada.
        self.register_window = result

    def login(self):
        usuario = self.username_var.get().strip()
        # No se hace .strip() a la contraseña: si el usuario la puso
        # con espacios a propósito, quitárselos la invalidaría.
        clave = self.password_var.get()

        if not usuario or not clave:
            messagebox.showwarning(
                "Advertencia", "Ingrese usuario y contraseña", parent=self.root
            )
            return

        try:
            with connect_database(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, clave, activo, role FROM usuarios WHERE usuario = ?",
                    (usuario,),
                )
                row = cursor.fetchone()
                valid, needs_upgrade = verify_password(clave, row[1]) if row else (False, False)

                if row and row[2] and valid:
                    user_id, _, _activo, role = row

                    if needs_upgrade:
                        cursor.execute(
                            "UPDATE usuarios SET clave=? WHERE id=?",
                            (hash_password(clave), user_id),
                        )
                    cursor.execute(
                        "UPDATE usuarios SET ultimo_acceso=CURRENT_TIMESTAMP, "
                        "intentos_fallidos=0 WHERE id=?",
                        (user_id,),
                    )
                    audit(conn, "INICIO_SESION", "usuarios", user_id, usuario, user_id)

                    if self.remember_var.get():
                        cursor.execute(
                            "REPLACE INTO config (clave, valor) VALUES (?, ?)",
                            ("remembered_user", usuario),
                        )
                    else:
                        cursor.execute(
                            "DELETE FROM config WHERE clave = ?", ("remembered_user",)
                        )

                    conn.commit()

                    self.root.destroy()
                    self.on_success({"id": user_id, "usuario": usuario, "role": role})

                else:
                    if row:
                        cursor.execute(
                            "UPDATE usuarios SET intentos_fallidos=intentos_fallidos+1 "
                            "WHERE id=?",
                            (row[0],),
                        )
                        # Antes esta llamada pasaba 5 argumentos y la de
                        # login exitoso pasaba 6 (le faltaba
                        # performed_by). Se igualan para que la
                        # auditoría quede completa en ambos casos.
                        audit(
                            conn,
                            "FALLO_INICIO_SESION",
                            "usuarios",
                            row[0],
                            usuario,
                            row[0],
                        )
                        conn.commit()

                    messagebox.showwarning(
                        "Acceso denegado",
                        "Usuario o contraseña incorrectos. Si no tiene cuenta, regístrese.",
                        parent=self.root,
                    )
        except sqlite3.Error as e:
            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudo validar el usuario: {e}",
                parent=self.root,
            )