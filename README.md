# KLP SYSTEM

Aplicación de escritorio para gestión comercial y facturación, desarrollada en Python con Tkinter/ttk y SQLite.

KLP SYSTEM reúne en una aplicación local herramientas para administrar facturas, productos, clientes, caja y usuarios. La interfaz utiliza widgets nativos de Tkinter y la información operativa se almacena en una base de datos SQLite.

## Características

- **Facturación:** creación y consulta de facturas.
- **Inventario:** administración de productos y existencias.
- **Clientes:** registro y mantenimiento de clientes.
- **Caja:** gestión de cajas y movimientos de efectivo.
- **Usuarios y permisos:** autenticación, roles y permisos.
- **Auditoría:** registro de operaciones relevantes.
- **Copias de seguridad:** creación y restauración de respaldos SQLite con comprobaciones de integridad.
- **Reportes:** generación de documentos PDF.

> El proyecto está en desarrollo. La disponibilidad y el grado de terminación de cada módulo pueden cambiar entre versiones.

## Tecnologías

| Tecnología | Uso |
| --- | --- |
| Python 3 | Lenguaje principal |
| Tkinter + ttk | Interfaz de escritorio |
| SQLite | Persistencia local |
| ReportLab | Generación de PDF |
| Pillow | Recursos gráficos |
| PyInstaller | Empaquetado de ejecutables |

## Requisitos

- Python 3.10 o posterior recomendado.
- Tkinter disponible en la instalación de Python.
- Git para clonar el repositorio.
- En Linux, el paquete del sistema que proporciona Tkinter (por ejemplo, `python3-tk`).
- Para generar paquetes: dependencias de `requirements.txt`, además de `appimagetool` para el AppImage de Linux.

## Instalación desde el código fuente

Clona el repositorio y entra en la carpeta:

```bash
git clone https://github.com/K3NYEL/klp_system.git
cd klp_system
```

Crea y activa un entorno virtual.

**Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Inicia la aplicación:

```bash
python main.py
```

Si Tkinter no está disponible en Linux, instala el paquete Tk de tu distribución y vuelve a ejecutar la aplicación.

Consulta [INSTALLATION.md](INSTALLATION.md) para instrucciones de instalación y compilación por plataforma.

## Estructura del proyecto

```text
klp_system/
├── app/
│   ├── auth/       # Autenticación, contraseñas, roles y permisos
│   ├── core/       # Base de datos, rutas, auditoría, respaldos y utilidades
│   ├── services/   # Operaciones de negocio
│   ├── setup/      # Inicialización y comprobación de dependencias
│   └── ui/         # Ventanas, vistas, estilos y widgets
├── main.py         # Punto de entrada
├── requirements.txt
├── klp_system.spec # Configuración de PyInstaller
├── build.sh        # Compilación Linux / AppImage
└── build.bat       # Compilación Windows
```

La descripción de responsabilidades y del flujo de ejecución está en [ARCHITECTURE.md](ARCHITECTURE.md).

## Datos y copias de seguridad

En desarrollo, la aplicación resuelve su directorio de datos desde la raíz del proyecto. En una compilación, utiliza el directorio de datos del usuario:

- Windows: `%LOCALAPPDATA%\KLPSystem` (o `%APPDATA%\KLPSystem` como alternativa).
- Linux: `$XDG_DATA_HOME/KLPSystem`; si no está definido, `~/.local/share/KLPSystem`.

La base de datos principal se llama `facturacion.db`. Conserva copias de seguridad fuera del repositorio y no compartas bases de datos reales, credenciales ni datos personales.

## Contribuir

Antes de modificar el proyecto, lee [CONTRIBUTING.md](CONTRIBUTING.md). Las propuestas deben describir el cambio, su alcance y las pruebas manuales realizadas.

## Licencia

El repositorio no contiene actualmente un archivo de licencia que conceda permisos de redistribución o modificación. La publicación del código en GitHub no debe interpretarse por sí sola como una licencia de software libre. Para consultas sobre uso o distribución, contacta con el mantenedor.
