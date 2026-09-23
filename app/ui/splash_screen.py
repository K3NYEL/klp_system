import customtkinter as ctk

from app.core.ui import CREATOR_URL, set_app_icon
from app.core.paths import application_path
from app.ui.styles import Colors, Fonts


class SplashScreen:
    """
    Pantalla de carga inicial de KLP SYSTEM.

    El SplashScreen no realiza directamente tareas pesadas.
    Su responsabilidad es mostrar el progreso de inicialización
    que le comunique el proceso de preparación del sistema.
    """

    def __init__(self, root, on_finished):

        self.root = root
        self.on_finished = on_finished
        self.base_path = application_path()

        self._finished = False

        # =========================================================
        # CONFIGURACIÓN DE LA VENTANA
        # =========================================================

        self.root.title("KLP SYSTEM")
        self.root.geometry("520x320")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)

        set_app_icon(
            self.root,
            self.base_path,
        )

        self.center_window(
            520,
            320,
        )

        # =========================================================
        # INTERFAZ
        # =========================================================

        self.create_widgets()

        # =========================================================
        # INICIO
        # =========================================================

        self.root.after(
            100,
            self.start_loading,
        )

    # =============================================================
    # UTILIDADES
    # =============================================================

    def center_window(self, width, height):
        """Centra la ventana en la pantalla."""

        self.root.update_idletasks()

        x = (
            self.root.winfo_screenwidth() - width
        ) // 2

        y = (
            self.root.winfo_screenheight() - height
        ) // 2

        self.root.geometry(
            f"{width}x{height}+{x}+{y}"
        )

    # =============================================================
    # INTERFAZ
    # =============================================================

    def create_widgets(self):

        # =========================================================
        # CONTENEDOR PRINCIPAL
        # =========================================================

        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=Colors.SURFACE,
            corner_radius=0,
            border_width=1,
            border_color=Colors.BORDER,
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
        )

        # =========================================================
        # CONTENIDO CENTRAL
        # =========================================================

        content_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
            corner_radius=0,
        )

        content_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        # =========================================================
        # MARCA
        # =========================================================

        self.title_label = ctk.CTkLabel(
            content_frame,
            text="KLP SYSTEM",
            text_color=Colors.PRIMARY,
            font=Fonts.TITLE,
        )

        self.title_label.pack(
            pady=(0, 4),
        )

        # =========================================================
        # DESCRIPCIÓN
        # =========================================================

        self.subtitle_label = ctk.CTkLabel(
            content_frame,
            text="Sistema de facturación",
            text_color=Colors.TEXT_SECONDARY,
            font=Fonts.BODY,
        )

        self.subtitle_label.pack(
            pady=(0, 24),
        )

        # =========================================================
        # BARRA DE PROGRESO
        # =========================================================

        self.progress = ctk.CTkProgressBar(
            content_frame,
            width=300,
            height=6,
            corner_radius=3,
            fg_color=Colors.BORDER,
            progress_color=Colors.PRIMARY,
        )

        self.progress.pack()

        self.progress.set(0)

        # =========================================================
        # ESTADO
        # =========================================================

        self.status_label = ctk.CTkLabel(
            content_frame,
            text="Iniciando sistema...",
            text_color=Colors.TEXT_SECONDARY,
            font=Fonts.SMALL,
        )

        self.status_label.pack(
            pady=(12, 0),
        )

        # =========================================================
        # FOOTER
        # =========================================================

        self.footer_label = ctk.CTkLabel(
            self.main_frame,
            text="KLP SYSTEM",
            text_color=Colors.TEXT_SECONDARY,
            font=Fonts.SMALL,
        )

        self.footer_label.place(
            relx=0.5,
            rely=0.93,
            anchor="center",
        )

        # =============================================================
    # INICIALIZACIÓN REAL
    # =============================================================

    def start_loading(self):
        """
        Inicia la preparación real de KLP SYSTEM.
        """

        from threading import Thread

        from app.setup.initializer import Initializer

        self.initializer = Initializer(
            progress_callback=self._queue_progress,
        )

        self.worker = Thread(
            target=self._run_initializer,
            daemon=True,
        )

        self.worker.start()

    def _run_initializer(self):
        """
        Ejecuta el inicializador en segundo plano.
        """

        success = self.initializer.run()

        self.root.after(
            0,
            self._initialization_finished,
            success,
        )

    def _queue_progress(
        self,
        progress,
        message,
    ):
        """
        Envía las actualizaciones del hilo de trabajo
        al hilo principal de Tkinter.
        """

        self.root.after(
            0,
            self.set_progress,
            progress,
            message,
        )

    def set_progress(
        self,
        progress,
        status=None,
    ):
        """
        Actualiza visualmente el progreso.
        """

        if self._finished:
            return

        progress = max(
            0,
            min(100, progress),
        )

        self.progress.set(
            progress / 100,
        )

        if status:
            self.status_label.configure(
                text=status,
            )

        self.root.update_idletasks()

    # =============================================================
    # FINALIZACIÓN DE INICIALIZACIÓN
    # =============================================================

    def _initialization_finished(self, success):
        """
        Se ejecuta cuando Initializer termina.
        """

        if self._finished:
            return

        if success:

            self.set_progress(
                100,
                "Sistema listo.",
            )

            self.root.after(
                350,
                self.finish,
            )

        else:

            self.status_label.configure(
                text="No se pudo preparar el sistema.",
            )

            self.progress.set(0)

    # =============================================================
    # API DE PROGRESO
    # =============================================================

    def update_status(self, text, progress=None):
        """
        Actualiza el mensaje y el progreso del SplashScreen.

        Parameters
        ----------
        text:
            Texto que se mostrará debajo de la barra.

        progress:
            Progreso entre 0 y 100.
            Si es None, solamente se actualiza el texto.
        """

        if self._finished:
            return

        self.status_label.configure(
            text=text,
        )

        if progress is not None:

            progress = max(
                0,
                min(100, progress),
            )

            self.progress.set(
                progress / 100,
            )

        self.root.update_idletasks()

    # =============================================================
    # PROGRESO POR TAREA
    # =============================================================

    def set_progress(self, progress, status=None):
        """
        Permite actualizar manualmente el progreso.

        Útil para tareas reales como:

            set_progress(25, "Verificando dependencias...")
            set_progress(50, "Inicializando base de datos...")
            set_progress(100, "Sistema listo.")
        """

        if self._finished:
            return

        progress = max(
            0,
            min(100, progress),
        )

        self.progress.set(
            progress / 100,
        )

        if status:
            self.status_label.configure(
                text=status,
            )

        self.root.update_idletasks()

    # =============================================================
    # FINALIZAR
    # =============================================================

    def finish(self):

        if self._finished:
            return

        self._finished = True

        self.root.destroy()

        if self.on_finished:
            self.on_finished()