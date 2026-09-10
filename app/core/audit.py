import sqlite3


def record_audit(connection: sqlite3.Connection, action: str, entity: str | None = None,
                 entity_id: int | None = None, details: str | None = None,
                 user_id: int | None = None) -> None:
    connection.execute(
        """INSERT INTO audit_logs (usuario_id, accion, entidad, entidad_id, detalles)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, action, entity, entity_id, details),
    )
