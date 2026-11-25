import os
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

REQUIRED_TABLES = {"usuarios", "productos", "clientes", "facturas", "factura_items"}


def _integrity_check(connection: sqlite3.Connection) -> None:
    rows = connection.execute("PRAGMA integrity_check").fetchall()
    if not rows or any(row[0] != "ok" for row in rows):
        details = "; ".join(str(row[0]) for row in rows)
        raise ValueError(f"La base de datos no es íntegra: {details or 'sin resultado'}")


def validate_backup(backup_path: str | Path) -> None:
    path = Path(backup_path)
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(f"No existe un backup válido: {path}")
    try:
        with sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True) as connection:
            _integrity_check(connection)
            tables = {row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )}
            missing = REQUIRED_TABLES - tables
            if missing:
                raise ValueError("El backup no contiene las tablas requeridas: " + ", ".join(sorted(missing)))
    except sqlite3.DatabaseError as exc:
        raise ValueError(f"El archivo de backup no es una base SQLite válida: {exc}") from exc


def create_backup(database_path: str | Path, backup_directory: str | Path) -> Path:
    source = Path(database_path)
    if not source.is_file():
        raise FileNotFoundError(f"No existe la base de datos: {source}")
    destination_dir = Path(backup_directory)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"facturacion_{datetime.now():%Y%m%d_%H%M%S_%f}.db"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".facturacion_backup_", suffix=".tmp", dir=destination_dir, delete=False) as handle:
            temporary = Path(handle.name)
        with sqlite3.connect(source) as source_connection:
            with sqlite3.connect(temporary) as backup_connection:
                source_connection.backup(backup_connection)
                _integrity_check(backup_connection)
        validate_backup(temporary)
        os.replace(temporary, destination)
        return destination
    except Exception:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise


def restore_backup(backup_path: str | Path, database_path: str | Path, backup_directory: str | Path) -> Path:
    source_path = Path(backup_path).resolve()
    database = Path(database_path).resolve()
    if source_path == database:
        raise ValueError("El backup y la base de datos de destino deben ser archivos distintos.")
    validate_backup(source_path)
    if not database.is_file():
        raise FileNotFoundError(f"No existe la base de datos que se va a reemplazar: {database}")
    current_copy = create_backup(database, backup_directory)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=f".{database.name}.restore_", suffix=".tmp", dir=database.parent, delete=False) as handle:
            temporary = Path(handle.name)
        with sqlite3.connect(source_path) as source_connection:
            with sqlite3.connect(temporary) as target_connection:
                source_connection.backup(target_connection)
                _integrity_check(target_connection)
        validate_backup(temporary)
        Path(f"{database}-wal").unlink(missing_ok=True)
        Path(f"{database}-shm").unlink(missing_ok=True)
        os.replace(temporary, database)
        return current_copy
    except Exception:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise
