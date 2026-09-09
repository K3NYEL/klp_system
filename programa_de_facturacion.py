import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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

CREATOR_URL = "https://github.com/K3NYEL"

INPUT_STYLE = {
    "bg": "#ffffff",
    "fg": "#2d3436",
    "insertbackground": "#2d3436",
    "relief": tk.FLAT,
    "highlightthickness": 2,
    "highlightbackground": "#8a8a8a",
    "highlightcolor": "#3498db",
}

def resource_path(filename):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename) # type: ignore
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

def set_app_icon(window, base_path=None):
    icon_path = resource_path("facturacion_ico.ico")
    if not os.path.exists(icon_path) and base_path:
        icon_path = os.path.join(base_path, "facturacion_ico.ico")
    if os.path.exists(icon_path):
        try:
            window.iconbitmap(default=icon_path)
        except tk.TclError:
            pass

def configure_app_style():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    
    class ThemeManager:
        THEMES = {
            'dark': {
                'bg_primary': '#2d3436',
                'bg_secondary': '#4a4a4a',
                'bg_card': '#34495e',
                'text_primary': '#ecf0f1',
                'accent': '#3498db',
                'success': '#27ae60',
                'danger': '#e74c3c'
            },
            'light': {
                'bg_primary': '#ecf0f1',
                'bg_secondary': '#d5dbdb',
                'bg_card': '#ffffff',
                'text_primary': '#2d3436',
                'accent': '#3498db',
                'success': '#27ae60',
                'danger': '#e74c3c'
            }
        }

        def __init__(self, root):
            self.root = root
            self.current_theme = 'dark'
            self.load_theme()
    
    def load_theme(self):
        self.apply_theme(self.current_theme)
    
    def apply_theme(self, theme_name):
        theme = self.THEMES[theme_name]
        self.current_theme = theme_name
        
        # Update root
        self.root.configure(bg=theme['bg_primary'])
        
        # Update ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=theme['bg_primary'])
        style.configure("TLabel", background=theme['bg_primary'], foreground=theme['text_primary'])
        style.configure("TNotebook", background=theme['bg_secondary'])
        style.configure("TNotebook.Tab", background=theme['bg_card'], foreground=theme['text_primary'])
        style.map("TNotebook.Tab", background=[("selected", theme['accent'])])
        style.configure("Treeview", background=theme['bg_card'], foreground=theme['text_primary'], fieldbackground=theme['bg_card'])
        style.configure("Treeview.Heading", background=theme['accent'], foreground=theme['text_primary'])
        style.map("Treeview", background=[("selected", theme['accent'])], foreground=[("selected", theme['bg_primary'])])
        style.configure("TEntry", fieldbackground=theme['bg_card'], foreground=theme['text_primary'])
        style.configure("TCombobox", fieldbackground=theme['bg_card'], foreground=theme['text_primary'])
        style.configure("Accent.TButton", background=theme['accent'], font=("Arial", 10, "bold"), foreground="white", padding=6)
        style.map("Accent.TButton", background=[("active", f"{theme['accent']}90")])
        style.configure("Secondary.TButton", background=theme['success'], font=("Arial", 10, "bold"), foreground="white", padding=6)
        style.configure("Danger.TButton", background=theme['danger'], font=("Arial", 10, "bold"), foreground="white", padding=6)

    def toggle_theme(self):
        new_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme(new_theme)

    def configure_app_style():
        style = ttk.Style()
    # Usamos el tema 'clam' para que permita personalizar mejor las pestañas
        style.theme_use('clam') 

    # Configuración de las pestañas (Tabs)
        style.configure("TNotebook.Tab",
                        font=("Arial", 12, "bold"), # Aumenta el tamaño de letra
                        padding=[20, 10],            # [Ancho, Alto] internos de la pestaña
                        background="#e1e1e1",        # Color de fondo cuando no está seleccionada
                        foreground="#333333")        # Color de letra

    # Estilo de la pestaña cuando está seleccionada (activa)
        style.map("TNotebook.Tab",
                background=[("selected", "#3b82f6")], # Fondo azul al hacer clic
                foreground=[("selected", "white")])   # Letra blanca al hacer clic

        style.configure("Secondary.TButton",
                    font=("Arial", 10, "bold"),
                    # ... resto de tu configuración ...
                    foreground="white",
                    background="#2ecc71",
                    padding=6)
        style.map("Secondary.TButton",
              background=[("active", "#27ae60"), ("pressed", "#1e8449")])

        style.configure("Danger.TButton",
                    font=("Arial", 10, "bold"),
                    foreground="white",
                    background="#e74c3c",
                    padding=6)

        style.configure("TNotebook",
                    background="#f0f0f0",
                    tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab",
                    font=("Arial", 11, "bold"),
                    padding=[12, 8],
                    background="#dfe6e9",
                    foreground="#2d3436")
        style.map("TNotebook.Tab",
              background=[("selected", "#74b9ff"), ("!disabled", "#dfe6e9")],
              foreground=[("selected", "#2d3436")])

        style.configure("Treeview",
                    font=("Arial", 10),
                    rowheight=26,
                    fieldbackground="#ffffff",
                    background="#ffffff",
                    foreground="#2d3436")
        style.configure("Treeview.Heading",
                    font=("Arial", 10, "bold"),
                    background="#0984e3",
                    foreground="white")
        style.map("Treeview",
              background=[("selected", "#74b9ff")],
              foreground=[("selected", "black")])

        style.configure("TLabel", background="#f0f0f0")
        style.configure("TCombobox", fieldbackground="#ffffff", background="#ffffff")
        style.configure("TEntry",
                    fieldbackground="#ffffff",
                    foreground="#2d3436",
                    bordercolor="#8a8a8a",
                    lightcolor="#3498db",
                    darkcolor="#8a8a8a",
                    padding=4)

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

class SistemaFacturacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Facturacion")
        self.base_path = self.get_base_path()
        set_app_icon(self.root, self.base_path)
        self.root.geometry("1200x700")
        self.root.geometry("1920x1080")
        self.root.state('zoomed')
        self.root.configure(bg="#f0f0f0")
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
        """Inicializa la base de datos SQLite"""
        try:
            # Conectar a la base de datos usando la ruta del ejecutable
            db_path = os.path.join(self.base_path, 'facturacion.db')
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            
            # Tabla de productos
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL,
                    stock INTEGER DEFAULT 0
                )
            ''')
            
            # Tabla de clientes
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    cedula TEXT UNIQUE,
                    telefono TEXT,
                    direccion TEXT
                )
            ''')
            
            # Tabla de facturas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS facturas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT UNIQUE,
                    fecha TEXT,
                    cliente_id INTEGER,
                    subtotal REAL,
                    itbis REAL,
                    total REAL,
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id)
                )
            ''')
            
            # Tabla de items de factura
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS factura_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    factura_id INTEGER,
                    producto_id INTEGER,
                    cantidad INTEGER,
                    precio_unitario REAL,
                    subtotal REAL,
                    FOREIGN KEY (factura_id) REFERENCES facturas (id),
                    FOREIGN KEY (producto_id) REFERENCES productos (id)
                )
            ''')

            # Tabla de configuración de la empresa
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS empresa (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT,
                    rnc TEXT,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    website TEXT
                )
            ''')
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", 
                               f"Error al inicializar la base de datos: {str(e)}")
            if hasattr(self, 'conn'):
                self.conn.close()
            raise

    def get_base_path(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def center_window(self, width, height, window=None):
        if window is None:
            window = self.root
        window.update_idletasks()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def crear_pestaña_admin(self):
        """Crea la pestaña de configuración de la empresa"""
        tab = tk.Frame(self.root, bg="white")
        self.empresa_tab = tab
        
        form_frame = tk.Frame(tab, bg="white", relief=tk.RIDGE, bd=2)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(form_frame, text="Datos que aparecerán en la factura", font=("Arial", 14, "bold"),
                bg="white").grid(row=0, column=0, columnspan=2, pady=10)
        
        tk.Label(form_frame, text="Nombre de la empresa:", bg="white", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.empresa_nombre_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.empresa_nombre_var, width=50, font=("Arial", 10)).grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(form_frame, text="RNC:", bg="white", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.empresa_rnc_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.empresa_rnc_var, width=30, font=("Arial", 10)).grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        tk.Label(form_frame, text="Dirección:", bg="white", font=("Arial", 10)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.empresa_direccion_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.empresa_direccion_var, width=50, font=("Arial", 10)).grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(form_frame, text="Teléfono:", bg="white", font=("Arial", 10)).grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.empresa_telefono_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.empresa_telefono_var, width=30, font=("Arial", 10)).grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        tk.Label(form_frame, text="Email:", bg="white", font=("Arial", 10)).grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.empresa_email_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.empresa_email_var, width=50, font=("Arial", 10)).grid(row=5, column=1, padx=10, pady=5)
        
        tk.Label(form_frame, text="Sitio web:", bg="white", font=("Arial", 10)).grid(row=6, column=0, padx=10, pady=5, sticky="e")
        self.empresa_website_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.empresa_website_var, width=50, font=("Arial", 10)).grid(row=6, column=1, padx=10, pady=5)
        
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Guardar empresa", command=self.guardar_empresa,
                 bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                 width=24, cursor="hand2").pack()

    def cargar_empresa(self):
        self.cursor.execute('SELECT nombre, rnc, direccion, telefono, email, website FROM empresa WHERE id = 1')
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
        nombre = self.empresa_nombre_var.get().strip()
        rnc = self.empresa_rnc_var.get().strip()
        direccion = self.empresa_direccion_var.get().strip()
        telefono = self.empresa_telefono_var.get().strip()
        email = self.empresa_email_var.get().strip()
        website = self.empresa_website_var.get().strip()

        self.cursor.execute('SELECT id FROM empresa WHERE id = 1')
        if self.cursor.fetchone():
            self.cursor.execute('''
                UPDATE empresa
                SET nombre=?, rnc=?, direccion=?, telefono=?, email=?, website=?
                WHERE id = 1
            ''', (nombre, rnc, direccion, telefono, email, website))
        else:
            self.cursor.execute('''
                INSERT INTO empresa (id, nombre, rnc, direccion, telefono, email, website)
                VALUES (1, ?, ?, ?, ?, ?, ?)
            ''', (nombre, rnc, direccion, telefono, email, website))

        self.conn.commit()
        messagebox.showinfo("Éxito", "Información de la empresa guardada correctamente")

    def crear_interfaz(self):
        """Crea la interfaz principal con pestañas"""
        menu_bar = tk.Menu(self.root)
        archivo_menu = tk.Menu(menu_bar, tearoff=0)
        archivo_menu.add_command(label="Cerrar sesión", command=self.cerrar_sesion)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.salir)
        menu_bar.add_cascade(label="Archivo", menu=archivo_menu)

        ayuda_menu = tk.Menu(menu_bar, tearoff=0)
        ayuda_menu.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        menu_bar.add_cascade(label="Ayuda", menu=ayuda_menu)

        self.root.config(menu=menu_bar)

        access_frame = tk.Frame(self.root, relief=tk.FLAT)
        access_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        tk.Label(access_frame, text="Accesos rápidos", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=12, pady=6)

        tk.Button(access_frame, text="Inicio de sesión", command=self.cerrar_sesion,
                  bg="#0984e3", fg="white", activebackground="#0878cc",
                  activeforeground="white", font=("Arial", 9, "bold"),
                  cursor="hand2", relief=tk.FLAT, padx=12).pack(side=tk.RIGHT, padx=(4, 8), pady=4)

        tk.Button(access_frame, text="Mi Empresa", command=self.ir_mi_empresa,
                  bg="#00b894", fg="white", activebackground="#00a383",
                  activeforeground="white", font=("Arial", 9, "bold"),
                  cursor="hand2", relief=tk.FLAT, padx=12).pack(side=tk.RIGHT, padx=4, pady=4)

        tk.Button(access_frame, text="Acerca de", command=self.mostrar_acerca_de,
                  bg="#636e72", fg="white", activebackground="#4f5b60",
                  activeforeground="white", font=("Arial", 9, "bold"),
                  cursor="hand2", relief=tk.FLAT, padx=12).pack(side=tk.RIGHT, padx=4, pady=4)

        header_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.RIDGE, bd=1)
        header_frame.pack(fill=tk.X, padx=10, pady=(6, 0))
        title_frame = tk.Frame(header_frame, bg="#ffffff")
        title_frame.pack(side=tk.LEFT, padx=18, pady=12)
        tk.Label(title_frame, text="Sistema de Facturación", font=("Arial", 22, "bold"),
                 bg="#ffffff", fg="#2d3436").pack(anchor="w")
        tk.Label(title_frame, text="Nueva factura, productos, clientes e historial desde una sola pantalla",
                 font=("Arial", 10), bg="#ffffff", fg="#636e72").pack(anchor="w", pady=(2, 0))

        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        self.crear_pestaña_facturacion()
        self.crear_pestaña_productos()
        self.crear_pestaña_clientes()
        self.crear_pestaña_admin()
        self.crear_pestaña_historial()

        tk.Label(self.root, text="Facturación App • K.A.R.M. • Versión 1.0", bg="#f0f0f0",
                 fg="#555", font=("Arial", 8)).pack(side=tk.BOTTOM, pady=6)

    def ir_mi_empresa(self):
        empresa_win = tk.Toplevel(self.root)
        empresa_win.title("Mi Empresa")
        set_app_icon(empresa_win, self.base_path)
        empresa_win.geometry("640x420")
        empresa_win.configure(bg="#f0f0f0")
        empresa_win.transient(self.root)
        empresa_win.grab_set()
        self.center_window(640, 420, window=empresa_win)

        container = tk.Frame(empresa_win, bg="white", relief=tk.RIDGE, bd=0,
                             highlightbackground="#dfe6e9", highlightthickness=1)
        container.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)
        container.columnconfigure(1, weight=1)

        tk.Label(container, text="Datos de mi empresa", font=("Arial", 16, "bold"),
                 bg="white", fg="#2d3436").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(18, 12))

        fields = [
            ("Nombre de la empresa", self.empresa_nombre_var),
            ("RNC", self.empresa_rnc_var),
            ("Dirección", self.empresa_direccion_var),
            ("Teléfono", self.empresa_telefono_var),
            ("Email", self.empresa_email_var),
            ("Sitio web", self.empresa_website_var),
        ]

        for index, (label, variable) in enumerate(fields, start=1):
            tk.Label(container, text=label, bg="white", font=("Arial", 10, "bold")).grid(
                row=index, column=0, padx=20, pady=6, sticky="w"
            )
            tk.Entry(container, textvariable=variable, font=("Arial", 10), **INPUT_STYLE).grid(
                row=index, column=1, padx=(0, 20), pady=6, sticky="ew"
            )

        btn_frame = tk.Frame(container, bg="white")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=(18, 16))

        tk.Button(btn_frame, text="Guardar datos", command=self.guardar_empresa,
                 bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                 width=18, cursor="hand2").pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Cerrar", command=empresa_win.destroy,
                 bg="#95a5a6", fg="white", font=("Arial", 10, "bold"),
                 width=12, cursor="hand2").pack(side=tk.LEFT, padx=6)
        
    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Desea cerrar sesión y volver al login?"):
            self.root.destroy()
            login_root = tk.Tk()
            LoginWindow(login_root, on_success=start_main_app)
            login_root.mainloop()

    def salir(self):
        if messagebox.askyesno("Salir", "¿Desea salir del sistema?"):
            self.root.destroy()

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

        tk.Label(about, text="Sistema de Facturación", font=("Arial", 14, "bold"),
                 bg="#f0f0f0").pack(pady=(20, 8))
        tk.Label(about, text="Versión 1.0\nDesarrollado por K.A.R.M.", font=("Arial", 10),
                 bg="#f0f0f0", fg="#555").pack()

        link = tk.Label(about, text=CREATOR_URL, font=("Arial", 10, "underline"),
                       fg="#0984e3", bg="#f0f0f0", cursor="hand2")
        link.pack(pady=12)
        link.bind("<Button-1>", lambda event: webbrowser.open_new_tab(CREATOR_URL))

        tk.Button(about, text="Cerrar", command=about.destroy,
                 bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                 activebackground="#2980b9", activeforeground="white",
                 width=12, cursor="hand2", relief=tk.FLAT).pack(pady=(10, 16))

    def crear_pestaña_facturacion(self):
        """Crea la pestaña de facturación"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="  Crear Factura  ")

        # Canvas con scrollbar que envuelve todo
        main_canvas = tk.Canvas(tab, bg="white", highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(tab, orient="vertical", command=main_canvas.yview)
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
        unified_frame = tk.LabelFrame(inner, text="  Factura  ", bg="white",
                                      fg="#2d3436", font=("Arial", 11, "bold"), padx=10, pady=8)
        unified_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        unified_frame.columnconfigure(1, weight=1)
        unified_frame.columnconfigure(3, weight=1)

        # --- Datos del comprobante ---
        tk.Label(unified_frame, text="Factura No.", font=("Arial", 10, "bold"),
                bg="white").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.num_factura = tk.StringVar(value=self.generar_numero_factura())
        tk.Entry(unified_frame, textvariable=self.num_factura, state="readonly",
                width=20, font=("Arial", 10)).grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(unified_frame, text="Fecha", font=("Arial", 10, "bold"),
                bg="white").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.fecha_factura = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        tk.Entry(unified_frame, textvariable=self.fecha_factura, state="readonly",
                width=15, font=("Arial", 10)).grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        tk.Label(unified_frame, text="Cliente", font=("Arial", 10, "bold"),
                bg="white").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.cliente_var = tk.StringVar()
        self.combo_cliente = ttk.Combobox(unified_frame, textvariable=self.cliente_var,
                                         width=40, font=("Arial", 10))
        self.combo_cliente.grid(row=1, column=1, columnspan=3, padx=10, pady=5, sticky="ew")

        # Separador
        ttk.Separator(unified_frame, orient="horizontal").grid(row=2, column=0, columnspan=4,
                                                                sticky="ew", padx=5, pady=6)

        # --- Agregar producto ---
        tk.Label(unified_frame, text="Producto", bg="white",
                font=("Arial", 10, "bold")).grid(row=3, column=0, padx=5, pady=5)
        self.producto_var = tk.StringVar()
        self.combo_producto = ttk.Combobox(unified_frame, textvariable=self.producto_var,
                                          width=35, font=("Arial", 10))
        self.combo_producto.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.combo_producto.bind('<<ComboboxSelected>>', self.seleccionar_producto)

        tk.Label(unified_frame, text="Precio", bg="white",
                font=("Arial", 10, "bold")).grid(row=3, column=2, padx=5, pady=5)
        self.precio_var = tk.StringVar()
        tk.Entry(unified_frame, textvariable=self.precio_var, width=12,
                font=("Arial", 10)).grid(row=3, column=3, padx=5, pady=5, sticky="w")

        tk.Label(unified_frame, text="Cantidad", bg="white",
                font=("Arial", 10, "bold")).grid(row=4, column=0, padx=5, pady=5)
        self.cantidad_var = tk.StringVar(value="1")
        tk.Entry(unified_frame, textvariable=self.cantidad_var, width=10,
                font=("Arial", 10)).grid(row=4, column=1, padx=5, pady=5, sticky="w")

        tk.Button(unified_frame, text="Agregar producto", command=self.agregar_item,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2").grid(row=4, column=3, padx=10, pady=5, sticky="e")

        # Separador
        ttk.Separator(unified_frame, orient="horizontal").grid(row=5, column=0, columnspan=4,
                                                                sticky="ew", padx=5, pady=6)

        # --- Tabla de productos ---
        table_frame = tk.Frame(unified_frame, bg="white")
        table_frame.grid(row=6, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        table_frame.columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview para items
        self.tree_items = ttk.Treeview(table_frame, columns=("Código", "Producto", "Cantidad", "Precio", "Subtotal"),
                                       show="headings", height=2, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree_items.yview)

        self.tree_items.heading("Código", text="Código")
        self.tree_items.heading("Producto", text="Producto")
        self.tree_items.heading("Cantidad", text="Cantidad")
        self.tree_items.heading("Precio", text="Precio Unit.")
        self.tree_items.heading("Subtotal", text="Subtotal")

        self.tree_items.column("Código", width=100)
        self.tree_items.column("Producto", width=300)
        self.tree_items.column("Cantidad", width=100)
        self.tree_items.column("Precio", width=100)
        self.tree_items.column("Subtotal", width=120)

        self.tree_items.pack(fill=tk.X)

        # Separador
        ttk.Separator(unified_frame, orient="horizontal").grid(row=7, column=0, columnspan=4,
                                                                sticky="ew", padx=5, pady=6)

        # --- Totales en fila horizontal ---
        totals_row = tk.Frame(unified_frame, bg="white")
        totals_row.grid(row=8, column=0, columnspan=4, sticky="w", padx=10, pady=5)

        tk.Label(totals_row, text="Subtotal:", font=("Arial", 11, "bold"), bg="white").pack(side=tk.LEFT, padx=(0, 4))
        self.subtotal_var = tk.StringVar(value="RD$ 0.00")
        tk.Label(totals_row, textvariable=self.subtotal_var, font=("Arial", 11), bg="white").pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(totals_row, text="ITBIS (18%):", font=("Arial", 11, "bold"), bg="white").pack(side=tk.LEFT, padx=(0, 4))
        self.itbis_var = tk.StringVar(value="RD$ 0.00")
        tk.Label(totals_row, textvariable=self.itbis_var, font=("Arial", 11), bg="white").pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(totals_row, text="TOTAL:", font=("Arial", 13, "bold"), bg="white", fg="#27ae60").pack(side=tk.LEFT, padx=(0, 4))
        self.total_var = tk.StringVar(value="RD$ 0.00")
        tk.Label(totals_row, textvariable=self.total_var, font=("Arial", 13, "bold"), bg="white", fg="#27ae60").pack(side=tk.LEFT)

        # --- Botones ---
        btn_frame = tk.Frame(unified_frame, bg="white")
        btn_frame.grid(row=9, column=0, columnspan=4, pady=10)

        tk.Button(btn_frame, text="Guardar factura y crear PDF", command=self.generar_factura,
                 bg="#3498db", fg="white", font=("Arial", 11, "bold"),
                 width=25, height=2, cursor="hand2").pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="Limpiar y hacer otra factura", command=self.nueva_factura,
                 bg="#95a5a6", fg="white", font=("Arial", 11, "bold"),
                 width=26, height=2, cursor="hand2").pack(side=tk.LEFT, padx=10)
        
    def crear_pestaña_productos(self):
        """Crea la pestaña de gestión de productos"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="  Inventario  ")
        
        # Frame para formulario
        form_frame = tk.Frame(tab, bg="white", relief=tk.RIDGE, bd=2)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(form_frame, text="Inventario de productos", font=("Arial", 14, "bold"),
                bg="white").grid(row=0, column=0, columnspan=4, pady=10)
        
        # Campos del formulario
        tk.Label(form_frame, text="Código:", bg="white", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.prod_codigo = tk.Entry(form_frame, width=20, font=("Arial", 10))
        self.prod_codigo.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(form_frame, text="Nombre:", bg="white", font=("Arial", 10)).grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.prod_nombre = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.prod_nombre.grid(row=1, column=3, padx=10, pady=5)
        
        tk.Label(form_frame, text="Precio:", bg="white", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.prod_precio = tk.Entry(form_frame, width=20, font=("Arial", 10))
        self.prod_precio.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(form_frame, text="Stock:", bg="white", font=("Arial", 10)).grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.prod_stock = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.prod_stock.grid(row=2, column=3, padx=10, pady=5)
        
        # Botones
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        tk.Button(btn_frame, text="Agregar", command=self.agregar_producto,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 width=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Actualizar", command=self.actualizar_producto,
                 bg="#f39c12", fg="white", font=("Arial", 10, "bold"),
                 width=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Eliminar", command=self.eliminar_producto,
                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                 width=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Limpiar", command=self.limpiar_form_producto,
                 bg="#95a5a6", fg="white", font=("Arial", 10, "bold"),
                 width=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Frame para búsqueda
        search_frame = tk.Frame(tab, bg="white")
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="Buscar por código o nombre:", bg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.prod_buscar = tk.Entry(search_frame, width=40, font=("Arial", 10))
        self.prod_buscar.pack(side=tk.LEFT, padx=5)
        self.prod_buscar.bind('<KeyRelease>', lambda e: self.cargar_productos())
        
        # Frame para tabla
        table_frame = tk.Frame(tab, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_productos = ttk.Treeview(table_frame, columns=("ID", "Código", "Nombre", "Precio", "Stock"),
                                          show="headings", yscrollcommand=scrollbar.set)
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
        self.tree_productos.bind('<ButtonRelease-1>', self.seleccionar_producto_tabla)
        
    def crear_pestaña_clientes(self):
        """Crea la pestaña de gestión de clientes"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="  Clientes  ")
        
        # Frame para formulario
        form_frame = tk.Frame(tab, bg="white", relief=tk.RIDGE, bd=2)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(form_frame, text="Registro de clientes", font=("Arial", 14, "bold"),
                bg="white").grid(row=0, column=0, columnspan=4, pady=10)
        
        # Campos del formulario
        tk.Label(form_frame, text="Nombre:", bg="white", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.cli_nombre = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.cli_nombre.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(form_frame, text="Cédula:", bg="white", font=("Arial", 10)).grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.cli_cedula = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.cli_cedula.grid(row=1, column=3, padx=10, pady=5)
        
        tk.Label(form_frame, text="Teléfono:", bg="white", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.cli_telefono = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.cli_telefono.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(form_frame, text="Dirección:", bg="white", font=("Arial", 10)).grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.cli_direccion = tk.Entry(form_frame, width=30, font=("Arial", 10))
        self.cli_direccion.grid(row=2, column=3, padx=10, pady=5)
        
        # Botones
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        tk.Button(btn_frame, text="Agregar", command=self.agregar_cliente,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 width=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Actualizar", command=self.actualizar_cliente,
                 bg="#f39c12", fg="white", font=("Arial", 10, "bold"),
                 width=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Eliminar", command=self.eliminar_cliente,
                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                 width=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Limpiar", command=self.limpiar_form_cliente,
                 bg="#95a5a6", fg="white", font=("Arial", 10, "bold"),
                 width=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Frame para búsqueda
        search_frame = tk.Frame(tab, bg="white")
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="Buscar por nombre o cédula:", bg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.cli_buscar = tk.Entry(search_frame, width=40, font=("Arial", 10))
        self.cli_buscar.pack(side=tk.LEFT, padx=5)
        self.cli_buscar.bind('<KeyRelease>', lambda e: self.cargar_clientes())
        
        # Frame para tabla
        table_frame = tk.Frame(tab, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_clientes = ttk.Treeview(table_frame, columns=("ID", "Nombre", "Cédula", "Teléfono", "Dirección"),
                                         show="headings", yscrollcommand=scrollbar.set)
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
        self.tree_clientes.bind('<ButtonRelease-1>', self.seleccionar_cliente_tabla)
        
    def crear_pestaña_historial(self):
        """Crea la pestaña de historial de facturas"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="  Facturas guardadas  ")
        
        # Frame para búsqueda
        search_frame = tk.Frame(tab, bg="white")
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="Buscar factura o cliente:", bg="white", 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.hist_buscar = tk.Entry(search_frame, width=30, font=("Arial", 10))
        self.hist_buscar.pack(side=tk.LEFT, padx=5)
        self.hist_buscar.bind('<KeyRelease>', lambda e: self.cargar_historial())
        
        tk.Button(search_frame, text="Ver detalles", command=self.ver_detalles_factura,
                 bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(search_frame, text="Crear PDF de nuevo", command=self.regenerar_pdf,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Frame para tabla
        table_frame = tk.Frame(tab, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_historial = ttk.Treeview(table_frame, 
                                          columns=("ID", "Número", "Fecha", "Cliente", "Subtotal", "ITBIS", "Total"),
                                          show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree_historial.yview)
        
        self.tree_historial.heading("ID", text="ID")
        self.tree_historial.heading("Número", text="Número")
        self.tree_historial.heading("Fecha", text="Fecha")
        self.tree_historial.heading("Cliente", text="Cliente")
        self.tree_historial.heading("Subtotal", text="Subtotal")
        self.tree_historial.heading("ITBIS", text="ITBIS")
        self.tree_historial.heading("Total", text="Total")
        
        self.tree_historial.column("ID", width=50)
        self.tree_historial.column("Número", width=120)
        self.tree_historial.column("Fecha", width=100)
        self.tree_historial.column("Cliente", width=250)
        self.tree_historial.column("Subtotal", width=100)
        self.tree_historial.column("ITBIS", width=100)
        self.tree_historial.column("Total", width=100)
        
        self.tree_historial.pack(fill=tk.BOTH, expand=True)
        
    # Métodos de Productos
    def agregar_producto(self):
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
            
            self.cursor.execute('''
                INSERT INTO productos (codigo, nombre, precio, stock)
                VALUES (?, ?, ?, ?)
            ''', (codigo, nombre, precio, stock))
            
            self.conn.commit()
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
        selected = self.tree_productos.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto de la tabla")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?"):
            item = self.tree_productos.item(selected[0])
            producto_id = item['values'][0]
            
            try:
                self.cursor.execute('DELETE FROM productos WHERE id=?', (producto_id,))
                self.conn.commit()
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
            values = item['values']
            
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
        
        buscar = self.prod_buscar.get().strip()
        
        if buscar:
            self.cursor.execute('''
                SELECT * FROM productos 
                WHERE codigo LIKE ? OR nombre LIKE ?
                ORDER BY nombre
            ''', (f'%{buscar}%', f'%{buscar}%'))
        else:
            self.cursor.execute('SELECT * FROM productos ORDER BY nombre')
        
        for row in self.cursor.fetchall():
            self.tree_productos.insert('', tk.END, values=row)
            
    # Métodos de Clientes
    def agregar_cliente(self):
        nombre = self.cli_nombre.get().strip()
        cedula = self.cli_cedula.get().strip()
        telefono = self.cli_telefono.get().strip()
        direccion = self.cli_direccion.get().strip()
        
        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO clientes (nombre, cedula, telefono, direccion)
                VALUES (?, ?, ?, ?)
            ''', (nombre, cedula, telefono, direccion))
            
            self.conn.commit()
            messagebox.showinfo("Éxito", "Cliente agregado correctamente")
            self.limpiar_form_cliente()
            self.cargar_clientes()
            self.cargar_datos()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "La cédula ya está registrada")
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar cliente: {str(e)}")
            
    def actualizar_cliente(self):
        selected = self.tree_clientes.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un cliente de la tabla")
            return
        
        item = self.tree_clientes.item(selected[0])
        cliente_id = item['values'][0]
        
        nombre = self.cli_nombre.get().strip()
        cedula = self.cli_cedula.get().strip()
        telefono = self.cli_telefono.get().strip()
        direccion = self.cli_direccion.get().strip()
        
        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        try:
            self.cursor.execute('''
                UPDATE clientes 
                SET nombre=?, cedula=?, telefono=?, direccion=?
                WHERE id=?
            ''', (nombre, cedula, telefono, direccion, cliente_id))
            
            self.conn.commit()
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
            self.limpiar_form_cliente()
            self.cargar_clientes()
            self.cargar_datos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar cliente: {str(e)}")
            
    def eliminar_cliente(self):
        selected = self.tree_clientes.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un cliente de la tabla")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este cliente?"):
            item = self.tree_clientes.item(selected[0])
            cliente_id = item['values'][0]
            
            try:
                self.cursor.execute('DELETE FROM clientes WHERE id=?', (cliente_id,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
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
        selected = self.tree_productos.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto de la tabla")
            return
        
        item = self.tree_productos.item(selected[0])
        producto_id = item['values'][0]
        
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
            
            self.cursor.execute('''
                UPDATE productos 
                SET codigo=?, nombre=?, precio=?, stock=?
                WHERE id=?
            ''', (codigo, nombre, precio, stock, producto_id))
            
            self.conn.commit()
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
            values = item['values']
            
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
        
        buscar = self.cli_buscar.get().strip()
        
        if buscar:
            self.cursor.execute('''
                SELECT * FROM clientes 
                WHERE nombre LIKE ? OR cedula LIKE ?
                ORDER BY nombre
            ''', (f'%{buscar}%', f'%{buscar}%'))
        else:
            self.cursor.execute('SELECT * FROM clientes ORDER BY nombre')
        
        for row in self.cursor.fetchall():
            self.tree_clientes.insert('', tk.END, values=row)
            
    # Métodos de Facturación
    def generar_numero_factura(self):
        self.cursor.execute('SELECT MAX(id) FROM facturas')
        result = self.cursor.fetchone()[0]
        numero = 1 if result is None else result + 1
        return f"FAC-{numero:05d}"
        
    def seleccionar_producto(self, event):
        producto_str = self.producto_var.get()
        if not producto_str:
            return
        
        # Extraer código del producto (formato: "CODIGO - Nombre")
        codigo = producto_str.split(' - ')[0]
        
        self.cursor.execute('SELECT precio FROM productos WHERE codigo=?', (codigo,))
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
            if ' - ' not in producto_str:
                raise ValueError("Seleccione un producto válido de la lista")
            
            codigo, nombre = producto_str.split(' - ', 1)
            
            # Verificar stock disponible
            self.cursor.execute('SELECT stock FROM productos WHERE codigo = ?', (codigo,))
            stock_actual = self.cursor.fetchone()
            if not stock_actual:
                raise ValueError("Producto no encontrado")
            if stock_actual[0] < cantidad:
                raise ValueError(f"Stock insuficiente. Disponible: {stock_actual[0]}")
            
            subtotal = precio * cantidad
            
            # Agregar a la tabla
            self.tree_items.insert('', tk.END, 
                                values=(codigo, nombre, cantidad, f"RD$ {precio:.2f}", f"RD$ {subtotal:.2f}"))
            
            # Agregar a lista interna
            self.items_factura.append({
                'codigo': codigo,
                'nombre': nombre,
                'cantidad': cantidad,
                'precio': precio,
                'subtotal': subtotal
            })
            
            # Actualizar totales
            self.actualizar_totales()
            
            # Limpiar campos
            self.producto_var.set('')
            self.precio_var.set('')
            self.cantidad_var.set('1')
            
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
        
    def actualizar_totales(self):
        subtotal = sum(item['subtotal'] for item in self.items_factura)
        itbis = subtotal * 0.18
        total = subtotal + itbis
        
        self.subtotal_var.set(f"RD$ {subtotal:.2f}")
        self.itbis_var.set(f"RD$ {itbis:.2f}")
        self.total_var.set(f"RD$ {total:.2f}")
        
    def generar_factura(self):
        if not self.items_factura:
            messagebox.showwarning("Advertencia", "Agregue al menos un producto a la factura")
            return
        
        cliente_str = self.cliente_var.get()
        if not cliente_str:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return
        
        try:
            # Obtener ID del cliente
            cliente_cedula = cliente_str.split(' - ')[1] if ' - ' in cliente_str else None
            
            if cliente_cedula:
                self.cursor.execute('SELECT id FROM clientes WHERE cedula=?', (cliente_cedula,))
            else:
                self.cursor.execute('SELECT id FROM clientes WHERE nombre=?', (cliente_str,))
            
            result = self.cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Cliente no encontrado")
                return
            
            cliente_id = result[0]
            
            # Calcular totales
            subtotal = sum(item['subtotal'] for item in self.items_factura)
            itbis = subtotal * 0.18
            total = subtotal + itbis
            
            # Insertar factura
            numero = self.num_factura.get()
            fecha = datetime.now().strftime("%Y-%m-%d")
            
            self.cursor.execute('''
                INSERT INTO facturas (numero, fecha, cliente_id, subtotal, itbis, total)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (numero, fecha, cliente_id, subtotal, itbis, total))
            
            factura_id = self.cursor.lastrowid
            
            # Insertar items de la factura
            for item in self.items_factura:
                # Obtener ID del producto
                self.cursor.execute('SELECT id FROM productos WHERE codigo=?', (item['codigo'],))
                producto_id = self.cursor.fetchone()[0]
                
                self.cursor.execute('''
                    INSERT INTO factura_items (factura_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (factura_id, producto_id, item['cantidad'], item['precio'], item['subtotal']))
                
                # Actualizar stock
                self.cursor.execute('''
                    UPDATE productos 
                    SET stock = stock - ?
                    WHERE id = ?
                ''', (item['cantidad'], producto_id))
            
            self.conn.commit()
            
            # Generar PDF
            self.generar_pdf(factura_id)
            
            messagebox.showinfo("Éxito", f"Factura {numero} generada correctamente\nPDF guardado exitosamente")
            
            # Limpiar y preparar nueva factura
            self.nueva_factura()
            self.cargar_historial()
            self.cargar_productos()
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al generar factura: {str(e)}")
            
    def generar_pdf(self, factura_id):
        try:
            self.cursor.execute('''
                SELECT f.numero, f.fecha, f.subtotal, f.itbis, f.total,
                       c.nombre, c.cedula, c.telefono, c.direccion
                FROM facturas f
                JOIN clientes c ON f.cliente_id = c.id
                WHERE f.id = ?
            ''', (factura_id,))
            factura_data = self.cursor.fetchone()
            if not factura_data:
                raise ValueError("Factura no encontrada")

            self.cursor.execute('''
                SELECT p.codigo, p.nombre, fi.cantidad, fi.precio_unitario, fi.subtotal
                FROM factura_items fi
                JOIN productos p ON fi.producto_id = p.id
                WHERE fi.factura_id = ?
            ''', (factura_id,))
            items_data = self.cursor.fetchall()
            if not items_data:
                raise ValueError("La factura no tiene items")

            self.cursor.execute('''
                SELECT nombre, rnc, direccion, telefono, email, website
                FROM empresa
                WHERE id = 1
            ''')
            empresa_row = self.cursor.fetchone()
            if empresa_row:
                empresa_nombre, empresa_rnc, empresa_direccion, empresa_telefono, empresa_email, empresa_website = empresa_row
            else:
                empresa_nombre, empresa_rnc, empresa_direccion, empresa_telefono, empresa_email, empresa_website = (
                    "TU EMPRESA S.A.", "000-00000-0", "Tu dirección aquí", "(809) 000-0000", "", ""
                )

            empresa_nombre = empresa_nombre or "TU EMPRESA S.A."
            empresa_rnc = empresa_rnc or "000-00000-0"
            empresa_direccion = empresa_direccion or "Tu dirección aquí"
            empresa_email = empresa_email or "example@gmail.com"
            empresa_telefono = empresa_telefono or "(809) 000-0000"

            facturas_dir = os.path.join(self.base_path, 'facturas')
            try:
                os.makedirs(facturas_dir, exist_ok=True)
            except OSError as e:
                raise RuntimeError(f"No se pudo crear la carpeta de facturas: {str(e)}")

            filename = os.path.join(facturas_dir, f"{factura_data[0]}.pdf")
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='InvoiceTitle', fontSize=18, leading=22, alignment=1, spaceAfter=10, fontName='Helvetica-Bold'))
            styles.add(ParagraphStyle(name='InvoiceHeader', fontSize=11, leading=14, spaceAfter=8))
            styles.add(ParagraphStyle(name='Footer', fontSize=8, leading=10, alignment=1, textColor=colors.grey))

            titulo = Paragraph("FACTURA", styles['InvoiceTitle'])
            elements.append(titulo)
            elements.append(Spacer(1, 0.2*inch))

            empresa_text = f"<b>{empresa_nombre}</b><br/>RNC: {empresa_rnc}<br/>Dirección: {empresa_direccion}<br/>Teléfono: {empresa_telefono}"
            if empresa_email:
                empresa_text += f"<br/>Email: {empresa_email}"
            if empresa_website:
                empresa_text += f"<br/>Web: {empresa_website}"

            empresa_info = Paragraph(empresa_text, styles['Normal'])
            elements.append(empresa_info)
            elements.append(Spacer(1, 0.3*inch))

            info_data = [
                ['Factura No.:', factura_data[0], 'Fecha:', factura_data[1]],
                ['Cliente:', factura_data[5], 'Cédula:', factura_data[6] or 'N/A'],
                ['Teléfono:', factura_data[7] or 'N/A', 'Dirección:', factura_data[8] or 'N/A']
            ]
            info_table = Table(info_data, colWidths=[1.2*inch, 2.5*inch, 1.2*inch, 2*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 0.3*inch))

            productos_data = [['Código', 'Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']]
            for item in items_data:
                productos_data.append([
                    item[0],
                    item[1],
                    str(item[2]),
                    f"RD$ {item[3]:.2f}",
                    f"RD$ {item[4]:.2f}"
                ])

            productos_table = Table(productos_data, colWidths=[1*inch, 3*inch, 1*inch, 1.2*inch, 1.2*inch])
            productos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(productos_table)
            elements.append(Spacer(1, 0.3*inch))

            totales_data = [
                ['', '', '', 'Subtotal:', f"RD$ {factura_data[2]:.2f}"],
                ['', '', '', 'ITBIS (18%):', f"RD$ {factura_data[3]:.2f}"],
                ['', '', '', 'TOTAL:', f"RD$ {factura_data[4]:.2f}"]
            ]
            totales_table = Table(totales_data, colWidths=[1*inch, 3*inch, 1*inch, 1.2*inch, 1.2*inch])
            totales_table.setStyle(TableStyle([
                ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
                ('FONTNAME', (3, 2), (-1, 2), 'Helvetica-Bold'),
                ('FONTSIZE', (3, 2), (-1, 2), 12),
                ('LINEABOVE', (3, 2), (-1, 2), 2, colors.black),
                ('TEXTCOLOR', (3, 2), (-1, 2), colors.green),
            ]))
            elements.append(totales_table)
            elements.append(Spacer(1, 0.2*inch))
            footer = Paragraph("Gracias por su preferencia. Documento generado automáticamente.", styles['Footer'])
            elements.append(footer)
            doc.build(elements)
            messagebox.showinfo("Éxito", f"PDF generado correctamente en {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el PDF: {str(e)}")

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
        self.cliente_var.set('')
        
        # Limpiar campos de producto
        self.producto_var.set('')
        self.precio_var.set('')
        self.cantidad_var.set('1')
        
    def cargar_historial(self):
        for item in self.tree_historial.get_children():
            self.tree_historial.delete(item)
        
        buscar = self.hist_buscar.get().strip()
        
        if buscar:
            self.cursor.execute('''
                SELECT f.id, f.numero, f.fecha, c.nombre, f.subtotal, f.itbis, f.total
                FROM facturas f
                JOIN clientes c ON f.cliente_id = c.id
                WHERE f.numero LIKE ? OR c.nombre LIKE ?
                ORDER BY f.id DESC
            ''', (f'%{buscar}%', f'%{buscar}%'))
        else:
            self.cursor.execute('''
                SELECT f.id, f.numero, f.fecha, c.nombre, f.subtotal, f.itbis, f.total
                FROM facturas f
                JOIN clientes c ON f.cliente_id = c.id
                ORDER BY f.id DESC
            ''')
        
        for row in self.cursor.fetchall():
            formatted_row = (
                row[0], row[1], row[2], row[3],
                f"RD$ {row[4]:.2f}",
                f"RD$ {row[5]:.2f}",
                f"RD$ {row[6]:.2f}"
            )
            self.tree_historial.insert('', tk.END, values=formatted_row)
            
    def ver_detalles_factura(self):
        selected = self.tree_historial.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una factura")
            return
        
        item = self.tree_historial.item(selected[0])
        factura_id = item['values'][0]
        
        # Crear ventana de detalles
        detalle_win = tk.Toplevel(self.root)
        detalle_win.title("Detalles de Factura")
        set_app_icon(detalle_win, self.base_path)
        detalle_win.geometry("700x500")
        detalle_win.configure(bg="white")
        
        # Obtener datos
        self.cursor.execute('''
            SELECT f.numero, f.fecha, f.subtotal, f.itbis, f.total,
                   c.nombre, c.cedula, c.telefono
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            WHERE f.id = ?
        ''', (factura_id,))
        
        factura_data = self.cursor.fetchone()
        
        # Información general
        info_frame = tk.Frame(detalle_win, bg="white", relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(info_frame, text=f"Factura: {factura_data[0]}", font=("Arial", 14, "bold"),
                bg="white").pack(pady=5)
        tk.Label(info_frame, text=f"Fecha: {factura_data[1]}", bg="white").pack()
        tk.Label(info_frame, text=f"Cliente: {factura_data[5]}", bg="white").pack()
        tk.Label(info_frame, text=f"Cédula: {factura_data[6]}", bg="white").pack()
        
        # Tabla de items
        tk.Label(detalle_win, text="Productos:", font=("Arial", 12, "bold"),
                bg="white").pack(pady=5)
        
        tree_frame = tk.Frame(detalle_win, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tree = ttk.Treeview(tree_frame, columns=("Código", "Producto", "Cant", "Precio", "Subtotal"),
                           show="headings", height=8)
        
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
        self.cursor.execute('''
            SELECT p.codigo, p.nombre, fi.cantidad, fi.precio_unitario, fi.subtotal
            FROM factura_items fi
            JOIN productos p ON fi.producto_id = p.id
            WHERE fi.factura_id = ?
        ''', (factura_id,))
        
        for row in self.cursor.fetchall():
            tree.insert('', tk.END, values=(
                row[0], row[1], row[2],
                f"RD$ {row[3]:.2f}",
                f"RD$ {row[4]:.2f}"
            ))
        
        # Totales
        total_frame = tk.Frame(detalle_win, bg="white")
        total_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(total_frame, text=f"Subtotal: RD$ {factura_data[2]:.2f}",
                font=("Arial", 11), bg="white").pack()
        tk.Label(total_frame, text=f"ITBIS: RD$ {factura_data[3]:.2f}",
                font=("Arial", 11), bg="white").pack()
        tk.Label(total_frame, text=f"TOTAL: RD$ {factura_data[4]:.2f}",
                font=("Arial", 13, "bold"), bg="white", fg="#27ae60").pack()
        
    def regenerar_pdf(self):
        selected = self.tree_historial.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una factura")
            return
        
        item = self.tree_historial.item(selected[0])
        factura_id = item['values'][0]
        
        try:
            self.generar_pdf(factura_id)
            messagebox.showinfo("Éxito", "PDF generado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")
        
    def cargar_datos(self):
        """Carga los datos en los combobox"""
        # Cargar productos en combobox
        self.cursor.execute('SELECT codigo, nombre FROM productos ORDER BY nombre')
        productos = [f"{row[0]} - {row[1]}" for row in self.cursor.fetchall()]
        self.combo_producto['values'] = productos
        
        # Cargar clientes en combobox
        self.cursor.execute('SELECT nombre, cedula FROM clientes ORDER BY nombre')
        clientes = [f"{row[0]} - {row[1]}" if row[1] else row[0] for row in self.cursor.fetchall()]
        self.combo_cliente['values'] = clientes
        
        # Cargar tablas
        self.cargar_productos()
        self.cargar_clientes()
        self.cargar_historial()
        self.cargar_empresa()

# Ejecutar aplicación
def start_main_app():
    app = None
    try:
        main_root = tk.Tk()
        app = SistemaFacturacion(main_root)
        main_root.mainloop()
    except Exception as e:
        messagebox.showerror("Error Fatal", 
            f"Error al iniciar la aplicación: {str(e)}\n\nLa aplicación se cerrará.")
    finally:
        if app and hasattr(app, 'conn'):
            try:
                app.conn.close()
            except:
                pass

if __name__ == "__main__":
    login_root = tk.Tk()
    LoginWindow(login_root, on_success=start_main_app)
    login_root.mainloop()
