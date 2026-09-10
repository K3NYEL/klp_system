import sqlite3

from app.core.audit import record_audit


def register_movement(connection: sqlite3.Connection, product_id: int, movement_type: str,
                      quantity: int, reason: str, user_id: int | None) -> None:
    if movement_type not in {"ENTRADA", "AJUSTE", "DEVOLUCION"}:
        raise ValueError("Tipo de movimiento no válido.")
    if quantity <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")
    if not reason.strip():
        raise ValueError("El motivo es obligatorio.")
    delta = quantity if movement_type in {"ENTRADA", "DEVOLUCION"} else quantity
    connection.execute("UPDATE productos SET stock=stock+? WHERE id=? AND activo=1", (delta, product_id))
    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise ValueError("Producto no encontrado o inactivo.")
    connection.execute(
        """INSERT INTO inventory_movements
           (producto_id, tipo, cantidad, motivo, usuario_id)
           VALUES (?, ?, ?, ?, ?)""",
        (product_id, movement_type, delta, reason.strip(), user_id),
    )
    record_audit(connection, "MOVIMIENTO_INVENTARIO", "productos", product_id, reason, user_id)
    connection.commit()
