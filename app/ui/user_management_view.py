import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from app.core.user_management import create_user, deactivate_user, list_users


class UserManagementView:
    def __init__(self, parent, connection, actor_id):
        self.connection = connection
        self.actor_id = actor_id
        self.window = tk.Toplevel(parent)
        self.window.title("Usuarios y permisos")
        self.window.geometry("680x430")
        self.window.transient(parent)
        self._build()
        self.refresh()

    def _build(self):
        form = tk.LabelFrame(self.window, text="Crear usuario", padx=10, pady=10)
        form.pack(fill=tk.X, padx=12, pady=12)
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.role = tk.StringVar(value="Vendedor")
        tk.Label(form, text="Usuario").grid(row=0, column=0, padx=5)
        tk.Entry(form, textvariable=self.username, width=20).grid(row=0, column=1, padx=5)
        tk.Label(form, text="Contraseña").grid(row=0, column=2, padx=5)
        tk.Entry(form, textvariable=self.password, show="*", width=20).grid(row=0, column=3, padx=5)
        ttk.Combobox(form, textvariable=self.role, state="readonly",
                     values=("Administrador", "Vendedor", "Cajero", "Contador"), width=16).grid(row=0, column=4, padx=5)
        tk.Button(form, text="Crear", command=self.create, bg="#27ae60", fg="white").grid(row=0, column=5, padx=5)

        self.tree = ttk.Treeview(self.window, columns=("ID", "Usuario", "Rol", "Activo", "Último acceso"), show="headings")
        for column in ("ID", "Usuario", "Rol", "Activo", "Último acceso"):
            self.tree.heading(column, text=column)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=5)
        tk.Button(self.window, text="Desactivar seleccionado", command=self.deactivate,
                  bg="#e74c3c", fg="white").pack(pady=10)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in list_users(self.connection):
            self.tree.insert("", tk.END, values=(row[0], row[1], row[2], "Sí" if row[3] else "No", row[4] or ""))

    def create(self):
        try:
            create_user(self.connection, self.username.get().strip(), self.password.get(), self.role.get(), self.actor_id)
            self.username.set("")
            self.password.set("")
            self.refresh()
            messagebox.showinfo("Usuarios", "Usuario creado correctamente.", parent=self.window)
        except (ValueError, Exception) as exc:
            messagebox.showerror("Usuarios", str(exc), parent=self.window)

    def deactivate(self):
        selected = self.tree.selection()
        if not selected:
            return
        user_id = self.tree.item(selected[0])["values"][0]
        if not messagebox.askyesno("Usuarios", "¿Desactivar el usuario seleccionado?", parent=self.window):
            return
        try:
            deactivate_user(self.connection, int(user_id), self.actor_id)
            self.refresh()
        except (ValueError, Exception) as exc:
            messagebox.showerror("Usuarios", str(exc), parent=self.window)
