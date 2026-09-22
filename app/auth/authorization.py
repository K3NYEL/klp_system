import sqlite3


def list_permissions(
    connection: sqlite3.Connection,
) -> list[tuple]:
    """Devuelve todos los permisos disponibles."""
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


def permissions_for_role(
    connection: sqlite3.Connection,
    role: str | None,
) -> set[str]:
    """Devuelve los códigos de permisos asignados a un rol."""

    if not role:
        return set()

    rows = connection.execute(
        """
        SELECT p.codigo
        FROM role_permissions rp
        INNER JOIN roles r
            ON r.id = rp.role_id
        INNER JOIN permissions p
            ON p.id = rp.permission_id
        WHERE r.nombre = ?
          AND r.activo = 1
        """,
        (role,),
    ).fetchall()

    return {row[0] for row in rows}


def can(
    connection: sqlite3.Connection,
    role: str | None,
    permission: str,
) -> bool:
    """Comprueba si un rol tiene un permiso."""

    return permission in permissions_for_role(
        connection,
        role,
    )