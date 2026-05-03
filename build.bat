@echo off
cd /d "%~dp0"
pyinstaller --clean facturacion_completa.spec
echo.
echo Build complete. The executable is in dist\facturacion.exe
echo Press any key to close...
pause > nul
