**SISTEMA DE FACTURACION**

## Estructura del proyecto

```text
app/
	main.py                 # Punto de entrada y ciclo de vida de la aplicación
	auth/login_window.py    # Inicio de sesión y registro de usuarios
	core/ui.py              # Rutas de recursos, iconos y estilos Tkinter
	ui/main_window.py       # Ventana principal y módulos de facturación
programa_de_facturacion.py # Lanzador compatible para ejecución local
```

Para ejecutar la aplicación localmente usa el entorno virtual del proyecto:

```bash
.venv/bin/python -m app.main
```

En Windows, el ejecutable se genera mediante `build.bat` y la configuración
de PyInstaller en `facturacion_completa.spec`.

## 📜 Licencia

MIT License
Copyright (c) 2026 Kenyel


Para más detalles, revisa el archivo [LICENSE](./LICENSE).
