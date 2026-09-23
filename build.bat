@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo.
echo ============================================================
echo                 KLP SYSTEM - BUILD WINDOWS
echo ============================================================
echo.

:: ---------------------------------------------------------------------------
:: 1. Comprobar entorno
:: ---------------------------------------------------------------------------

echo [1/4] Comprobando entorno...

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo [ERROR] No se encontro el entorno virtual de Python.
    echo.
    echo Esperado:
    echo   .venv\Scripts\python.exe
    echo.
    goto error
)

if not exist ".venv\Scripts\pyinstaller.exe" (
    echo.
    echo [ERROR] PyInstaller no esta instalado en el entorno virtual.
    echo.
    echo Instala PyInstaller con:
    echo   .venv\Scripts\python.exe -m pip install pyinstaller
    echo.
    goto error
)

echo Entorno encontrado correctamente.
echo.

:: ---------------------------------------------------------------------------
:: 2. Limpiar compilacion anterior
:: ---------------------------------------------------------------------------

echo [2/4] Limpiando compilacion anterior...

if exist "build\klp_system" (
    rmdir /s /q "build\klp_system"
)

if exist "dist\klp_system.exe" (
    del /q "dist\klp_system.exe"
)

:: Nunca empaquetar la base de datos de desarrollo.

if exist "dist\facturacion.db" (
    del /q "dist\facturacion.db"
)

if exist "dist\facturacion.db-wal" (
    del /q "dist\facturacion.db-wal"
)

if exist "dist\facturacion.db-shm" (
    del /q "dist\facturacion.db-shm"
)

echo Limpieza completada.
echo.

:: ---------------------------------------------------------------------------
:: 3. PyInstaller
:: ---------------------------------------------------------------------------

echo [3/4] Generando ejecutable Windows...

".venv\Scripts\pyinstaller.exe" --clean --noconfirm "klp_system.spec"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo [ERROR] La compilacion de KLP SYSTEM ha fallado.
    echo ============================================================
    echo.
    goto error
)

if not exist "dist\klp_system.exe" (
    echo.
    echo ============================================================
    echo [ERROR] PyInstaller termino, pero no se encontro:
    echo         dist\klp_system.exe
    echo ============================================================
    echo.
    goto error
)

echo Compilacion completada correctamente.
echo.

:: ---------------------------------------------------------------------------
:: 4. Resultado
:: ---------------------------------------------------------------------------

echo [4/4] Verificando resultado...
echo.

echo ============================================================
echo             KLP SYSTEM - BUILD COMPLETADO
echo ============================================================
echo.
echo Ejecutable Windows:
echo   %CD%\dist\klp_system.exe
echo.

for %%A in ("dist\klp_system.exe") do (
    echo Tamano:
    echo   %%~zA bytes
)

echo.
echo ============================================================
echo.

goto end

:error

echo.
echo ============================================================
echo                  BUILD FALLIDO
echo ============================================================
echo.
echo Revisa el error mostrado anteriormente.
echo.

:end

echo Presiona cualquier tecla para salir...
pause > nul

endlocal