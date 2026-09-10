import sqlite3

from app.core.audit import record_audit


def list_customers(connection: sqlite3.Connection, search: str = "") -> list[tuple]:
    pattern = f"%{search.strip()}%"
    return connection.execute(
        """SELECT id, nombre, cedula, telefono, direccion
           FROM clientes
           WHERE activo=1 AND (nombre LIKE ? OR cedula LIKE ?)
           ORDER BY nombre""",
        (pattern, pattern),
    ).fetchall()


def create_customer(connection: sqlite3.Connection, name: str, identity: str,
                    phone: str, address: str, user_id: int | None) -> int:
    if not name:
        raise ValueError("El nombre es obligatorio.")
    cursor = connection.execute(
        "INSERT INTO clientes (nombre, cedula, telefono, direccion) VALUES (?, ?, ?, ?)",
        (name, identity or None, phone, address),
    )
    customer_id = cursor.lastrowid
    record_audit(connection, "CREAR_CLIENTE", "clientes", customer_id, name, user_id)
    connection.commit()
    return customer_id


def update_customer(connection: sqlite3.Connection, customer_id: int, name: str,
                    identity: str, phone: str, address: str, user_id: int | None) -> None:
    if not name:
        raise ValueError("El nombre es obligatorio.")
    connection.execute(
        """UPDATE clientes SET nombre=?, cedula=?, telefono=?, direccion=?
           WHERE id=? AND activo=1""",
        (name, identity or None, phone, address, customer_id),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise ValueError("Cliente no encontrado o inactivo.")
    record_audit(connection, "ACTUALIZAR_CLIENTE", "clientes", customer_id, name, user_id)
    connection.commit()


def deactivate_customer(connection: sqlite3.Connection, customer_id: int, user_id: int | None) -> None:
    connection.execute("UPDATE clientes SET activo=0 WHERE id=?", (customer_id,))
    record_audit(connection, "DESACTIVAR_CLIENTE", "clientes", customer_id, None, user_id)
    connection.commit()
