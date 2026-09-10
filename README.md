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

La base `facturacion.db` de la raíz contiene los datos de desarrollo actuales y
no se incluye en PyInstaller. En una versión empaquetada, los datos se guardan
en una carpeta separada del ejecutable: `%LOCALAPPDATA%/FacturacionApp` en
Windows o `~/.local/share/FacturacionApp` en Linux. Por eso una compilación
nueva empieza con una base limpia. Para conservar datos de otra instalación,
usa un backup y restáuralo explícitamente; no copies la base de desarrollo al
ejecutable.

En Windows, el ejecutable se genera mediante `build.bat` y la configuración
de PyInstaller en `facturacion_completa.spec`.

En Linux, no abras `build.bat`: ejecuta desde una terminal:

```bash
bash build.sh
```

El ejecutable se crea en:

```text
dist/facturacion
```

Para iniciarlo:

```bash
./dist/facturacion
```

También puedes usar `bash run.sh` para iniciar el ejecutable. Los archivos
`.sh` son scripts de compilación/arranque; si el explorador los abre como
texto, ejecútalos desde una terminal con `bash nombre-del-script.sh`.

El binario se genera para la arquitectura Linux del equipo donde se compila.
Para distribuirlo en otra arquitectura o distribución, recompílalo allí.

## 📜 Licencia

MIT License
Copyright (c) 2026 Kenyel


Para más detalles, revisa el archivo [LICENSE](./LICENSE).
