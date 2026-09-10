import os
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path


def create_backup(database_path: str | Path, backup_directory: str | Path) -> Path:
    source = Path(database_path)
    destination_dir = Path(backup_directory)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"facturacion_{datetime.now():%Y%m%d_%H%M%S}.db"

    source_connection = sqlite3.connect(source)
    backup_connection = sqlite3.connect(destination)
    try:
        source_connection.backup(backup_connection)
        backup_connection.execute("PRAGMA integrity_check")
        backup_connection.commit()
    finally:
        backup_connection.close()
        source_connection.close()
    return destination


def validate_backup(backup_path: str | Path) -> None:
    path = Path(backup_path)
    if not path.is_file():
        raise FileNotFoundError(f"No existe el backup: {path}")
    with sqlite3.connect(path) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise ValueError(f"El backup no es íntegro: {result}")
        connection.execute("SELECT name FROM sqlite_master LIMIT 1").fetchone()


def restore_backup(backup_path: str | Path, database_path: str | Path,
                   backup_directory: str | Path) -> Path:
    """Restores a validated backup after preserving the current database."""
    validate_backup(backup_path)
    current_copy = create_backup(database_path, backup_directory)
    source = sqlite3.connect(backup_path)
    target = sqlite3.connect(database_path)
    temporary = Path(f"{database_path}.restore.tmp")
    try:
        source.backup(target)
        target.commit()
    finally:
        target.close()
        source.close()
        if temporary.exists():
            temporary.unlink()
    return current_copy
