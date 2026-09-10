import sqlite3
from pathlib import Path
from typing import Iterable

SCHEMA_VERSION = 1


def connect_database(path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=10)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA journal_mode = WAL")
    migrate_database(connection)
    return connection


def _columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')}


def _add_columns(connection: sqlite3.Connection, table: str, definitions: Iterable[tuple[str, str]]) -> None:
    columns = _columns(connection, table)
    for name, definition in definitions:
        if name not in columns:
            connection.execute(f'ALTER TABLE "{table}" ADD COLUMN "{name}" {definition}')


def migrate_database(connection: sqlite3.Connection) -> None:
    """Applies additive migrations without deleting existing business data."""
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Vendedor'
        );
        CREATE TABLE IF NOT EXISTS config (
            clave TEXT PRIMARY KEY,
            valor TEXT
        );
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT UNIQUE,
            telefono TEXT,
            direccion TEXT
        );
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE,
            fecha TEXT,
            cliente_id INTEGER,
            subtotal REAL,
            itbis REAL,
            total REAL,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        );
        CREATE TABLE IF NOT EXISTS factura_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            factura_id INTEGER,
            producto_id INTEGER,
            cantidad INTEGER,
            precio_unitario REAL,
            subtotal REAL,
            FOREIGN KEY (factura_id) REFERENCES facturas (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        );
        CREATE TABLE IF NOT EXISTS empresa (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            rnc TEXT,
            direccion TEXT,
            telefono TEXT,
            email TEXT,
            website TEXT
        );
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
        );
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            descripcion TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INTEGER NOT NULL REFERENCES roles(id),
            permission_id INTEGER NOT NULL REFERENCES permissions(id),
            PRIMARY KEY (role_id, permission_id)
        );
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER REFERENCES usuarios(id),
            accion TEXT NOT NULL,
            entidad TEXT,
            entidad_id INTEGER,
            detalles TEXT,
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS payment_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
        );
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            factura_id INTEGER NOT NULL REFERENCES facturas(id),
            metodo_id INTEGER NOT NULL REFERENCES payment_methods(id),
            monto REAL NOT NULL CHECK (monto > 0),
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER REFERENCES usuarios(id),
            referencia TEXT
        );
        CREATE TABLE IF NOT EXISTS inventory_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL REFERENCES productos(id),
            tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SALIDA', 'AJUSTE', 'DEVOLUCION')),
            cantidad INTEGER NOT NULL CHECK (cantidad <> 0),
            motivo TEXT NOT NULL,
            referencia TEXT,
            usuario_id INTEGER REFERENCES usuarios(id),
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS cash_registers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_apertura INTEGER REFERENCES usuarios(id),
            fecha_apertura TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            monto_inicial REAL NOT NULL DEFAULT 0 CHECK (monto_inicial >= 0),
            fecha_cierre TEXT,
            monto_esperado REAL,
            monto_contado REAL,
            diferencia REAL,
            estado TEXT NOT NULL DEFAULT 'ABIERTA' CHECK (estado IN ('ABIERTA', 'CERRADA'))
        );
        CREATE TABLE IF NOT EXISTS cash_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caja_id INTEGER NOT NULL REFERENCES cash_registers(id),
            tipo TEXT NOT NULL CHECK (tipo IN ('VENTA', 'GASTO', 'RETIRO', 'INGRESO')),
            monto REAL NOT NULL CHECK (monto > 0),
            metodo_pago TEXT NOT NULL,
            referencia TEXT,
            usuario_id INTEGER REFERENCES usuarios(id),
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS backups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ruta TEXT NOT NULL,
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER REFERENCES usuarios(id)
        );
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
        );
        CREATE TABLE IF NOT EXISTS taxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            porcentaje REAL NOT NULL CHECK (porcentaje >= 0),
            codigo_fiscal TEXT,
            activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
        );
        CREATE TABLE IF NOT EXISTS fiscal_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            factura_id INTEGER NOT NULL UNIQUE REFERENCES facturas(id),
            tipo_comprobante TEXT NOT NULL,
            ncf TEXT UNIQUE,
            secuencia INTEGER,
            fecha_vencimiento TEXT,
            estado TEXT NOT NULL DEFAULT 'PENDIENTE',
            respuesta TEXT
        );
        """
    )

    _add_columns(connection, "usuarios", (
        ("activo", "INTEGER NOT NULL DEFAULT 1"),
        ("ultimo_acceso", "TEXT"),
        ("intentos_fallidos", "INTEGER NOT NULL DEFAULT 0"),
    ))
    _add_columns(connection, "productos", (
        ("codigo_barras", "TEXT"),
        ("descripcion", "TEXT"),
        ("categoria", "TEXT"),
        ("precio_compra", "REAL NOT NULL DEFAULT 0"),
        ("impuesto", "REAL NOT NULL DEFAULT 18"),
        ("stock_minimo", "INTEGER NOT NULL DEFAULT 0"),
        ("unidad_medida", "TEXT NOT NULL DEFAULT 'UNIDAD'"),
        ("activo", "INTEGER NOT NULL DEFAULT 1"),
    ))
    _add_columns(connection, "clientes", (
        ("razon_social", "TEXT"),
        ("email", "TEXT"),
        ("tipo_cliente", "TEXT NOT NULL DEFAULT 'CONTADO'"),
        ("activo", "INTEGER NOT NULL DEFAULT 1"),
    ))
    _add_columns(connection, "facturas", (
        ("estado", "TEXT NOT NULL DEFAULT 'PENDIENTE'"),
        ("descuento", "REAL NOT NULL DEFAULT 0"),
        ("metodo_pago", "TEXT NOT NULL DEFAULT 'CONTADO'"),
        ("usuario_id", "INTEGER"),
        ("fecha_vencimiento", "TEXT"),
        ("observaciones", "TEXT"),
    ))
    _add_columns(connection, "empresa", (
        ("moneda", "TEXT NOT NULL DEFAULT 'RD$'"),
        ("impuesto_porcentaje", "REAL NOT NULL DEFAULT 18"),
        ("logo_path", "TEXT"),
    ))

    connection.executemany(
        "INSERT OR IGNORE INTO roles (nombre) VALUES (?)",
        [("Administrador",), ("Vendedor",), ("Cajero",), ("Contador",)],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO payment_methods (nombre) VALUES (?)",
        [("EFECTIVO",), ("TARJETA",), ("TRANSFERENCIA",), ("CREDITO",), ("OTRO",)],
    )
    connection.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_facturas_fecha ON facturas(fecha);
        CREATE INDEX IF NOT EXISTS idx_facturas_estado ON facturas(estado);
        CREATE INDEX IF NOT EXISTS idx_facturas_cliente ON facturas(cliente_id);
        CREATE INDEX IF NOT EXISTS idx_movimientos_producto ON inventory_movements(producto_id);
        CREATE INDEX IF NOT EXISTS idx_audit_fecha ON audit_logs(fecha);
        CREATE INDEX IF NOT EXISTS idx_payments_factura ON payments(factura_id);
        CREATE INDEX IF NOT EXISTS idx_cash_fecha ON cash_movements(fecha);
        """
    )
    connection.execute(
        "INSERT OR IGNORE INTO schema_version(version) VALUES (?)",
        (SCHEMA_VERSION,),
    )
    connection.commit()


def audit(connection: sqlite3.Connection, action: str, entity: str | None = None,
          entity_id: int | None = None, details: str | None = None,
          user_id: int | None = None) -> None:
    connection.execute(
        """INSERT INTO audit_logs (usuario_id, accion, entidad, entidad_id, detalles)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, action, entity, entity_id, details),
    )
