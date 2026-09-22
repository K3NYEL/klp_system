import sqlite3

from app.core.audit import record_audit
from app.auth.security import hash_password


VALID_ROLES = {
    "Administrador",
    "Vendedor",
    "Cajero",
    "Contador",
}


def list_users(connection: sqlite3.Connection) -> list[tuple]:
    return connection.execute(
        """
        SELECT
            id,
            usuario,
            role,
            activo,
            ultimo_acceso
        FROM usuarios
        ORDER BY usuario
        """
    ).fetchall()


def create_user(
    connection: sqlite3.Connection,
    username: str,
    password: str,
    role: str,
    actor_id: int | None,
) -> int:
    username = username.strip()

    if not username:
        raise ValueError(
            "El usuario es obligatorio."
        )

    if len(password) < 8:
        raise ValueError(
            "La contraseña debe tener al menos 8 caracteres."
        )

    if role not in VALID_ROLES:
        raise ValueError(
            "Rol no válido."
        )

    existing = connection.execute(
        """
        SELECT id
        FROM usuarios
        WHERE usuario = ?
        """,
        (username,),
    ).fetchone()

    if existing:
        raise ValueError(
            "Ya existe un usuario con ese nombre."
        )

    try:
        cursor = connection.execute(
            """
            INSERT INTO usuarios (
                usuario,
                clave,
                role
            )
            VALUES (?, ?, ?)
            """,
            (
                username,
                hash_password(password),
                role,
            ),
        )

    except sqlite3.IntegrityError as exc:
        raise ValueError(
            "Ya existe un usuario con ese nombre."
        ) from exc

    user_id = cursor.lastrowid

    record_audit(
        connection,
        "CREAR_USUARIO",
        "usuarios",
        user_id,
        username,
        actor_id,
    )

    connection.commit()

    return user_id


def deactivate_user(
    connection: sqlite3.Connection,
    user_id: int,
    actor_id: int | None,
) -> None:
    if user_id == actor_id:
        raise ValueError(
            "No puedes desactivar tu propio usuario."
        )

    row = connection.execute(
        """
        SELECT usuario, activo
        FROM usuarios
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    if not row:
        raise ValueError(
            "El usuario seleccionado no existe."
        )

    username, active = row

    if not active:
        raise ValueError(
            "El usuario ya está desactivado."
        )

    connection.execute(
        """
        UPDATE usuarios
        SET activo = 0
        WHERE id = ?
        """,
        (user_id,),
    )

    record_audit(
        connection,
        "DESACTIVAR_USUARIO",
        "usuarios",
        user_id,
        username,
        actor_id,
    )

    connection.commit()


def activate_user(
    connection: sqlite3.Connection,
    user_id: int,
    actor_id: int | None,
) -> None:
    row = connection.execute(
        """
        SELECT usuario, activo
        FROM usuarios
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    if not row:
        raise ValueError(
            "El usuario seleccionado no existe."
        )

    username, active = row

    if active:
        raise ValueError(
            "El usuario ya está activo."
        )

    connection.execute(
        """
        UPDATE usuarios
        SET activo = 1
        WHERE id = ?
        """,
        (user_id,),
    )

    record_audit(
        connection,
        "ACTIVAR_USUARIO",
        "usuarios",
        user_id,
        username,
        actor_id,
    )

    connection.commit()