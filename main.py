import tkinter as tk
import traceback

from app.auth.login_window import LoginWindow
from app.ui.main_window import SistemaFacturacion
from app.ui.splash_screen import SplashScreen


def start_application() -> None:
    """
    Punto de entrada principal de KLP SYSTEM.

    Flujo:
        Splash Screen -> Login -> Dashboard
    """

    splash_root = tk.Tk()

    SplashScreen(
        splash_root,
        on_finished=start_login,
    )

    splash_root.mainloop()


def start_login() -> None:
    """
    Inicia la ventana de inicio de sesión.
    """

    login_root = tk.Tk()

    LoginWindow(
        login_root,
        on_success=start_main_app,
    )

    login_root.mainloop()

def start_main_app(user=None) -> None:
    """
    Inicia la aplicación principal después
    de un inicio de sesión exitoso.
    """

    import time

    application = None
    main_root = None

    try:
        start_time = time.perf_counter()

        print("\n[PERF] Creando Tk...")
        main_root = tk.Tk()

        print(
            f"[PERF] Tk creado: "
            f"{time.perf_counter() - start_time:.3f}s"
        )

        app_start = time.perf_counter()

        print("[PERF] Creando SistemaFacturacion...")

        application = SistemaFacturacion(
            main_root,
            on_logout=start_login,
            current_user=user,
        )

        print(
            f"[PERF] SistemaFacturacion creado: "
            f"{time.perf_counter() - app_start:.3f}s"
        )

        print(
            f"[PERF] Tiempo total: "
            f"{time.perf_counter() - start_time:.3f}s"
        )

        main_root.mainloop()

    except Exception:
        traceback.print_exc()

        # Si la construcción de la interfaz falla, no dejar una
        # ventana principal parcialmente inicializada y operable.
        if main_root is not None:
            try:
                if main_root.winfo_exists():
                    main_root.destroy()
            except tk.TclError:
                pass

        raise

    finally:
        if application and hasattr(application, "conn"):
            try:
                application.conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    start_application()
