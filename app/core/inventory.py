import sqlite3

from app.core.audit import record_audit


def register_movement(
    connection: sqlite3.Connection,
    product_id: int,
    movement_type: str,
    quantity: int,
    reason: str,
    user_id: int | None,
) -> None:
    if movement_type not in {
        "ENTRADA",
        "SALIDA",
        "AJUSTE",
        "DEVOLUCION",
    }:
        raise ValueError("Tipo de movimiento no válido.")

    if quantity <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")

    reason = reason.strip()

    if not reason:
        raise ValueError("El motivo es obligatorio.")

    # Los movimientos se almacenan con cantidad positiva.
    # El tipo determina cómo afecta al stock.
    if movement_type in {
        "ENTRADA",
        "DEVOLUCION",
        "AJUSTE",
    }:
        delta = quantity

    elif movement_type == "SALIDA":
        delta = -quantity

    connection.execute(
        """
        UPDATE productos
        SET stock = stock + ?
        WHERE id = ?
        AND activo = 1
        AND (
            stock + ?
        ) >= 0
        """,
        (
            delta,
            product_id,
            delta,
        ),
    )

    if connection.execute("SELECT changes()").fetchone()[0] != 1:
        raise ValueError("Producto no encontrado, inactivo " "o stock insuficiente.")

    connection.execute(
        """
        INSERT INTO inventory_movements (
            producto_id,
            tipo,
            cantidad,
            motivo,
            usuario_id
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            product_id,
            movement_type,
            quantity,
            reason,
            user_id,
        ),
    )

    record_audit(
        connection,
        "MOVIMIENTO_INVENTARIO",
        "productos",
        product_id,
        reason,
        user_id,
    )

    connection.commit()
