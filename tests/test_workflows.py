import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.core.database import connect_database


class WorkflowIntegrityTests(unittest.TestCase):
    def test_payment_cash_and_inventory_records_are_related(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "facturacion.db"
            with connect_database(database) as connection:
                user = connection.execute(
                    "INSERT INTO usuarios (usuario, clave, role) VALUES (?, ?, ?)",
                    ("tester", "hash", "Administrador"),
                ).lastrowid
                customer = connection.execute(
                    "INSERT INTO clientes (nombre) VALUES (?)", ("Cliente prueba",)
                ).lastrowid
                product = connection.execute(
                    "INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
                    ("SKU-1", "Producto prueba", 100, 5),
                ).lastrowid
                cash = connection.execute(
                    "INSERT INTO cash_registers (usuario_apertura, monto_inicial) VALUES (?, ?)",
                    (user, 0),
                ).lastrowid
                invoice = connection.execute(
                    """INSERT INTO facturas
                       (numero, fecha, cliente_id, subtotal, itbis, total, estado, metodo_pago, usuario_id)
                       VALUES (?, DATE('now'), ?, ?, ?, ?, 'PAGADA', 'EFECTIVO', ?)""",
                    ("FAC-TEST", customer, 100, 18, 118, user),
                ).lastrowid
                method = connection.execute(
                    "SELECT id FROM payment_methods WHERE nombre='EFECTIVO'"
                ).fetchone()[0]
                connection.execute(
                    "INSERT INTO payments (factura_id, metodo_id, monto, usuario_id) VALUES (?, ?, ?, ?)",
                    (invoice, method, 118, user),
                )
                connection.execute(
                    "UPDATE productos SET stock=stock-1 WHERE id=? AND stock>=1", (product,)
                )
                connection.execute(
                    """INSERT INTO inventory_movements
                       (producto_id, tipo, cantidad, motivo, referencia, usuario_id)
                       VALUES (?, 'SALIDA', -1, 'Venta', 'FAC-TEST', ?)""",
                    (product, user),
                )
                connection.execute(
                    """INSERT INTO cash_movements
                       (caja_id, tipo, monto, metodo_pago, referencia, usuario_id)
                       VALUES (?, 'VENTA', 118, 'EFECTIVO', 'FAC-TEST', ?)""",
                    (cash, user),
                )
                connection.commit()
                self.assertEqual(connection.execute("SELECT stock FROM productos WHERE id=?", (product,)).fetchone()[0], 4)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM payments WHERE factura_id=?", (invoice,)).fetchone()[0], 1)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM cash_movements WHERE caja_id=?", (cash,)).fetchone()[0], 1)

    def test_foreign_keys_reject_unknown_invoice_payment(self):
        with tempfile.TemporaryDirectory() as directory:
            with connect_database(Path(directory) / "facturacion.db") as connection:
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(
                        "INSERT INTO payments (factura_id, metodo_id, monto) VALUES (999, 1, 10)"
                    )


if __name__ == "__main__":
    unittest.main()
