import logging
import os
import sqlite3
import tkinter as tk
from app.ui import tk_widgets as tkui

from datetime import datetime
from tkinter import messagebox

from app.core.ui import CREATOR_URL, configure_app_style, set_app_icon
from app.core.paths import application_path
from app.core.database import connect_database, audit
from app.auth.security import hash_password, verify_password
from app.auth.register_window import RegisterWindow

from app.ui.styles import Colors, Fonts
from app.ui.components.buttons import AppButton
from app.ui.components import inputs


class LoginWindow:

    creator = CREATOR_URL

    def __init__(self, root, on_success):

        self.root = root
        self.on_success = on_success

        # =============================================================
        # CONFIGURACIÓN GENERAL
        # =============================================================

        configure_app_style()

        self.root.title("KLP SYSTEM - Iniciar sesión")
        self.root.geometry("460x430")
        self.root.resizable(False, False)

        self.base_path = self.get_base_path()
        self.db_path = os.path.join(
            self.base_path,
            "facturacion.db"
        )

        set_app_icon(
            self.root,
            self.base_path
        )

        self.center_window(
            460,
            430
        )

        # =============================================================
        # LOGS
        # =============================================================

        self.configure_logs()

        # =============================================================
        # VARIABLES
        # =============================================================

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.show_password_var = tk.BooleanVar(
            value=False
        )

        self.remember_var = tk.BooleanVar(
            value=False
        )

        # Referencia a ventana de registro
        self.register_window = None

        # =============================================================
        # MANEJO GLOBAL DE ERRORES
        # =============================================================

        self.root.report_callback_exception = (
            self._handle_callback_exception
        )

        # =============================================================
        # BASE DE DATOS
        # =============================================================

        self.ensure_user_table()
        self.load_remembered_user()

        # =============================================================
        # INTERFAZ
        # =============================================================

        self.create_widgets()

        self.root.bind(
            "<Return>",
            lambda event: self.login()
        )

    # =============================================================
    # LOGGING
    # =============================================================

    def configure_logs(self):

        logs_path = os.path.join(
            self.base_path,
            "logs"
        )

        os.makedirs(
            logs_path,
            exist_ok=True
        )

        date_now = datetime.now().strftime(
            "%Y-%m-%d"
        )

        log_file = os.path.join(
            logs_path,
            f"{date_now}.log"
        )

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding="utf-8",
        )

        logging.info(
            "=== FACTURING SYSTEM STARTED ==="
        )

    def register_accion(
        self,
        mensaje,
        nivel="info"
    ):

        nivel = nivel.lower()

        if nivel == "info":
            logging.info(mensaje)

        elif nivel == "warning":
            logging.warning(mensaje)

        elif nivel == "error":
            logging.error(mensaje)

        else:
            logging.debug(mensaje)

    # =============================================================
    # UTILIDADES
    # =============================================================

    def get_base_path(self):
        return application_path()

    def center_window(
        self,
        width,
        height,
        window=None
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

    def _handle_callback_exception(
        self,
        exc,
        val,
        tb
    ):

        """
        Handler global para excepciones no controladas
        dentro de callbacks de Tkinter.
        """

        logging.exception(
            "Excepción no controlada en un callback de Tkinter",
            exc_info=(exc, val, tb),
        )

        try:
            # El login se destruye al autenticar. Si la creación de la
            # ventana principal falla después, no intentar abrir un
            # messagebox usando un intérprete Tk que ya fue destruido.
            if not self.root.winfo_exists():
                return

            if self.root.state() == "withdrawn":
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()

            messagebox.showerror(
                "Error inesperado",
                f"Ocurrió un error inesperado:\n\n{val}\n\n"
                "Revisa el archivo de log en la carpeta 'logs' "
                "para más detalle.",
                parent=self.root,
            )
        except tk.TclError:
            logging.exception(
                "No se pudo mostrar el diálogo de error de Tkinter."
            )

    # =============================================================
    # BASE DE DATOS
    # =============================================================

    def ensure_user_table(self):

        """
        Crea las tablas necesarias para el sistema
        de autenticación si todavía no existen.
        """

        try:

            with connect_database(
                self.db_path
            ) as conn:

                cursor = conn.cursor()

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS usuarios (

                        id INTEGER PRIMARY KEY AUTOINCREMENT,

                        usuario TEXT NOT NULL UNIQUE,

                        clave TEXT NOT NULL,

                        role TEXT NOT NULL
                            DEFAULT 'Vendedor',

                        activo INTEGER NOT NULL
                            DEFAULT 1,

                        ultimo_acceso TIMESTAMP,

                        intentos_fallidos INTEGER NOT NULL
                            DEFAULT 0
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

            logging.exception(
                "Error inicializando las tablas de autenticación."
            )

            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudo inicializar la tabla de usuarios:\n\n{e}",
                parent=self.root,
            )

    def hash_password(self, password):
        return hash_password(password)

    # =============================================================
    # USUARIO RECORDADO
    # =============================================================

    def load_remembered_user(self):

        try:

            with connect_database(
                self.db_path
            ) as conn:

                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT valor
                    FROM config
                    WHERE clave = ?
                    """,
                    ("remembered_user",),
                )

                row = cursor.fetchone()

                if row and row[0]:

                    self.username_var.set(
                        row[0]
                    )

                    self.remember_var.set(
                        True
                    )

        except sqlite3.Error as e:

            logging.warning(
                f"No se pudo cargar el usuario recordado: {e}"
            )

    def save_remembered_user(self):

        try:

            username = self.username_var.get().strip()

            if not username:
                return

            with connect_database(
                self.db_path
            ) as conn:

                cursor = conn.cursor()

                cursor.execute(
                    """
                    REPLACE INTO config (
                        clave,
                        valor
                    )
                    VALUES (?, ?)
                    """,
                    (
                        "remembered_user",
                        username,
                    ),
                )

                conn.commit()

        except sqlite3.Error as e:

            logging.warning(
                f"No se pudo guardar el usuario recordado: {e}"
            )

    def clear_remembered_user(self):

        try:

            with connect_database(
                self.db_path
            ) as conn:

                cursor = conn.cursor()

                cursor.execute(
                    """
                    DELETE FROM config
                    WHERE clave = ?
                    """,
                    ("remembered_user",),
                )

                conn.commit()

        except sqlite3.Error as e:

            logging.warning(
                f"No se pudo eliminar el usuario recordado: {e}"
            )

    # =============================================================
    # CONTRASEÑA
    # =============================================================

    def toggle_password_visibility(self):

        show_char = (
            ""
            if self.show_password_var.get()
            else "*"
        )

        self.password_entry.configure(
            show=show_char
        )

    # =============================================================
    # INTERFAZ
    # =============================================================

    def create_widgets(self):

        # =========================================================
        # FRAME PRINCIPAL
        #
        # Ahora ocupa TODO el contenido de la ventana.
        # =========================================================

        self.login_frame = tkui.Frame(
            self.root,

            fg_color=Colors.SURFACE,

            corner_radius=0,

            border_width=0,
        )

        self.login_frame.pack(
            fill="both",
            expand=True,
        )

        # =========================================================
        # CONTENEDOR CENTRAL
        #
        # Permite mantener el contenido centrado y con márgenes
        # aunque el frame principal ocupe toda la ventana.
        # =========================================================

        content_frame = tkui.Frame(
            self.login_frame,

            fg_color="transparent",

            corner_radius=0,
        )

        content_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center",

            relwidth=0.82,
        )

        # =========================================================
        # HEADER
        # =========================================================

        header_frame = tkui.Frame(
            content_frame,

            fg_color="transparent",

            corner_radius=0,
        )

        header_frame.pack(
            fill="x",
            pady=(0, 18),
        )

        # =========================================================
        # LOGO / IDENTIDAD
        # =========================================================

        tkui.Label(
            header_frame,

            text="KLP SYSTEM",

            text_color=Colors.PRIMARY,

            font=Fonts.TITLE,
        ).pack(
            pady=(0, 3)
        )

        tkui.Label(
            header_frame,

            text="Sistema de facturación",

            text_color=Colors.TEXT_SECONDARY,

            font=Fonts.SMALL,
        ).pack()

        # =========================================================
        # SEPARADOR
        # =========================================================

        separator = tkui.Frame(
            content_frame,

            height=1,

            fg_color=Colors.BORDER,
        )

        separator.pack(
            fill="x",
            pady=(0, 18),
        )

        # =========================================================
        # DESCRIPCIÓN
        # =========================================================

        tkui.Label(
            content_frame,

            text="Inicie sesión para continuar",

            text_color=Colors.TEXT,

            font=Fonts.BODY_BOLD,
        ).pack(
            anchor="w",
            pady=(0, 14),
        )

        # =========================================================
        # USUARIO
        # =========================================================

        self.username_label = tkui.Label(
            content_frame,

            text="Usuario",

            text_color=Colors.TEXT,

            font=Fonts.BODY_BOLD,

            anchor="w",
        )

        self.username_label.pack(
            fill="x",
            pady=(0, 5),
        )

        self.username_entry = inputs.make_entry(
            content_frame,

            textvariable=self.username_var,

            width=328,

            height=38,

            font_role="body",

            placeholder_text="Ingrese su usuario",
        )

        self.username_entry.pack(
            fill="x",

            pady=(0, 14),
        )

        # =========================================================
        # CONTRASEÑA
        # =========================================================

        self.password_label = tkui.Label(
            content_frame,

            text="Contraseña",

            text_color=Colors.TEXT,

            font=Fonts.BODY_BOLD,

            anchor="w",
        )

        self.password_label.pack(
            fill="x",

            pady=(0, 5),
        )

        self.password_entry = inputs.make_entry(
            content_frame,

            textvariable=self.password_var,

            width=328,

            height=38,

            font_role="body",

            placeholder_text="Ingrese su contraseña",

            show="*",
        )

        self.password_entry.pack(
            fill="x",

            pady=(0, 10),
        )

        # =========================================================
        # OPCIONES
        # =========================================================

        options_frame = tkui.Frame(
            content_frame,

            fg_color="transparent",

            corner_radius=0,
        )

        options_frame.pack(
            fill="x",

            pady=(0, 16),
        )

        inputs.make_checkbutton(
            options_frame,

            text="Mostrar contraseña",

            variable=self.show_password_var,

            command=self.toggle_password_visibility,

            font_role="small",
        ).pack(
            side="left"
        )

        inputs.make_checkbutton(
            options_frame,

            text="Recordar usuario",

            variable=self.remember_var,

            font_role="small",
        ).pack(
            side="right"
        )

        # =========================================================
        # BOTONES
        # =========================================================

        btn_frame = tkui.Frame(
            content_frame,

            fg_color="transparent",

            corner_radius=0,
        )

        btn_frame.pack(
            fill="x",

            pady=(0, 12),
        )

        self.login_button = AppButton(
            btn_frame,

            text="Entrar",

            command=self.login,

            variant="primary",

            size="medium",

            font_role="button",
        )

        self.login_button.pack(
            side="left",

            fill="x",

            expand=True,

            padx=(0, 5),
        )

        self.register_button = AppButton(
            btn_frame,

            text="Crear cuenta",

            command=self.open_register_window,

            variant="success",

            size="medium",

            font_role="button",
        )

        self.register_button.pack(
            side="left",

            fill="x",

            expand=True,

            padx=(5, 0),
        )

        # =========================================================
        # FOOTER
        # =========================================================

        tkui.Label(
            content_frame,

            text="KLP SYSTEM",

            text_color=Colors.TEXT_SECONDARY,

            font=Fonts.SMALL,
        ).pack(
            pady=(4, 0)
        )

        # =========================================================
        # FOCUS INICIAL
        # =========================================================

        if self.username_var.get().strip():

            self.password_entry.focus_set()

        else:

            self.username_entry.focus_set()

    # =============================================================
    # REGISTRO
    # =============================================================

    def open_register_window(self):

        """
        Abre la ventana de registro evitando duplicados.
        """

        try:

            if (
                self.register_window is not None
                and self.register_window.winfo_exists()
            ):

                self.register_window.lift()
                self.register_window.focus_force()

                return

        except tk.TclError:

            self.register_window = None

        register_controller = RegisterWindow(
            self.root,
            self,
        )

        result = (
            register_controller.open_register_window()
        )

        self.register_window = result

    # =============================================================
    # LOGIN
    # =============================================================

    def login(self):

        usuario = self.username_var.get().strip()

        # No se hace strip() a la contraseña.
        clave = self.password_var.get()

        if not usuario or not clave:

            messagebox.showwarning(
                "Advertencia",

                "Ingrese usuario y contraseña.",

                parent=self.root,
            )

            return

        try:

            with connect_database(
                self.db_path
            ) as conn:

                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT
                        id,
                        clave,
                        activo,
                        role,
                        (
                            bloqueado_hasta IS NOT NULL
                            AND bloqueado_hasta > CURRENT_TIMESTAMP
                        )
                    FROM usuarios
                    WHERE usuario = ?
                    """,
                    (usuario,),
                )

                row = cursor.fetchone()

                valid, needs_upgrade = (
                    verify_password(
                        clave,
                        row[1]
                    )
                    if row and not row[4]
                    else (False, False)
                )

                # =================================================
                # LOGIN CORRECTO
                # =================================================

                if row and row[2] and valid:

                    user_id, _, _activo, role, _locked = row

                    # -------------------------------------------------
                    # Actualiza hashes antiguos si es necesario.
                    # -------------------------------------------------

                    if needs_upgrade:

                        cursor.execute(
                            """
                            UPDATE usuarios
                            SET clave = ?
                            WHERE id = ?
                            """,
                            (
                                hash_password(clave),
                                user_id,
                            ),
                        )

                    # -------------------------------------------------
                    # Actualizar acceso
                    # -------------------------------------------------

                    cursor.execute(
                        """
                        UPDATE usuarios
                        SET
                            ultimo_acceso = CURRENT_TIMESTAMP,
                            intentos_fallidos = 0,
                            bloqueado_hasta = NULL
                        WHERE id = ?
                        """,
                        (user_id,),
                    )

                    # -------------------------------------------------
                    # Auditoría
                    # -------------------------------------------------

                    audit(
                        conn,

                        "INICIO_SESION",

                        "usuarios",

                        user_id,

                        usuario,

                        user_id,
                    )

                    # -------------------------------------------------
                    # RECORDAR USUARIO
                    # -------------------------------------------------

                    if self.remember_var.get():

                        self.save_remembered_user()

                    else:

                        self.clear_remembered_user()

                    conn.commit()

                    # -------------------------------------------------
                    # CERRAR LOGIN
                    # -------------------------------------------------

                    self.root.destroy()

                    self.on_success(
                        {
                            "id": user_id,

                            "usuario": usuario,

                            "role": role,
                        }
                    )

                # =================================================
                # LOGIN INCORRECTO
                # =================================================

                else:

                    if row and not row[4]:

                        cursor.execute(
                            """
                            UPDATE usuarios
                            SET
                                intentos_fallidos = intentos_fallidos + 1,
                                bloqueado_hasta = CASE
                                    WHEN intentos_fallidos + 1 >= 5
                                    THEN datetime('now', '+15 minutes')
                                    ELSE bloqueado_hasta
                                END
                            WHERE id = ?
                            """,
                            (row[0],),
                        )

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

                        "Usuario o contraseña incorrectos. "
                        "Si no tiene cuenta, regístrese.",

                        parent=self.root,
                    )

        except sqlite3.Error as e:

            logging.exception(
                "Error de base de datos durante "
                "el inicio de sesión."
            )

            messagebox.showerror(
                "Error de Base de Datos",

                f"No se pudo validar el usuario:\n\n{e}",

                parent=self.root,
            )

