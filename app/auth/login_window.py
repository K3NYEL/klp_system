import hashlib
import logging
import os
import sqlite3
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from app.core.ui import CREATOR_URL, configure_app_style, set_app_icon

class LoginWindow:
    creator = CREATOR_URL
    def __init__(self, root, on_success):
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
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Generate a log file with de currente date
        date_now = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join("logs", f"{date_now}.log")
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
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def ensure_user_table(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT UNIQUE NOT NULL,
                        clave TEXT NOT NULL,
                        role TEXT NOT NULL DEFAULT 'Vendedor'
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS config (
                        clave TEXT PRIMARY KEY,
                        valor TEXT
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos",
                                 f"No se pudo inicializar la tabla de usuarios: {str(e)}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def center_window(self, width, height, window=None):
        if window is None:
            window = self.root
        window.update_idletasks()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def load_remembered_user(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('REPLACE INTO config (clave, valor) VALUES (?, ?)',
                               ('remembered_user', self.username_var.get().strip()))
                conn.commit()
        except sqlite3.Error:
            pass

    def clear_remembered_user(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM config WHERE clave = ?', ('remembered_user',))
                conn.commit()
        except sqlite3.Error:
            pass

    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')

    def create_widgets(self):
        login_frame = tk.Frame(self.root, bg="white", relief=tk.RIDGE, bd=0,
                               highlightbackground="#dfe6e9", highlightthickness=1)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=360)

        header_frame = tk.Frame(login_frame, bg="#3498db")
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Acceso al sistema", bg="#3498db", fg="white",
                 font=("Arial", 17, "bold")).pack(pady=(14, 4))
        tk.Label(header_frame, text="Facturas, clientes y productos en un solo lugar",
                 bg="#3498db", fg="#eef7ff", font=("Arial", 9)).pack(pady=(0, 14))

        tk.Label(login_frame, text="Ingrese sus datos para continuar", bg="white",
                 fg="#555", font=("Arial", 10)).pack(pady=(16, 14))

        tk.Label(login_frame, text="Usuario", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", padx=36)
        tk.Entry(login_frame, textvariable=self.username_var, font=("Arial", 10), width=32,
                 **INPUT_STYLE).pack(fill=tk.X, padx=36, pady=(4, 12))

        tk.Label(login_frame, text="Contraseña", font=("Arial", 10, "bold"), bg="white").pack(anchor="w", padx=36)
        self.password_entry = tk.Entry(login_frame, textvariable=self.password_var, font=("Arial", 10),
                                       show="*", width=32, **INPUT_STYLE)
        self.password_entry.pack(fill=tk.X, padx=36, pady=(4, 12))

        options_frame = tk.Frame(login_frame, bg="white")
        options_frame.pack(fill=tk.X, padx=34, pady=(0, 12))
        tk.Checkbutton(options_frame, text="Mostrar contraseña", variable=self.show_password_var,
                       bg="white", command=self.toggle_password_visibility).pack(side=tk.LEFT)
        tk.Checkbutton(options_frame, text="Recordar usuario", variable=self.remember_var,
                       bg="white").pack(side=tk.RIGHT)

        btn_frame = tk.Frame(login_frame, bg="white")
        btn_frame.pack(fill=tk.X, padx=36, pady=(4, 0))

        tk.Button(btn_frame, text="Entrar al sistema", command=self.login,
                 bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        tk.Button(btn_frame, text="Crear cuenta", command=self.open_register_window,
                 bg="#2ecc71", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        tk.Label(self.root, text="© 2026 K.A.R.M. • Facturación Fácil", font=("Arial", 8),
                 bg="#f0f0f0", fg="#555").pack(side=tk.BOTTOM, pady=10)

    def login(self):
        usuario = self.username_var.get().strip()
        clave = self.password_var.get().strip()
        if not usuario or not clave:
            messagebox.showwarning("Advertencia", "Ingrese usuario y contraseña")
            return

        hashed_clave = self.hash_password(clave)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT clave FROM usuarios WHERE usuario = ?', (usuario,))
                row = cursor.fetchone()
                if row and row[0] == hashed_clave:
                    if self.remember_var.get():
                        self.save_remembered_user()
                    else:
                        self.clear_remembered_user()
                    self.root.destroy()
                    self.on_success()
                else:
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

        tk.Label(register_window, text="Crear cuenta de acceso", font=("Arial", 17, "bold"),
                 bg="#f0f0f0", fg="#2d3436").pack(pady=(20, 6))
        tk.Label(register_window, text="Complete los datos. Luego podrá iniciar sesión con este usuario.", font=("Arial", 9),
                 bg="#f0f0f0", fg="#555").pack()

        form_frame = tk.Frame(register_window, bg="white", relief=tk.RIDGE, bd=0,
                              highlightbackground="#dfe6e9", highlightthickness=1)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        form_frame.columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Datos de la cuenta", font=("Arial", 13, "bold"),
                 bg="white", fg="#2d3436").grid(row=0, column=0, columnspan=2, sticky="w", padx=22, pady=(20, 14))

        tk.Label(form_frame, text="Usuario", font=("Arial", 10, "bold"), bg="white").grid(row=1, column=0, sticky="w", padx=22, pady=6)
        new_user_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=new_user_var, font=("Arial", 10), **INPUT_STYLE).grid(row=1, column=1, sticky="ew", padx=(0, 22), pady=6)

        tk.Label(form_frame, text="Contraseña", font=("Arial", 10, "bold"), bg="white").grid(row=2, column=0, sticky="w", padx=22, pady=6)
        new_password_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=new_password_var, font=("Arial", 10), show="*", **INPUT_STYLE).grid(row=2, column=1, sticky="ew", padx=(0, 22), pady=6)

        tk.Label(form_frame, text="Confirmar contraseña", font=("Arial", 10, "bold"), bg="white").grid(row=3, column=0, sticky="w", padx=22, pady=6)
        confirm_password_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=confirm_password_var, font=("Arial", 10), show="*", **INPUT_STYLE).grid(row=3, column=1, sticky="ew", padx=(0, 22), pady=6)

        tk.Label(form_frame, text="Tipo de usuario", font=("Arial", 10, "bold"), bg="white").grid(row=4, column=0, sticky="w", padx=22, pady=6)
        role_var = tk.StringVar(value="Vendedor")
        role_frame = tk.Frame(form_frame, bg="white")
        role_frame.grid(row=4, column=1, sticky="w", padx=(0, 22), pady=6)
        tk.Radiobutton(role_frame, text="Vendedor", variable=role_var, value="Vendedor",
                       bg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Radiobutton(role_frame, text="Administrador", variable=role_var, value="Administrador",
                       bg="white", font=("Arial", 10)).pack(side=tk.LEFT)

        tk.Label(form_frame, text="La contraseña debe tener mínimo 5 caracteres e incluir letras y números.",
                 font=("Arial", 9), bg="white", fg="#636e72").grid(row=5, column=0, columnspan=2, sticky="w", padx=22, pady=(8, 0))

        register_button = tk.Button(form_frame, text="Guardar cuenta", command=lambda: self.register_user(
            new_user_var.get().strip(), new_password_var.get().strip(), confirm_password_var.get().strip(), role_var.get(), register_window),
                 bg="#2ecc71", fg="white", font=("Arial", 10, "bold"),
                 width=24, cursor="hand2")
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

        hashed_clave = self.hash_password(clave)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM usuarios WHERE usuario = ?', (usuario,))
                if cursor.fetchone():
                    messagebox.showwarning("Advertencia", "El usuario ya existe")
                    return
                cursor.execute('INSERT INTO usuarios (usuario, clave, role) VALUES (?, ?, ?)',
                               (usuario, hashed_clave, role))
                conn.commit()
                messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente. Ahora puede iniciar sesión.")
                window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos",
                                 f"No se pudo crear el usuario: {str(e)}")

