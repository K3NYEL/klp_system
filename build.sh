#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

PYTHON=".venv/bin/python"
PYINSTALLER=".venv/bin/pyinstaller"

if [[ ! -x "$PYTHON" ]]; then
    PYTHON="python3"
fi

if [[ ! -x "$PYINSTALLER" ]]; then
    PYINSTALLER="$(command -v pyinstaller || true)"
fi

if [[ -z "$PYINSTALLER" ]]; then
    echo "Error: PyInstaller no está instalado."
    echo "Instálalo con: $PYTHON -m pip install pyinstaller"
    exit 1
fi

echo "[1/3] Limpiando la compilación anterior..."
rm -rf build/klp_system dist/klp_system dist/facturacion.db dist/facturacion.db-wal dist/facturacion.db-shm

# Nunca se incluye la base de datos de desarrollo en el ejecutable.
echo "[2/3] Generando ejecutable Linux..."
"$PYINSTALLER" --clean --noconfirm facturacion_completa.spec


if [[ ! -x dist/klp_system ]]; then
    echo "Error: no se generó dist/klp_system"
    exit 1
fi

echo "[3/3] Compilación terminada correctamente."
echo "Ejecutable: $(pwd)/dist/klp_system"
echo "Ejecuta con: ./dist/klp_system"
