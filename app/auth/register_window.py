import logging
import sqlite3
import tkinter as tk
from typing import Optional
import customtkinter as ctk
from tkinter import messagebox

from app.core.ui import set_app_icon
from app.core.database import connect_database, audit
from app.auth.security import hash_password


class RegisterWindow:
    def __init__(self, root, login_window):
        self.root = root
        self.login_window = login_window

        self.base_path = login_window.base_path
        self.db_path = login_window.db_path

        # Referencia al Toplevel, para poder reutilizarla/cerrarla
        # correctamente en cualquier punto de salida.
        self.window: Optional[tk.Toplevel] = None

    def open_register_window(self):
        try:
            return self._build_register_window()
        except Exception:
            logging.exception("Error construyendo la ventana de registro.")
            messagebox.showerror(
                "Error",
                "No se pudo abrir la ventana de registro. "
                "Revisa el log para más detalle.",
            )
            self.window = None
            return None

    def _build_register_window(self):
        # -----------------------------------------------------------
        # ANTES acá había self.root.withdraw().
        #
        # Esa combinación -ocultar el root y luego abrir un Toplevel
        # con .transient(self.root)- es un problema conocido: varios
        # gestores de ventanas (sobre todo en Linux/X11, y a veces en
        # Windows) se niegan a mapear/mostrar una ventana "transient"
        # cuyo dueño (master) está withdrawn (oculto). El resultado es
        # que el Toplevel nunca llega a pintarse en pantalla, y el
        # proceso queda corriendo sin nada visible: exactamente el bug
        # que estabas reportando desde el principio.
        #
        # La solución: dejamos el root visible detrás. El grab_set()
        # de más abajo ya se encarga de que no se pueda interactuar
        # con el login mientras el registro está abierto, así que no
        # hace falta ocultarlo.
        # -----------------------------------------------------------
        self.window = tk.Toplevel(self.root)
        self.window.title("Registro de Usuario")
        set_app_icon(self.window, self.base_path)
        self.window.geometry("500x470")
        self.window.resizable(False, False)
        self.window.configure(bg="#f0f0f0")
        self.window.transient(self.root)

        # ¡OJO! self.window.grab_set() se llamaba ACÁ en el código
        # original, justo después de crear la ventana y ANTES de
        # centrarla (center_window hace update_idletasks()). En ese
        # punto la ventana todavía no está "viewable" (no terminó de
        # mapearse en pantalla), y grab_set() sobre una ventana no
        # viewable puede lanzar:
        #   _tkinter.TclError: grab failed: window not viewable
        # Como nada capturaba esa excepción, quedaba el root oculto
        # (withdraw) y el Toplevel en un estado roto: exactamente el
        # "la app desaparece y queda en segundo plano" que reportaste.
        #
        # La corrección: centrar/dibujar la ventana primero, y recién
        # al final, cuando ya es visible, pedir el grab.
        self.login_window.center_window(500, 470, window=self.window)

        # -----------------------------------------------------------
        # BUG PRINCIPAL QUE ESTABAS VIENDO:
        # antes, si cerrabas esta ventana con la "X" (o si algo fallaba
        # antes de llegar a window.destroy()), el root quedaba oculto
        # para siempre (withdraw() sin su deiconify() correspondiente).
        # La app seguía corriendo en segundo plano, sin ninguna ventana
        # visible. Este handler garantiza que, sea como sea que se
        # cierre esta ventana, el login se vuelve a mostrar.
        # -----------------------------------------------------------
        self.window.protocol("WM_DELETE_WINDOW", self.close_register_window)

        ctk.CTkLabel(
            self.window,
            text="Crear cuenta",
            font=("Roboto", 20, "bold"),
            text_color="#2d3436",
        ).pack(pady=(20, 6))
        ctk.CTkLabel(
            self.window,
            text="Complete los datos. Luego podrá iniciar sesión con este usuario.",
            font=("Arial", 15),
            text_color="#555",
        ).pack()

        form_frame = ctk.CTkFrame(self.window, fg_color="#ffffff", corner_radius=12)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        form_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            form_frame,
            text="Datos de la cuenta",
            font=("Arial", 15, "bold"),
            text_color="#2d3436",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=22, pady=(20, 14))

        ctk.CTkLabel(
            form_frame, text="Usuario", font=("Arial", 13, "bold"), text_color="#2d3436"
        ).grid(row=1, column=0, sticky="w", padx=22, pady=6)
        new_user_var = tk.StringVar()
        username_entry = ctk.CTkEntry(
            form_frame, textvariable=new_user_var, font=("Arial", 13), height=32
        )
        username_entry.grid(row=1, column=1, sticky="ew", padx=(0, 22), pady=6)

        ctk.CTkLabel(
            form_frame,
            text="Contraseña",
            font=("Arial", 13, "bold"),
            text_color="#2d3436",
        ).grid(row=2, column=0, sticky="w", padx=22, pady=6)
        new_password_var = tk.StringVar()
        ctk.CTkEntry(
            form_frame,
            textvariable=new_password_var,
            font=("Arial", 13),
            show="*",
            height=32,
        ).grid(row=2, column=1, sticky="ew", padx=(0, 22), pady=6)

        ctk.CTkLabel(
            form_frame,
            text="Confirmar contraseña",
            font=("Arial", 13, "bold"),
            text_color="#2d3436",
        ).grid(row=3, column=0, sticky="w", padx=22, pady=6)
        confirm_password_var = tk.StringVar()
        ctk.CTkEntry(
            form_frame,
            textvariable=confirm_password_var,
            font=("Arial", 13),
            show="*",
            height=32,
        ).grid(row=3, column=1, sticky="ew", padx=(0, 22), pady=6)

        ctk.CTkLabel(
            form_frame,
            text="Tipo de usuario",
            font=("Arial", 13, "bold"),
            text_color="#2d3436",
        ).grid(row=4, column=0, sticky="w", padx=22, pady=6)
        ctk.CTkLabel(
            form_frame,
            text="Vendedor (o Administrador si es el primer usuario)",
            text_color="#636e72",
            font=("Arial", 13),
        ).grid(row=4, column=1, sticky="w", padx=(0, 22), pady=6)

        ctk.CTkLabel(
            form_frame,
            text="La contraseña debe tener mínimo 5 caracteres e incluir letras y números.",
            font=("Arial", 13),
            text_color="#636e72",
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=22, pady=(8, 0))

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=6, column=0, columnspan=2, padx=36, pady=(4, 15))

        register_button = ctk.CTkButton(
            button_frame,
            text="Guardar cuenta",
            command=lambda: self.register_user(
                new_user_var.get().strip(),
                new_password_var.get(),
                confirm_password_var.get(),
            ),
            fg_color="#43a047",
            hover_color="#388e3c",
            font=("Arial", 13, "bold"),
            width=190,
        )
        register_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, pady=(5, 16))

        # Antes no existía forma de "salir" de esta ventana salvo la X,
        # que era justo el camino que dejaba la app oculta. Con el
        # protocolo de arriba ya no rompe nada, pero además agregamos
        # un botón explícito para que el usuario no dependa de la X.
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.close_register_window,
            fg_color="#757575",
            hover_color="#616161",
            font=("Arial", 13, "bold"),
            width=140,
        )
        cancel_button.pack(side=tk.LEFT, padx=(0, 10), expand=True, pady=(5, 16))

        self.window.bind("<Return>", lambda event: register_button.invoke())
        self.window.bind("<Escape>", lambda event: self.close_register_window())

        username_entry.focus_set()

        # Recién ACÁ, con la ventana ya construida, centrada y
        # dibujada, pedimos el grab modal. wait_visibility() se
        # asegura de que el sistema de ventanas ya la mapeó en
        # pantalla antes de intentar el grab_set(); si por alguna
        # razón de la plataforma igual fallara, no dejamos que reviente
        # todo el flujo: preferimos una ventana no-modal a que
        # desaparezca la app.
        try:
            self.window.wait_visibility()
            self.window.grab_set()
        except tk.TclError:
            logging.warning(
                "No se pudo hacer modal la ventana de registro (grab_set)."
            )

        return self.window

    def close_register_window(self):
        """
        Cierra la ventana de registro. Como el root del login nunca se
        ocultó (ver la nota en _build_register_window), en general no
        haría falta hacer nada con él más que liberar el foco. El
        deiconify()/lift() se deja como red de seguridad no-op, por si
        en algún punto futuro alguien reintroduce un withdraw().
        """
        if self.window is not None:
            try:
                self.window.grab_release()
            except tk.TclError:
                pass
            self.window.destroy()
            self.window = None

        try:
            self.root.deiconify()
        except tk.TclError:
            pass
        self.root.lift()
        self.root.focus_force()

    def register_user(self, usuario, clave, clave_confirm):
        # Copiamos self.window a una variable local: así el type
        # checker sabe que, de acá para abajo, "window" ya no puede
        # ser None (Optional[Toplevel] -> Toplevel), y dejamos de
        # generar el warning de "Toplevel | None no es asignable a
        # Misc" en cada messagebox.
        window = self.window
        if window is None:
            return

        if not usuario or not clave or not clave_confirm:
            messagebox.showwarning(
                "Advertencia", "Complete todos los campos", parent=window
            )
            return
        if clave != clave_confirm:
            messagebox.showwarning(
                "Advertencia", "Las contraseñas no coinciden", parent=window
            )
            return
        if len(clave) < 5:
            messagebox.showwarning(
                "Advertencia",
                "La contraseña debe tener al menos 5 caracteres",
                parent=window,
            )
            return
        if not any(c.isdigit() for c in clave) or not any(c.isalpha() for c in clave):
            messagebox.showwarning(
                "Advertencia",
                "La contraseña debe incluir letras y números",
                parent=window,
            )
            return

        try:
            with connect_database(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario,))
                if cursor.fetchone():
                    messagebox.showwarning(
                        "Advertencia", "El usuario ya existe", parent=window
                    )
                    return

                # El primer usuario del sistema se vuelve Administrador
                # automáticamente; el parámetro "role" que antes se
                # recibía y se ignoraba se eliminó porque no aportaba
                # nada (el rol real siempre se calcula acá).
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                first_user = cursor.fetchone()[0] == 0
                assigned_role = "Administrador" if first_user else "Vendedor"

                cursor.execute(
                    "INSERT INTO usuarios (usuario, clave, role) VALUES (?, ?, ?)",
                    (usuario, hash_password(clave), assigned_role),
                )
                user_id = cursor.lastrowid
                audit(conn, "CREAR_USUARIO", "usuarios", user_id, usuario, user_id)
                conn.commit()

            messagebox.showinfo(
                "Registro exitoso",
                f"Usuario registrado correctamente como {assigned_role}.\n"
                "Ahora puede iniciar sesión.",
                parent=window,
            )

            # Precargamos el usuario en el login para comodidad, y
            # recién ahí cerramos y restauramos el root.
            try:
                self.login_window.username_var.set(usuario)
            except Exception:
                pass

            self.close_register_window()

        except sqlite3.Error as e:
            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudo crear el usuario: {e}",
                parent=window,
            )