# Instalación y compilación

Esta guía cubre la ejecución de KLP SYSTEM desde el código fuente y la generación de ejecutables.

## Requisitos generales

- Python 3.10 o posterior recomendado.
- Tkinter instalado y funcional.
- Git.
- Acceso a una terminal.

En Linux, instala también el paquete Tk de tu distribución. En Debian/Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk
```

## Obtener el código

```bash
git clone https://github.com/K3NYEL/klp_system.git
cd klp_system
```

Si vas a colaborar, cambia a la rama que te indique el mantenedor antes de instalar o modificar archivos.

## Entorno virtual

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

## Dependencias

Con el entorno virtual activo:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

El archivo raíz `requirements.txt` contiene las dependencias fijadas para el entorno de desarrollo y empaquetado. La aplicación también comprueba las dependencias declaradas allí durante su inicialización cuando se ejecuta desde el código fuente.

## Ejecutar

```bash
python main.py
```

El flujo de inicio previsto es pantalla de presentación, inicio de sesión y ventana principal. En el primer inicio, la aplicación prepara el directorio de datos y la base de datos.

## Compilar en Linux

Con el entorno virtual activo y las dependencias instaladas:

```bash
chmod +x build.sh
./build.sh
```

El script utiliza `klp_system.spec` para generar el ejecutable con PyInstaller y luego prepara un AppDir para crear el AppImage.

También necesitas `appimagetool`. Si no está en el PATH, indica su ubicación:

```bash
APPIMAGETOOL=/ruta/a/appimagetool ./build.sh
```

Salidas esperadas:

- Ejecutable: `dist/klp_system`
- AppImage: `releases/Linux/KLP-System-x86_64.AppImage`

## Compilar en Windows

Crea el entorno virtual e instala las dependencias como se explicó arriba. Después ejecuta:

```bat
build.bat
```

El script espera encontrar PyInstaller dentro de `.venv\Scripts\` y deja el ejecutable en:

```text
releases\Windows\klp_system.exe
```

## Datos de la aplicación

En modo desarrollo, los datos se guardan en la raíz del proyecto. En modo empaquetado, se usa el directorio de datos del usuario:

- Windows: `%LOCALAPPDATA%\KLPSystem`, con alternativa `%APPDATA%\KLPSystem`.
- Linux: `$XDG_DATA_HOME/KLPSystem`; si la variable no existe, `~/.local/share/KLPSystem`.

La base de datos principal es `facturacion.db`. Haz respaldos antes de probar migraciones o restauraciones. Nunca uses datos reales de clientes para pruebas compartidas.

## Problemas frecuentes

### No se puede importar Tkinter

En Linux instala el paquete Tk de tu distribución (por ejemplo, `python3-tk`). Comprueba la instalación con:

```bash
python -m tkinter
```

### No se encuentra PyInstaller

Activa el entorno virtual y ejecuta:

```bash
python -m pip install -r requirements.txt
```

### No se encuentra appimagetool

Instala AppImageTool y vuelve a ejecutar `build.sh`, o define la variable `APPIMAGETOOL` con la ruta al ejecutable.

### La compilación de Windows indica que falta .venv

Crea y activa el entorno virtual en la raíz del repositorio e instala las dependencias. El script de Windows requiere `.venv\Scripts\python.exe` y `.venv\Scripts\pyinstaller.exe`.
