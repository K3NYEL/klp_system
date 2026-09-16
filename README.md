###KLP SYSTEM

Para ejecutar la aplicación localmente usa el entorno virtual del proyecto:

```bash
.venv/bin/python main.py
```

Instala las dependencias con:

```bash
.venv/bin/pip install -r requirements.txt
```

Las pruebas de infraestructura se ejecutan con:

```bash
.venv/bin/python -m unittest discover -s tests
```

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
