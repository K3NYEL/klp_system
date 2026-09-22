import sqlite3

from app.auth.security import hash_password
from app.core.audit import record_audit


# ============================================================
# USUARIOS
# ============================================================

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
    role = role.strip()

    if not username:
        raise ValueError("El usuario es obligatorio.")

    if len(password) < 8:
        raise ValueError(
            "La contraseña debe tener al menos 8 caracteres."
        )

    # El rol debe existir y estar activo.
    role_exists = connection.execute(
        """
        SELECT 1
        FROM roles
        WHERE nombre = ?
          AND activo = 1
        """,
        (role,),
    ).fetchone()

    if not role_exists:
        raise ValueError(
            "El rol seleccionado no existe o está desactivado."
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
        f"Usuario: {username} | Rol: {role}",
        actor_id,
    )

    connection.commit()

    return user_id


def update_user_role(
    connection: sqlite3.Connection,
    user_id: int,
    role: str,
    actor_id: int | None,
) -> None:
    role = role.strip()

    user = connection.execute(
        """
        SELECT usuario, role
        FROM usuarios
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    if not user:
        raise ValueError(
            "El usuario seleccionado no existe."
        )

    role_exists = connection.execute(
        """
        SELECT 1
        FROM roles
        WHERE nombre = ?
          AND activo = 1
        """,
        (role,),
    ).fetchone()

    if not role_exists:
        raise ValueError(
            "El rol seleccionado no existe o está desactivado."
        )

    username, old_role = user

    if old_role == role:
        raise ValueError(
            "El usuario ya tiene ese rol."
        )

    # Evitar que el último administrador activo pierda
    # accidentalmente el rol de administrador.
    if old_role == "Administrador":
        admin_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM usuarios
            WHERE role = 'Administrador'
            AND activo = 1
            """
        ).fetchone()[0]

        if admin_count <= 1:
            raise ValueError(
                "No puedes quitar el rol de Administrador "
                "al último administrador activo."
            )

    connection.execute(
        """
        UPDATE usuarios
        SET role = ?
        WHERE id = ?
        """,
        (role, user_id),
    )

    record_audit(
        connection,
        "CAMBIAR_ROL_USUARIO",
        "usuarios",
        user_id,
        f"Usuario: {username} | {old_role} -> {role}",
        actor_id,
    )

    connection.commit()


def change_user_password(
    connection: sqlite3.Connection,
    user_id: int,
    new_password: str,
    actor_id: int | None,
) -> None:
    if len(new_password) < 8:
        raise ValueError(
            "La contraseña debe tener al menos 8 caracteres."
        )

    user = connection.execute(
        """
        SELECT usuario
        FROM usuarios
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    if not user:
        raise ValueError(
            "El usuario seleccionado no existe."
        )

    username = user[0]

    connection.execute(
        """
        UPDATE usuarios
        SET clave = ?,
            intentos_fallidos = 0
        WHERE id = ?
        """,
        (
            hash_password(new_password),
            user_id,
        ),
    )

    record_audit(
        connection,
        "CAMBIAR_CONTRASENA",
        "usuarios",
        user_id,
        f"Usuario: {username}",
        actor_id,
    )

    connection.commit()


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
        SELECT usuario, role, activo
        FROM usuarios
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    if not row:
        raise ValueError(
            "El usuario seleccionado no existe."
        )

    username, role, active = row

    if not active:
        raise ValueError(
            "El usuario ya está desactivado."
        )

    # No permitir dejar el sistema sin administradores activos.
    if role == "Administrador":
        admin_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM usuarios
            WHERE role = 'Administrador'
              AND activo = 1
            """
        ).fetchone()[0]

        if admin_count <= 1:
            raise ValueError(
                "No puedes desactivar al último "
                "Administrador activo."
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


# ============================================================
# ROLES
# ============================================================

def list_roles(
    connection: sqlite3.Connection,
    include_inactive: bool = True,
) -> list[tuple]:
    query = """
        SELECT
            r.id,
            r.nombre,
            r.activo,
            COUNT(
                CASE
                    WHEN u.activo = 1 THEN 1
                END
            ) AS usuarios_activos
        FROM roles r
        LEFT JOIN usuarios u
            ON u.role = r.nombre
    """

    if not include_inactive:
        query += " WHERE r.activo = 1 "

    query += """
        GROUP BY
            r.id,
            r.nombre,
            r.activo
        ORDER BY r.nombre
    """

    return connection.execute(query).fetchall()


def create_role(
    connection: sqlite3.Connection,
    name: str,
    actor_id: int | None,
) -> int:
    name = name.strip()

    if not name:
        raise ValueError(
            "El nombre del rol es obligatorio."
        )

    existing = connection.execute(
        """
        SELECT id
        FROM roles
        WHERE nombre = ?
        """,
        (name,),
    ).fetchone()

    if existing:
        raise ValueError(
            "Ya existe un rol con ese nombre."
        )

    try:
        cursor = connection.execute(
            """
            INSERT INTO roles (
                nombre,
                activo
            )
            VALUES (?, 1)
            """,
            (name,),
        )
    except sqlite3.IntegrityError as exc:
        raise ValueError(
            "Ya existe un rol con ese nombre."
        ) from exc

    role_id = cursor.lastrowid

    record_audit(
        connection,
        "CREAR_ROL",
        "roles",
        role_id,
        name,
        actor_id,
    )

    connection.commit()

    return role_id


def rename_role(
    connection: sqlite3.Connection,
    role_id: int,
    new_name: str,
    actor_id: int | None,
) -> None:
    new_name = new_name.strip()

    if not new_name:
        raise ValueError(
            "El nombre del rol es obligatorio."
        )

    role = connection.execute(
        """
        SELECT nombre
        FROM roles
        WHERE id = ?
        """,
        (role_id,),
    ).fetchone()

    if not role:
        raise ValueError(
            "El rol seleccionado no existe."
        )

    old_name = role[0]

    if old_name == new_name:
        raise ValueError(
            "El rol ya tiene ese nombre."
        )

    existing = connection.execute(
        """
        SELECT id
        FROM roles
        WHERE nombre = ?
          AND id != ?
        """,
        (new_name, role_id),
    ).fetchone()

    if existing:
        raise ValueError(
            "Ya existe otro rol con ese nombre."
        )

    try:
        # Primero actualizamos roles.
        connection.execute(
            """
            UPDATE roles
            SET nombre = ?
            WHERE id = ?
            """,
            (new_name, role_id),
        )

        # Como usuarios.role almacena el nombre,
        # también debemos actualizar los usuarios.
        connection.execute(
            """
            UPDATE usuarios
            SET role = ?
            WHERE role = ?
            """,
            (new_name, old_name),
        )

    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise ValueError(
            "No se pudo cambiar el nombre del rol."
        ) from exc

    record_audit(
        connection,
        "RENOMBRAR_ROL",
        "roles",
        role_id,
        f"{old_name} -> {new_name}",
        actor_id,
    )

    connection.commit()


def activate_role(
    connection: sqlite3.Connection,
    role_id: int,
    actor_id: int | None,
) -> None:
    row = connection.execute(
        """
        SELECT nombre, activo
        FROM roles
        WHERE id = ?
        """,
        (role_id,),
    ).fetchone()

    if not row:
        raise ValueError(
            "El rol seleccionado no existe."
        )

    name, active = row

    if active:
        raise ValueError(
            "El rol ya está activo."
        )

    connection.execute(
        """
        UPDATE roles
        SET activo = 1
        WHERE id = ?
        """,
        (role_id,),
    )

    record_audit(
        connection,
        "ACTIVAR_ROL",
        "roles",
        role_id,
        name,
        actor_id,
    )

    connection.commit()


def deactivate_role(
    connection: sqlite3.Connection,
    role_id: int,
    actor_id: int | None,
) -> None:
    row = connection.execute(
        """
        SELECT nombre, activo
        FROM roles
        WHERE id = ?
        """,
        (role_id,),
    ).fetchone()

    if not row:
        raise ValueError(
            "El rol seleccionado no existe."
        )

    name, active = row

    if not active:
        raise ValueError(
            "El rol ya está desactivado."
        )

    active_users = connection.execute(
        """
        SELECT COUNT(*)
        FROM usuarios
        WHERE role = ?
          AND activo = 1
        """,
        (name,),
    ).fetchone()[0]

    if active_users > 0:
        raise ValueError(
            f"No puedes desactivar el rol porque tiene "
            f"{active_users} usuario(s) activo(s) asignado(s)."
        )

    if name == "Administrador":
        raise ValueError(
            "El rol Administrador no puede desactivarse."
        )

    connection.execute(
        """
        UPDATE roles
        SET activo = 0
        WHERE id = ?
        """,
        (role_id,),
    )

    record_audit(
        connection,
        "DESACTIVAR_ROL",
        "roles",
        role_id,
        name,
        actor_id,
    )

    connection.commit()


# ============================================================
# PERMISOS
# ============================================================

def list_permissions(
    connection: sqlite3.Connection,
) -> list[tuple]:
    return connection.execute(
        """
        SELECT
            id,
            codigo,
            descripcion
        FROM permissions
        ORDER BY id
        """
    ).fetchall()


def get_role_permissions(
    connection: sqlite3.Connection,
    role_id: int,
) -> set[str]:
    rows = connection.execute(
        """
        SELECT p.codigo
        FROM role_permissions rp
        INNER JOIN permissions p
            ON p.id = rp.permission_id
        WHERE rp.role_id = ?
        ORDER BY p.id
        """,
        (role_id,),
    ).fetchall()

    return {row[0] for row in rows}


def set_role_permissions(
    connection: sqlite3.Connection,
    role_id: int,
    permission_codes: set[str],
    actor_id: int | None,
) -> None:
    role = connection.execute(
        """
        SELECT nombre, activo
        FROM roles
        WHERE id = ?
        """,
        (role_id,),
    ).fetchone()

    if not role:
        raise ValueError(
            "El rol seleccionado no existe."
        )

    role_name, active = role

    if not active:
        raise ValueError(
            "No puedes modificar los permisos de un rol "
            "desactivado."
        )

    valid_permissions = {
        row[0]
        for row in connection.execute(
            """
            SELECT codigo
            FROM permissions
            """
        ).fetchall()
    }

    invalid = permission_codes - valid_permissions

    if invalid:
        raise ValueError(
            "Se encontraron permisos no válidos."
        )

    # El Administrador debe conservar manage_users.
    if role_name == "Administrador":
        if "manage_users" not in permission_codes:
            raise ValueError(
                "El rol Administrador debe conservar "
                "el permiso para gestionar usuarios."
            )

    try:
        connection.execute(
            """
            DELETE FROM role_permissions
            WHERE role_id = ?
            """,
            (role_id,),
        )

        for code in permission_codes:
            permission = connection.execute(
                """
                SELECT id
                FROM permissions
                WHERE codigo = ?
                """,
                (code,),
            ).fetchone()

            if permission:
                connection.execute(
                    """
                    INSERT INTO role_permissions (
                        role_id,
                        permission_id
                    )
                    VALUES (?, ?)
                    """,
                    (
                        role_id,
                        permission[0],
                    ),
                )

    except Exception:
        connection.rollback()
        raise

    details = (
        f"Rol: {role_name} | "
        f"Permisos: {', '.join(sorted(permission_codes)) or 'ninguno'}"
    )

    record_audit(
        connection,
        "ACTUALIZAR_PERMISOS_ROL",
        "roles",
        role_id,
        details,
        actor_id,
    )

    connection.commit()

def change_user_role(
        connection: sqlite3.Connection,
        user_id: int,
        role: str,
        actor_id: int | None,
    ) -> None:
        """Compatibilidad con las vistas que usan el nombre change_user_role."""
        update_user_role(
        connection,
        user_id,
        role,
        actor_id,
    )