@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo.
echo ============================================================
echo                 KLP SYSTEM - BUILD WINDOWS
echo ============================================================
echo.

:: -----------------------------------------------------------------------
:: 1. Comprobar entorno
:: -----------------------------------------------------------------------

echo [1/5] Comprobando entorno...

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

:: -----------------------------------------------------------------------
:: 2. Limpiar compilacion anterior
:: -----------------------------------------------------------------------

echo [2/5] Limpiando compilacion anterior...

if exist "build\klp_system" (
    rmdir /s /q "build\klp_system"
)

if exist "dist\klp_system.exe" (
    del /q "dist\klp_system.exe"
)

if exist "releases\Windows" (
    rmdir /s /q "releases\Windows"
)

mkdir "releases\Windows"

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

:: -----------------------------------------------------------------------
:: 3. PyInstaller
:: -----------------------------------------------------------------------

echo [3/5] Generando ejecutable Windows...

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

:: -----------------------------------------------------------------------
:: 4. Preparar ejecutable final
:: -----------------------------------------------------------------------

echo [4/5] Preparando ejecutable final...

copy /Y "dist\klp_system.exe" "releases\Windows\klp_system.exe" > nul

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo copiar el ejecutable final.
    echo.
    goto error
)

if not exist "releases\Windows\klp_system.exe" (
    echo.
    echo [ERROR] No se encontro el ejecutable final.
    echo.
    goto error
)

echo Ejecutable final preparado correctamente.
echo.

:: -----------------------------------------------------------------------
:: 5. Resultado
:: -----------------------------------------------------------------------

echo [5/5] Verificando resultado...
echo.

echo ============================================================
echo             KLP SYSTEM - BUILD COMPLETADO
echo ============================================================
echo.

echo Ejecutable Windows:
echo   %CD%\releases\Windows\klp_system.exe
echo.

for %%A in ("releases\Windows\klp_system.exe") do (
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