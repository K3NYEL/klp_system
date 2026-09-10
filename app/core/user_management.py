import sqlite3

from app.core.audit import record_audit
from app.auth.security import hash_password


def list_users(connection: sqlite3.Connection) -> list[tuple]:
    return connection.execute(
        "SELECT id, usuario, role, activo, ultimo_acceso FROM usuarios ORDER BY usuario"
    ).fetchall()


def create_user(connection: sqlite3.Connection, username: str, password: str,
                role: str, actor_id: int | None) -> int:
    if not username or len(password) < 8:
        raise ValueError("El usuario es obligatorio y la contraseña debe tener al menos 8 caracteres.")
    if role not in {"Administrador", "Vendedor", "Cajero", "Contador"}:
        raise ValueError("Rol no válido.")
    cursor = connection.execute(
        "INSERT INTO usuarios (usuario, clave, role) VALUES (?, ?, ?)",
        (username, hash_password(password), role),
    )
    user_id = cursor.lastrowid
    record_audit(connection, "CREAR_USUARIO", "usuarios", user_id, username, actor_id)
    connection.commit()
    return user_id


def deactivate_user(connection: sqlite3.Connection, user_id: int, actor_id: int | None) -> None:
    if user_id == actor_id:
        raise ValueError("No puedes desactivar tu propio usuario.")
    connection.execute("UPDATE usuarios SET activo=0 WHERE id=?", (user_id,))
    record_audit(connection, "DESACTIVAR_USUARIO", "usuarios", user_id, None, actor_id)
    connection.commit()
