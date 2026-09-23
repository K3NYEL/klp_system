@echo off

cd /d "%~dp0"

:: --- 1. ACTIVAR ENTORNO VIRTUAL ---

call .venv\Scripts\activate

echo [1/2] Limpiando la salida de desarrollo y compilando KLP SYSTEM con PyInstaller...
echo.

:: Nunca empaquetar la base de datos usada durante el desarrollo.

if exist dist\facturacion.db del /q dist\facturacion.db
if exist dist\facturacion.db-wal del /q dist\facturacion.db-wal
if exist dist\facturacion.db-shm del /q dist\facturacion.db-shm

pyinstaller --clean --noconfirm facturacion_completa.spec

:: --- 2. CONTROL DE ERRORES ---

if %errorlevel% neq 0 (

```
echo.
echo ============================================================
echo [ERROR] La compilacion de KLP SYSTEM ha fallado.
echo ============================================================
goto final
```

)

:: --- 3. EXITO ---

echo.
echo ============================================================
echo [OK] KLP SYSTEM compilado correctamente.
echo Ejecutable: dist\klp_system.exe
echo ============================================================

:final

echo.
echo Presiona cualquier tecla para salir...
pause > nul
