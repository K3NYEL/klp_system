**SISTEMA DE FACTURACION**

## Estructura del proyecto

```text
app/
	main.py                 # Punto de entrada y ciclo de vida de la aplicación
	auth/login_window.py    # Inicio de sesión y registro de usuarios
	core/paths.py           # Rutas de datos para ejecución local y ejecutable
	core/ui.py              # Rutas de recursos, iconos y estilos Tkinter
	ui/main_window.py       # Ventana principal y módulos de facturación
programa_de_facturacion.py # Lanzador compatible para ejecución local
```

Para ejecutar la aplicación localmente usa el entorno virtual del proyecto:

```bash
.venv/bin/python -m app.main
```

Instala las dependencias con:

```bash
.venv/bin/pip install -r requirements.txt
```

Las pruebas de infraestructura se ejecutan con:

```bash
.venv/bin/python -m unittest discover -s tests
```

Las copias de seguridad manuales se crean desde `Archivo > Crear copia de
seguridad` y se guardan en la carpeta `backups/` sin sobrescribir copias
anteriores.

En Windows, el ejecutable se genera mediante `build.bat` y la configuración
de PyInstaller en `facturacion_completa.spec`.

## 📜 Licencia

MIT License
Copyright (c) 2026 Kenyel


Para más detalles, revisa el archivo [LICENSE](./LICENSE).
