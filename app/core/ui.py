import os
import sys
import tkinter as tk
from tkinter import ttk

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
