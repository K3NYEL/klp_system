import tkinter as tk
from tkinter import ttk

from app.core.ui import set_app_icon
from app.core.paths import application_path
from app.ui.styles import Colors, Fonts, configure_app_style


class SplashScreen:
    def __init__(self, root, on_finished):
        self.root = root
        self.on_finished = on_finished
        self.base_path = application_path()
        self._finished = False

        configure_app_style(self.root)
        self.root.title("KLP SYSTEM")
        self.root.geometry("520x320")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        self.root.configure(bg=Colors.SURFACE)

        set_app_icon(self.root, self.base_path)
        self.center_window(520, 320)
        self.create_widgets()
        self.root.after(100, self.start_loading)

    def center_window(self, width, height):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        self.main_frame = tk.Frame(
            self.root,
            bg=Colors.SURFACE,
            highlightthickness=1,
            highlightbackground=Colors.BORDER,
        )
        self.main_frame.pack(fill="both", expand=True)

        content_frame = tk.Frame(self.main_frame, bg=Colors.SURFACE)
        content_frame.place(relx=0.5, rely=0.47, anchor="center")

        self.title_label = tk.Label(
            content_frame,
            text="KLP SYSTEM",
            bg=Colors.SURFACE,
            fg=Colors.PRIMARY,
            font=Fonts.TITLE,
        )
        self.title_label.pack(pady=(0, 4))

        self.subtitle_label = tk.Label(
            content_frame,
            text="Sistema de facturación",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY,
        )
        self.subtitle_label.pack(pady=(0, 24))

        self.progress = ttk.Progressbar(
            content_frame,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            length=300,
            style="TProgressbar",
        )
        self.progress.pack()
        self.progress["value"] = 0

        self.status_label = tk.Label(
            content_frame,
            text="Iniciando sistema...",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.SMALL,
        )
        self.status_label.pack(pady=(12, 0))

        self.footer_label = tk.Label(
            self.main_frame,
            text="KLP SYSTEM",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.SMALL,
        )
        self.footer_label.place(relx=0.5, rely=0.93, anchor="center")

    def start_loading(self):
        from threading import Thread
        from app.setup.initializer import Initializer

        self.initializer = Initializer(progress_callback=self._queue_progress)
        self.worker = Thread(target=self._run_initializer, daemon=True)
        self.worker.start()

    def _run_initializer(self):
        success = self.initializer.run()
        try:
            self.root.after(0, self._initialization_finished, success)
        except tk.TclError:
            pass

    def _queue_progress(self, progress, message):
        try:
            self.root.after(0, self.set_progress, progress, message)
        except tk.TclError:
            pass

    def set_progress(self, progress, status=None):
        if self._finished:
            return
        progress = max(0, min(100, progress))
        self.progress["value"] = progress
        if status:
            self.status_label.configure(text=status)
        self.root.update_idletasks()

    def _initialization_finished(self, success):
        if self._finished:
            return
        if success:
            self.set_progress(100, "Sistema listo.")
            self.root.after(350, self.finish)
        else:
            self.status_label.configure(text="No se pudo preparar el sistema.")
            self.progress["value"] = 0

    def update_status(self, text, progress=None):
        if self._finished:
            return
        self.status_label.configure(text=text)
        if progress is not None:
            self.progress["value"] = max(0, min(100, progress))
        self.root.update_idletasks()

    def finish(self):
        if self._finished:
            return
        self._finished = True
        self.root.destroy()
        if self.on_finished:
            self.on_finished()
