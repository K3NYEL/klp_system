import sqlite3
from datetime import datetime


TAX_RATE = 0.18


def calculate_totals(items: list[dict], tax_rate: float = TAX_RATE, discount: float = 0) -> tuple[float, float, float]:
    subtotal = round(sum(item["subtotal"] for item in items), 2)
    taxable = max(0, subtotal - discount)
    tax = round(taxable * tax_rate, 2)
    return subtotal, tax, round(taxable + tax, 2)


def next_invoice_number(connection: sqlite3.Connection) -> str:
    row = connection.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM facturas").fetchone()
    return f"FAC-{row[0]:05d}"


def find_customer(connection: sqlite3.Connection, customer_value: str) -> int | None:
    if " - " in customer_value:
        identity = customer_value.split(" - ", 1)[1]
        row = connection.execute("SELECT id FROM clientes WHERE cedula=? AND activo=1", (identity,)).fetchone()
    else:
        row = connection.execute("SELECT id FROM clientes WHERE nombre=? AND activo=1", (customer_value,)).fetchone()
    return row[0] if row else None


def find_product_by_code(connection: sqlite3.Connection, code: str) -> tuple | None:
    return connection.execute(
        "SELECT id, codigo, nombre, precio, stock FROM productos WHERE activo=1 AND codigo=?",
        (code,),
    ).fetchone()


def invoice_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")
