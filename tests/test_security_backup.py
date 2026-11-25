import hashlib
from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.auth.security import hash_password, verify_password
from app.core.backup import create_backup, restore_backup, validate_backup


class PasswordSecurityTests(unittest.TestCase):
    def test_pbkdf2_hash_round_trip(self):
        stored = hash_password("ClaveSegura123")
        self.assertTrue(verify_password("ClaveSegura123", stored)[0])
        self.assertFalse(verify_password("OtraClave123", stored)[0])

    def test_legacy_hash_requests_upgrade(self):
        stored = hashlib.sha256("ClaveAntigua123".encode("utf-8")).hexdigest()
        self.assertEqual(verify_password("ClaveAntigua123", stored), (True, True))

    def test_invalid_iteration_count_is_rejected(self):
        stored = "pbkdf2_sha256$999999999$" + ("ab" * 16) + "$" + ("cd" * 32)
        self.assertEqual(verify_password("Clave123", stored), (False, False))


class BackupTests(unittest.TestCase):
    def create_database(self, path: Path, value: str) -> None:
        with closing(sqlite3.connect(path)) as connection:
            for table in ("usuarios", "productos", "clientes", "facturas", "factura_items"):
                connection.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY, valor TEXT)")
            connection.execute("INSERT INTO facturas (valor) VALUES (?)", (value,))
            connection.commit()

    def test_backup_is_valid_and_contains_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "database.db"
            self.create_database(database, "original")
            backup = create_backup(database, root / "backups")
            validate_backup(backup)
            with closing(sqlite3.connect(backup)) as connection:
                value = connection.execute("SELECT valor FROM facturas").fetchone()[0]
            self.assertEqual(value, "original")

    def test_restore_replaces_database_atomically(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.db"
            target = root / "target.db"
            self.create_database(source, "restored")
            self.create_database(target, "current")
            backup = create_backup(source, root / "source_backups")
            preserved = restore_backup(backup, target, root / "preserved")
            self.assertTrue(preserved.is_file())
            with closing(sqlite3.connect(target)) as connection:
                value = connection.execute("SELECT valor FROM facturas").fetchone()[0]
            self.assertEqual(value, "restored")


if __name__ == "__main__":
    unittest.main()
