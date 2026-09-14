import tkinter as tk
from tkinter import messagebox

from app.auth.login_window import LoginWindow
from app.ui.main_window import SistemaFacturacion


def start_login() -> None:
    login_root = tk.Tk()
    LoginWindow(login_root, on_success=start_main_app)
    login_root.mainloop()


def start_main_app(user=None) -> None:
    application = None
    try:
        main_root = tk.Tk()
        application = SistemaFacturacion(
            main_root,  
            on_logout=start_login,
            current_user=user,
        )
        main_root.mainloop()
    except Exception as exc:
        messagebox.showerror(
            "Error Fatal",
            f"Error al iniciar la aplicación: {exc}\n\nLa aplicación se cerrará.",
        )
    finally:
        if application and hasattr(application, "conn"):
            try:
                application.conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    start_login()
