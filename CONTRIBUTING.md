# Guía de contribución

Gracias por ayudar a mejorar KLP SYSTEM. Esta guía define un flujo de trabajo básico para colaborar de forma ordenada.

## Antes de empezar

1. Lee el [README](README.md), [INSTALLATION.md](INSTALLATION.md) y [ARCHITECTURE.md](ARCHITECTURE.md).
2. Revisa los issues y las pull requests existentes para evitar duplicar trabajo.
3. Confirma con el mantenedor el alcance de cambios grandes o que afecten a la base de datos.
4. Trabaja en una rama de desarrollo; no hagas commits directamente en `main`.

## Preparar el entorno

Sigue las instrucciones de [INSTALLATION.md](INSTALLATION.md). Para ejecutar desde el código fuente:

```bash
python main.py
```

## Flujo de trabajo

1. Actualiza tu rama base antes de comenzar.
2. Crea una rama descriptiva para tu tarea, por ejemplo `fix/login-validation`, `feature/customer-search` o `docs/setup-guide`.
3. Realiza cambios pequeños y enfocados.
4. Ejecuta las comprobaciones disponibles y prueba manualmente los flujos afectados.
5. Revisa `git diff` y `git status` antes de confirmar.
6. Abre una pull request hacia la rama que indique el mantenedor. No asumas que el destino es `main`.

Comandos habituales:

```bash
git switch <rama-base>
git pull
git switch -c <rama-descriptiva>
git status
git diff
```

## Convenciones

- Mantén el código compatible con la versión de Python utilizada por el proyecto.
- Usa Tkinter y ttk para la interfaz; no reintroduzcas CustomTkinter sin aprobación del mantenedor.
- Mantén las consultas SQL parametrizadas. No construyas consultas con datos introducidos por el usuario.
- Separa la interfaz de las operaciones de negocio: coloca lógica reutilizable en `app/services/` o `app/core/`, según su responsabilidad.
- Conserva las migraciones de SQLite de forma aditiva y compatible con bases de datos existentes.
- No elimines ni reemplaces datos de usuarios durante una migración.
- No incluyas credenciales, archivos `.env`, bases de datos reales, respaldos ni información personal en commits.
- No añadas dependencias sin justificar su necesidad y actualizar `requirements.txt`.

## Estilo de commits

Usa mensajes breves que indiquen la intención:

```text
feat: añadir búsqueda de clientes
fix: corregir validación de factura
docs: actualizar instrucciones de instalación
refactor: separar lógica de inventario
```

## Comprobaciones antes de abrir una pull request

Como mínimo:

- Comprueba que la aplicación inicia con `python main.py`.
- Recorre manualmente el módulo afectado.
- Comprueba que no aparecen errores en la terminal.
- Si el cambio afecta a SQLite, prueba con una copia de una base de datos y verifica que los datos existentes se conservan.
- Si modifica el empaquetado, ejecuta el script correspondiente en el sistema operativo objetivo.

El repositorio puede no incluir todavía una suite de pruebas automatizadas completa. No afirmes que las pruebas pasan si no se ejecutaron.

## Pull requests

Incluye en la descripción:

- Problema que resuelve y motivo del cambio.
- Resumen de los archivos o módulos modificados.
- Pasos de prueba y resultado observado.
- Capturas para cambios visuales, cuando sean útiles.
- Riesgos, limitaciones o migraciones necesarias.

No publiques releases ni cambies la configuración de workflows sin autorización del mantenedor.
