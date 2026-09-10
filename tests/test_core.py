import hashlib
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.core.backup import create_backup
from app.core.database import connect_database
from app.auth.security import hash_password, verify_password


class CoreInfrastructureTests(unittest.TestCase):
    def test_migration_preserves_existing_data(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "facturacion.db"
            shutil.copy2("facturacion.db", database)
            with connect_database(database) as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                self.assertIn("usuarios", tables)
                self.assertIn("payments", tables)
                self.assertIn("audit_logs", tables)
                self.assertGreaterEqual(
                    connection.execute("SELECT COUNT(*) FROM facturas").fetchone()[0], 0
                )

    def test_password_hash_supports_new_and_legacy_values(self):
        password = "Segura123"
        self.assertEqual(verify_password(password, hash_password(password)), (True, False))
        legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self.assertEqual(verify_password(password, legacy), (True, True))
        self.assertFalse(verify_password("incorrecta", legacy)[0])

    def test_backup_is_valid_sqlite_database(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "facturacion.db"
            shutil.copy2("facturacion.db", database)
            backup = create_backup(database, Path(directory) / "backups")
            with sqlite3.connect(backup) as connection:
                self.assertEqual(
                    connection.execute("PRAGMA integrity_check").fetchone()[0], "ok"
                )


if __name__ == "__main__":
    unittest.main()
