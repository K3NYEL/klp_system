import tkinter as tk
from tkinter import messagebox

from app.auth.login_window import LoginWindow
from app.ui.main_window import SistemaFacturacion


def start_login():
    login_root = tk.Tk()
    LoginWindow(login_root, on_success=start_main_app)
    login_root.mainloop()

def start_main_app(user=None):
    app = None
    try:
        main_root = tk.Tk()
        app = SistemaFacturacion(main_root, on_logout=start_login, current_user=user)
        main_root.mainloop()
    except Exception as e:
        messagebox.showerror("Error Fatal", f"Error al iniciar la aplicación: {str(e)}\n\nLa aplicación se cerrará.")
    finally:
        if app and hasattr(app, "conn"):
            try:
                app.conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    start_login()
