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

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

APPDIR="AppDir"
APPIMAGE="dist/KLP-System-x86_64.AppImage"

# appimagetool extraído para evitar problemas con FUSE
APPIMAGETOOL="$HOME/.local/bin/squashfs-root/AppRun"

# ---------------------------------------------------------------------------
# 1. Limpiar
# ---------------------------------------------------------------------------

echo "[1/5] Limpiando la compilación anterior..."

rm -rf \
    build/klp_system \
    dist/klp_system \
    "$APPIMAGE"

rm -f \
    dist/facturacion.db \
    dist/facturacion.db-wal \
    dist/facturacion.db-shm

# ---------------------------------------------------------------------------
# 2. PyInstaller
# ---------------------------------------------------------------------------

echo "[2/5] Generando ejecutable Linux..."

"$PYINSTALLER" --clean --noconfirm klp_system.spec

if [[ ! -x dist/klp_system ]]; then
    echo "Error: no se generó dist/klp_system"
    exit 1
fi

echo "Ejecutable generado correctamente."

# ---------------------------------------------------------------------------
# 3. Preparar AppDir
# ---------------------------------------------------------------------------

echo "[3/5] Preparando AppDir..."

rm -rf "$APPDIR"

mkdir -p \
    "$APPDIR/usr/bin" \
    "$APPDIR/usr/share/applications" \
    "$APPDIR/usr/share/icons/hicolor/256x256/apps"

cp \
    dist/klp_system \
    "$APPDIR/usr/bin/klp_system"

chmod +x \
    "$APPDIR/usr/bin/klp_system"

# ---------------------------------------------------------------------------
# Desktop Entry
# ---------------------------------------------------------------------------

cat > "$APPDIR/usr/share/applications/klp_system.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=KLP SYSTEM
Comment=Sistema de facturación y gestión
Exec=klp_system
Icon=klp_system
Terminal=false
Categories=Office;Finance;
EOF

# AppImage necesita el desktop entry también en la raíz
cp \
    "$APPDIR/usr/share/applications/klp_system.desktop" \
    "$APPDIR/klp_system.desktop"

# ---------------------------------------------------------------------------
# Icono
# ---------------------------------------------------------------------------

ICON_FOUND=""

for icon in \
    "app/ui/assets/icon.png" \
    "app/ui/assets/logo.png" \
    "app/ui/assets/klp_system.png"
do
    if [[ -f "$icon" ]]; then
        ICON_FOUND="$icon"
        break
    fi
done

if [[ -n "$ICON_FOUND" ]]; then
    cp \
        "$ICON_FOUND" \
        "$APPDIR/usr/share/icons/hicolor/256x256/apps/klp_system.png"

    cp \
        "$ICON_FOUND" \
        "$APPDIR/klp_system.png"

    echo "Icono encontrado: $ICON_FOUND"
else
    echo "Aviso: no se encontró un icono PNG para el AppImage."
fi

# ---------------------------------------------------------------------------
# AppRun
# ---------------------------------------------------------------------------

cat > "$APPDIR/AppRun" <<'EOF'
#!/usr/bin/env bash

HERE="$(dirname "$(readlink -f "$0")")"

exec "$HERE/usr/bin/klp_system" "$@"
EOF

chmod +x "$APPDIR/AppRun"

# ---------------------------------------------------------------------------
# 4. Comprobar appimagetool
# ---------------------------------------------------------------------------

echo "[4/5] Comprobando appimagetool..."

if [[ ! -x "$APPIMAGETOOL" ]]; then
    echo ""
    echo "Error: no se encontró el AppRun de appimagetool."
    echo ""
    echo "Ruta esperada:"
    echo "  $APPIMAGETOOL"
    echo ""
    exit 1
fi

"$APPIMAGETOOL" --version

# ---------------------------------------------------------------------------
# 5. Crear AppImage
# ---------------------------------------------------------------------------

echo "[5/5] Generando AppImage..."

"$APPIMAGETOOL" \
    "$APPDIR" \
    "$APPIMAGE"

if [[ ! -f "$APPIMAGE" ]]; then
    echo "Error: no se generó el AppImage."
    exit 1
fi

chmod +x "$APPIMAGE"

echo ""
echo "=============================================="
echo "       KLP SYSTEM - BUILD COMPLETADO"
echo "=============================================="
echo ""

echo "Ejecutable:"
echo "  $(pwd)/dist/klp_system"

echo ""

echo "AppImage:"
echo "  $(pwd)/$APPIMAGE"

echo ""

echo "Ejecutar AppImage:"
echo "  ./$APPIMAGE"

echo ""