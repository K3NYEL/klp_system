@echo off
cd /d "%~dp0"

:: --- 1. ACTIVAR ENTORNO VIRTUAL (SI USAS UNO) ---
:: Si guardas tus librerías en una carpeta como 'venv' o '.venv', 
:: quita los dos puntos (::) de la línea de abajo para activarlo:
call .venv\Scripts\activate

echo [1/2] Limpiando la salida de desarrollo y compilando con PyInstaller...
echo.

:: Nunca empaquetar la base de datos usada durante el desarrollo.
if exist dist\facturacion.db del /q dist\facturacion.db
if exist dist\facturacion.db-wal del /q dist\facturacion.db-wal
if exist dist\facturacion.db-shm del /q dist\facturacion.db-shm

pyinstaller --clean --noconfirm facturacion_completa.spec

:: --- 2. CONTROL DE ERRORES ---
:: Verifica si PyInstaller devolvió un código de error (cualquier cosa diferente a 0)
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo [ERROR] La compilacion ha fallado. Revisa el texto de arriba.
    echo ============================================================
    goto final
)

:: --- 3. EXITO ---
echo.
echo ============================================================
echo [OK] Build complete. El ejecutable esta en dist\facturacion.exe
echo ============================================================

:final
echo.
echo Presiona cualquier tecla para salir...
pause > nul