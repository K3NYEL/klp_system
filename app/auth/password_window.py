import logging
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk


class PasswordWindow:

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.password = None

    def open(self):
        try:
            self._build_window()

            window = self.window

            if window is not None:
                window.wait_window()

            return self.password

        except Exception:
            logging.exception(
                "Error construyendo la ventana de contraseña."
            )

            if self.window is not None:
                try:
                    self.window.destroy()
                except tk.TclError:
                    pass

            self.window = None
            return None

    def _build_window(self):
        self.window = tk.Toplevel(self.parent)

        self.window.title("Crear contraseña")
        self.window.geometry("500x300")
        self.window.resizable(False, False)
        self.window.configure(bg="#f0f0f0")
        self.window.transient(self.parent)

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.close,
        )

        ctk.CTkLabel(
            self.window,
            text="Crear contraseña",
            font=("Roboto", 20, "bold"),
            text_color="#2d3436",
        ).pack(pady=(25, 8))

        ctk.CTkLabel(
            self.window,
            text="Crea una contraseña para la nueva cuenta.",
            font=("Arial", 14),
            text_color="#555555",
        ).pack()

        form_frame = ctk.CTkFrame(
            self.window,
            fg_color="#ffffff",
            corner_radius=12,
        )

        form_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=20,
        )

        form_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            form_frame,
            text="Contraseña",
            font=("Arial", 13, "bold"),
            text_color="#2d3436",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=22,
            pady=(22, 8),
        )

        self.password_var = tk.StringVar()

        self.password_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.password_var,
            font=("Arial", 13),
            show="*",
            height=32,
        )

        self.password_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 22),
            pady=(22, 8),
        )

        ctk.CTkLabel(
            form_frame,
            text="Confirmar",
            font=("Arial", 13, "bold"),
            text_color="#2d3436",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=22,
            pady=8,
        )

        self.confirm_password_var = tk.StringVar()

        self.confirm_password_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.confirm_password_var,
            font=("Arial", 13),
            show="*",
            height=32,
        )

        self.confirm_password_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 22),
            pady=8,
        )

        ctk.CTkLabel(
            form_frame,
            text="Mínimo 5 caracteres e incluir letras y números.",
            font=("Arial", 12),
            text_color="#636e72",
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="w",
            padx=22,
            pady=(5, 10),
        )

        button_frame = ctk.CTkFrame(
            form_frame,
            fg_color="transparent",
        )

        button_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=22,
            pady=(5, 15),
        )

        ctk.CTkButton(
            button_frame,
            text="Aceptar",
            command=self.confirm,
            font=("Arial", 13, "bold"),
            width=150,
        ).pack(
            side=tk.LEFT,
            padx=(0, 10),
        )

        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.close,
            fg_color="#757575",
            hover_color="#616161",
            font=("Arial", 13, "bold"),
            width=130,
        ).pack(
            side=tk.LEFT,
        )

        self.window.bind(
            "<Return>",
            lambda event: self.confirm(),
        )

        self.window.bind(
            "<Escape>",
            lambda event: self.close(),
        )

        self.password_entry.focus_set()

        self._center_window()

        try:
            self.window.wait_visibility()
            self.window.grab_set()
        except tk.TclError:
            logging.warning(
                "No se pudo hacer modal la ventana de contraseña."
            )

    def _center_window(self):
        window = self.window

        if window is None:
            return

        window.update_idletasks()

        width = 500
        height = 300

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(
            f"{width}x{height}+{x}+{y}"
    )

    def validate_password(self, password, confirmation):
        window = self.window

        if window is None:
            return False

        if not password or not confirmation:
            messagebox.showwarning(
                "Advertencia",
                "Complete ambos campos.",
                parent=window,
            )
            return False

        if password != confirmation:
            messagebox.showwarning(
                "Advertencia",
                "Las contraseñas no coinciden.",
                parent=window,
            )
            return False

        if len(password) < 5:
            messagebox.showwarning(
                "Advertencia",
                "La contraseña debe tener al menos 5 caracteres.",
                parent=window,
            )
            return False

        if not any(c.isdigit() for c in password):
            messagebox.showwarning(
                "Advertencia",
                "La contraseña debe incluir al menos un número.",
                parent=window,
            )
            return False

        if not any(c.isalpha() for c in password):
            messagebox.showwarning(
                "Advertencia",
                "La contraseña debe incluir al menos una letra.",
                parent=window,
            )
            return False

        return True

    def confirm(self):
        password = self.password_var.get()
        confirmation = self.confirm_password_var.get()

        if not self.validate_password(password, confirmation):
            return

        self.password = password
        self.close()

    def close(self):
        if self.window is None:
            return

        try:
            self.window.grab_release()
        except tk.TclError:
            pass

        try:
            self.window.destroy()
        except tk.TclError:
            pass

        self.window = None