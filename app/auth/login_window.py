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

class LoginWindow:
    creator = CREATOR_URL
    def __init__(self, root, on_success):
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self.root = root
        self.on_success = on_success
        self.root.title("Sistema de Facturacion")
        self.base_path = self.get_base_path()
        set_app_icon(self.root, self.base_path)
        self.root.geometry("460x430")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        self.center_window(460, 430)
        self.configure_logs()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.show_password_var = tk.BooleanVar(value=False)
        self.remember_var = tk.BooleanVar(value=False)
        self.base_path = self.get_base_path()
        configure_app_style()
        self.db_path = os.path.join(self.base_path, 'facturacion.db')
        self.ensure_user_table()
        self.load_remembered_user()
        self.create_widgets()
        self.root.bind("<Return>", lambda event: self.login())

    def configure_logs(self):
        # Sistema de los Logs

        # Create a log File doesn´t exist
        logs_path = os.path.join(self.base_path, "logs")
        os.makedirs(logs_path, exist_ok=True)

        # Generate a log file with de currente date
        date_now = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(logs_path, f"{date_now}.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            encoding='utf-8'
        )

        logging.info("=== FACTURING SISTEM STARTED ===")

    def register_accion(self, mensaje,nivel="info"):
        # Easy funtion for register events in the sistem
        if nivel.lower() == "info":
            logging.info(mensaje)
        elif nivel.lower() == "warning":
            logging.warning(mensaje)
        elif nivel.lower() == "error":
            logging.error(mensaje)
        else:
            logging.debug(mensaje) 


    def get_base_path(self):
        return application_path()

    def ensure_user_table(self):
        try:
            with connect_database(self.db_path) as conn:
                conn.cursor()
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos",
                                 f"No se pudo inicializar la tabla de usuarios: {str(e)}")

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
                cursor.execute('SELECT valor FROM config WHERE clave = ?', ('remembered_user',))
                row = cursor.fetchone()
                if row:
                    self.username_var.set(row[0])
                    self.remember_var.set(True)
        except sqlite3.Error:
            pass

    def save_remembered_user(self):
        try:
            with connect_database(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('REPLACE INTO config (clave, valor) VALUES (?, ?)',
                               ('remembered_user', self.username_var.get().strip()))
                conn.commit()
        except sqlite3.Error:
            pass

    def clear_remembered_user(self):
        try:
            with connect_database(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM config WHERE clave = ?', ('remembered_user',))
                conn.commit()
        except sqlite3.Error:
            pass

    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.configure(show='')
        else:
            self.password_entry.configure(show='*')

    def create_widgets(self):
        login_frame = ctk.CTkFrame(self.root, fg_color="#ffffff", corner_radius=14,
                       width=400, height=360)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        header_frame = ctk.CTkFrame(login_frame, fg_color="#3498db", corner_radius=10)
        header_frame.pack(fill=tk.X)
        ctk.CTkLabel(header_frame, text="Acceso al sistema", text_color="white",
                     font=("Arial", 17, "bold")).pack(pady=(14, 4))
        ctk.CTkLabel(header_frame, text="Facturas, clientes y productos en un solo lugar",
                     text_color="#eef7ff", font=("Arial", 9)).pack(pady=(0, 14))

        ctk.CTkLabel(login_frame, text="Ingrese sus datos para continuar",
                     text_color="#555", font=("Arial", 10)).pack(pady=(16, 14))

        ctk.CTkLabel(login_frame, text="Usuario", font=("Arial", 10, "bold"), text_color="#2d3436").pack(anchor="w", padx=36)
        ctk.CTkEntry(login_frame, textvariable=self.username_var, font=("Arial", 10), height=34,
                     border_width=1).pack(fill=tk.X, padx=36, pady=(4, 12))

        ctk.CTkLabel(login_frame, text="Contraseña", font=("Arial", 10, "bold"), text_color="#2d3436").pack(anchor="w", padx=36)
        self.password_entry = ctk.CTkEntry(login_frame, textvariable=self.password_var, font=("Arial", 10),
                                           show="*", height=34, border_width=1)
        self.password_entry.pack(fill=tk.X, padx=36, pady=(4, 12))

        options_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        options_frame.pack(fill=tk.X, padx=34, pady=(0, 12))
        ctk.CTkCheckBox(options_frame, text="Mostrar contraseña", variable=self.show_password_var,
                        command=self.toggle_password_visibility, text_color="#2d3436", font=("Arial", 10)).pack(side=tk.LEFT)
        ctk.CTkCheckBox(options_frame, text="Recordar usuario", variable=self.remember_var,
                        text_color="#2d3436", font=("Arial", 10)).pack(side=tk.RIGHT)

        btn_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=36, pady=(4, 0))

        ctk.CTkButton(btn_frame, text="Entrar al sistema", command=self.login,
                      font=("Arial", 10, "bold"), height=36).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        ctk.CTkButton(btn_frame, text="Crear cuenta", command=self.open_register_window,
                      fg_color="#2ecc71", hover_color="#27ae60",
                      font=("Arial", 10, "bold"), height=36).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        ctk.CTkLabel(self.root, text="© 2026 K.A.R.M. • Facturación Fácil", font=("Arial", 8),
                     text_color="#555").pack(side=tk.BOTTOM, pady=10)

    def login(self):
        usuario = self.username_var.get().strip()
        clave = self.password_var.get().strip()
        if not usuario or not clave:
            messagebox.showwarning("Advertencia", "Ingrese usuario y contraseña")
            return

        try:
            with connect_database(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, clave, activo FROM usuarios WHERE usuario = ?', (usuario,))
                row = cursor.fetchone()
                valid, needs_upgrade = verify_password(clave, row[1]) if row else (False, False)
                if row and row[2] and valid:
                    if needs_upgrade:
                        cursor.execute('UPDATE usuarios SET clave=? WHERE id=?', (hash_password(clave), row[0]))
                    cursor.execute(
                        'UPDATE usuarios SET ultimo_acceso=CURRENT_TIMESTAMP, intentos_fallidos=0 WHERE id=?',
                        (row[0],),
                    )
                    audit(conn, "INICIO_SESION", "usuarios", row[0], usuario, row[0])
                    if self.remember_var.get():
                        cursor.execute(
                            'REPLACE INTO config (clave, valor) VALUES (?, ?)',
                            ('remembered_user', usuario),
                        )
                    else:
                        cursor.execute('DELETE FROM config WHERE clave = ?', ('remembered_user',))
                    conn.commit()
                    self.root.destroy()
                    cursor.execute('SELECT role FROM usuarios WHERE id=?', (row[0],))
                    role = cursor.fetchone()[0]
                    self.on_success({"id": row[0], "usuario": usuario, "role": role})
                else:
                    if row:
                        cursor.execute('UPDATE usuarios SET intentos_fallidos=intentos_fallidos+1 WHERE id=?', (row[0],))
                        audit(conn, "FALLO_INICIO_SESION", "usuarios", row[0], usuario)
                        conn.commit()
                    messagebox.showwarning("Acceso denegado",
                                           "Usuario o contraseña incorrectos. Si no tiene cuenta, regístrese.")
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos",
                                 f"No se pudo validar el usuario: {str(e)}")

    def open_register_window(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Registro de Usuario")
        set_app_icon(register_window, self.base_path)
        register_window.geometry("500x470")
        register_window.resizable(False, False)
        register_window.configure(bg="#f0f0f0")
        register_window.transient(self.root)
        register_window.grab_set()
        self.center_window(500, 470, window=register_window)

        ctk.CTkLabel(register_window, text="Crear cuenta de acceso", font=("Arial", 17, "bold"),
                 text_color="#2d3436").pack(pady=(20, 6))
        ctk.CTkLabel(register_window, text="Complete los datos. Luego podrá iniciar sesión con este usuario.", font=("Arial", 9),
                 text_color="#555").pack()

        form_frame = ctk.CTkFrame(register_window, fg_color="#ffffff", corner_radius=12)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        form_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="Datos de la cuenta", font=("Arial", 13, "bold"),
                     text_color="#2d3436").grid(row=0, column=0, columnspan=2, sticky="w", padx=22, pady=(20, 14))

        ctk.CTkLabel(form_frame, text="Usuario", font=("Arial", 10, "bold"), text_color="#2d3436").grid(row=1, column=0, sticky="w", padx=22, pady=6)
        new_user_var = tk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=new_user_var, font=("Arial", 10), height=32).grid(row=1, column=1, sticky="ew", padx=(0, 22), pady=6)

        ctk.CTkLabel(form_frame, text="Contraseña", font=("Arial", 10, "bold"), text_color="#2d3436").grid(row=2, column=0, sticky="w", padx=22, pady=6)
        new_password_var = tk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=new_password_var, font=("Arial", 10), show="*", height=32).grid(row=2, column=1, sticky="ew", padx=(0, 22), pady=6)

        ctk.CTkLabel(form_frame, text="Confirmar contraseña", font=("Arial", 10, "bold"), text_color="#2d3436").grid(row=3, column=0, sticky="w", padx=22, pady=6)
        confirm_password_var = tk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=confirm_password_var, font=("Arial", 10), show="*", height=32).grid(row=3, column=1, sticky="ew", padx=(0, 22), pady=6)

        ctk.CTkLabel(form_frame, text="Tipo de usuario", font=("Arial", 10, "bold"), text_color="#2d3436").grid(row=4, column=0, sticky="w", padx=22, pady=6)
        ctk.CTkLabel(form_frame, text="Vendedor (asignado por seguridad)", text_color="#636e72",
                     font=("Arial", 10)).grid(row=4, column=1, sticky="w", padx=(0, 22), pady=6)

        ctk.CTkLabel(form_frame, text="La contraseña debe tener mínimo 5 caracteres e incluir letras y números.",
                 font=("Arial", 9), text_color="#636e72").grid(row=5, column=0, columnspan=2, sticky="w", padx=22, pady=(8, 0))

        register_button = ctk.CTkButton(form_frame, text="Guardar cuenta", command=lambda: self.register_user(
            new_user_var.get().strip(), new_password_var.get().strip(), confirm_password_var.get().strip(), "Vendedor", register_window),
                  fg_color="#2ecc71", hover_color="#27ae60", font=("Arial", 10, "bold"),
                  width=220)
        register_button.grid(row=6, column=0, columnspan=2, pady=(24, 16))

        register_window.bind("<Return>", lambda event: register_button.invoke())

    def register_user(self, usuario, clave, clave_confirm, role, window):
        if not usuario or not clave or not clave_confirm:
            messagebox.showwarning("Advertencia", "Complete todos los campos")
            return
        if clave != clave_confirm:
            messagebox.showwarning("Advertencia", "Las contraseñas no coinciden")
            return
        if len(clave) < 5:
            messagebox.showwarning("Advertencia", "La contraseña debe tener al menos 5 caracteres")
            return
        if not any(c.isdigit() for c in clave) or not any(c.isalpha() for c in clave):
            messagebox.showwarning("Advertencia", "La contraseña debe incluir letras y números")
            return

        try:
            with connect_database(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM usuarios WHERE usuario = ?', (usuario,))
                if cursor.fetchone():
                    messagebox.showwarning("Advertencia", "El usuario ya existe")
                    return
                cursor.execute('SELECT COUNT(*) FROM usuarios')
                first_user = cursor.fetchone()[0] == 0
                assigned_role = "Administrador" if first_user else "Vendedor"
                cursor.execute('INSERT INTO usuarios (usuario, clave, role) VALUES (?, ?, ?)',
                               (usuario, hash_password(clave), assigned_role))
                user_id = cursor.lastrowid
                audit(conn, "CREAR_USUARIO", "usuarios", user_id, usuario, user_id)
                conn.commit()
                messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente. Ahora puede iniciar sesión.")
                window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos",
                                 f"No se pudo crear el usuario: {str(e)}")

