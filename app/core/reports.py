from datetime import date
import sqlite3
from typing import Any


def sales_summary(connection: sqlite3.Connection, start: str, end: str) -> dict[str, Any]:
    row = connection.execute(
        """SELECT COUNT(*), COALESCE(SUM(subtotal), 0), COALESCE(SUM(itbis), 0),
                  COALESCE(SUM(total), 0)
           FROM facturas
           WHERE fecha >= ? AND fecha <= ? AND estado <> 'ANULADA'""",
        (start, end),
    ).fetchone()
    return {
        "facturas": row[0],
        "subtotal": row[1],
        "impuestos": row[2],
        "total": row[3],
    }


def top_products(connection: sqlite3.Connection, start: str, end: str, limit: int = 10) -> list[tuple]:
    return connection.execute(
        """SELECT p.codigo, p.nombre, SUM(fi.cantidad) AS unidades,
                  SUM(fi.subtotal) AS ventas
           FROM factura_items fi
           JOIN facturas f ON f.id = fi.factura_id
           JOIN productos p ON p.id = fi.producto_id
           WHERE f.fecha >= ? AND f.fecha <= ? AND f.estado <> 'ANULADA'
           GROUP BY p.id
           ORDER BY unidades DESC
           LIMIT ?""",
        (start, end, limit),
    ).fetchall()


def receivables(connection: sqlite3.Connection) -> list[tuple]:
    return connection.execute(
        """SELECT f.id, f.numero, c.nombre, f.total,
                  COALESCE(SUM(p.monto), 0) AS pagado,
                  f.total - COALESCE(SUM(p.monto), 0) AS saldo
           FROM facturas f
           JOIN clientes c ON c.id = f.cliente_id
           LEFT JOIN payments p ON p.factura_id = f.id
           WHERE f.estado NOT IN ('PAGADA', 'ANULADA')
           GROUP BY f.id
           HAVING saldo > 0
           ORDER BY f.fecha DESC"""
    ).fetchall()
