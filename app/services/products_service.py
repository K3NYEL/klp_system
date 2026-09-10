import sqlite3

from app.core.audit import record_audit


def list_products(connection: sqlite3.Connection, search: str = "") -> list[tuple]:
    pattern = f"%{search.strip()}%"
    return connection.execute(
        """SELECT id, codigo, nombre, precio, stock
           FROM productos
           WHERE activo=1 AND (codigo LIKE ? OR nombre LIKE ?)
           ORDER BY nombre""",
        (pattern, pattern),
    ).fetchall()


def create_product(connection: sqlite3.Connection, code: str, name: str,
                   price: float, stock: int, user_id: int | None) -> int:
    if not code or not name:
        raise ValueError("Código y nombre son obligatorios.")
    if price <= 0:
        raise ValueError("El precio debe ser mayor que cero.")
    if stock < 0:
        raise ValueError("El stock no puede ser negativo.")
    cursor = connection.execute(
        "INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
        (code, name, price, stock),
    )
    product_id = cursor.lastrowid
    record_audit(connection, "CREAR_PRODUCTO", "productos", product_id, code, user_id)
    connection.commit()
    return product_id


def update_product(connection: sqlite3.Connection, product_id: int, code: str,
                   name: str, price: float, stock: int, user_id: int | None) -> None:
    if not code or not name or price <= 0 or stock < 0:
        raise ValueError("Código, nombre, precio válido y stock no negativo son obligatorios.")
    connection.execute(
        "UPDATE productos SET codigo=?, nombre=?, precio=?, stock=? WHERE id=? AND activo=1",
        (code, name, price, stock, product_id),
    )
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise ValueError("Producto no encontrado o inactivo.")
    record_audit(connection, "ACTUALIZAR_PRODUCTO", "productos", product_id, code, user_id)
    connection.commit()


def deactivate_product(connection: sqlite3.Connection, product_id: int, user_id: int | None) -> None:
    connection.execute("UPDATE productos SET activo=0 WHERE id=?", (product_id,))
    record_audit(connection, "DESACTIVAR_PRODUCTO", "productos", product_id, None, user_id)
    connection.commit()
