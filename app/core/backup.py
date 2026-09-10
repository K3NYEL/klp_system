import os
import sqlite3
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
