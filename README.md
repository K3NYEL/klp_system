# KLP SYSTEM

**Sistema de gestión y facturación de escritorio desarrollado en Python.**

KLP SYSTEM es una aplicación de escritorio orientada a la gestión de operaciones de facturación, con almacenamiento local y una interfaz gráfica desarrollada con CustomTkinter.

El proyecto está actualmente **en desarrollo** y cuenta con herramientas para ejecución desde código fuente, pruebas automatizadas y generación de ejecutables mediante PyInstaller.

---

## Tecnologías

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-1f6feb?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge\&logo=sqlite\&logoColor=white)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF-8A2BE2?style=for-the-badge)
![PyInstaller](https://img.shields.io/badge/PyInstaller-Build-000000?style=for-the-badge)

---

## Características

* Gestión de operaciones de facturación.
* Interfaz gráfica de escritorio.
* Almacenamiento local.
* Sistema de autenticación de usuarios.
* Pruebas automatizadas mediante `unittest`.
* Generación de documentos PDF mediante ReportLab.
* Generación de ejecutables mediante PyInstaller.
* Compilación para Linux.
* Compilación para Windows.
* Ejecución mediante entorno virtual de Python.

---

## Requisitos

Para ejecutar KLP SYSTEM desde el código fuente necesitas:

* Python 3
* `pip`
* Entorno virtual de Python
* Dependencias del proyecto

Las dependencias principales se encuentran definidas en:

```text
requirements.txt
```

Actualmente incluyen:

* `customtkinter`
* `reportlab`
* `pyinstaller`

---

## Instalación

Clona el repositorio:

```bash
git clone https://github.com/K3NYEL/klp_system.git
```

Entra al directorio:

```bash
cd klp_system
```

Crea un entorno virtual:

```bash
python3 -m venv .venv
```

Activa el entorno virtual:

### Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

---

## Ejecución

Una vez instaladas las dependencias, puedes iniciar la aplicación directamente desde el código fuente.

### Linux

```bash
.venv/bin/python main.py
```

También puedes activar primero el entorno virtual:

```bash
source .venv/bin/activate
python main.py
```

El archivo `main.py` inicia el flujo de autenticación y, después de un inicio de sesión exitoso, carga la aplicación principal.

---

## Pruebas

Las pruebas del proyecto pueden ejecutarse utilizando el módulo `unittest`:

```bash
.venv/bin/python -m unittest discover -s tests
```

Esto permite ejecutar automáticamente las pruebas encontradas dentro del directorio `tests`.

---

## Generación del ejecutable

KLP SYSTEM utiliza **PyInstaller** para generar ejecutables independientes.

### Linux

El proyecto incluye un script de compilación:

```bash
bash build.sh
```

El script utiliza el PyInstaller del entorno virtual cuando está disponible y genera:

```text
dist/facturacion
```

Para iniciar el ejecutable:

```bash
./dist/facturacion
```

También puedes utilizar:

```bash
bash run.sh
```

El proceso de compilación limpia determinados archivos generados anteriormente y verifica que el ejecutable haya sido creado correctamente.

### Windows

En Windows puedes utilizar:

```text
build.bat
```

El proceso utiliza la configuración:

```text
facturacion_completa.spec
```

y genera:

```text
dist/facturacion.exe
```

El script también comprueba el resultado de PyInstaller e informa si la compilación finalizó correctamente.

---

## PyInstaller

La configuración de compilación se encuentra en:

```text
facturacion_completa.spec
```

Esta configuración utiliza `main.py` como punto de entrada y empaqueta recursos de la aplicación, incluyendo el icono utilizado por el programa.

El ejecutable se genera con el nombre:

```text
facturacion
```

en Linux, y:

```text
facturacion.exe
```

en Windows.

---

## 🖥️ Compatibilidad

El ejecutable generado por PyInstaller debe compilarse para la plataforma y arquitectura de destino.

Por lo tanto, un ejecutable generado en Linux no debe considerarse automáticamente compatible con Windows, y viceversa.

Para distribuir KLP SYSTEM en otra plataforma o arquitectura, se recomienda realizar la compilación correspondiente en un entorno compatible.

---

## Estructura del proyecto

La estructura principal del repositorio actualmente incluye:

```text
klp_system/
├── app/
├── facturas/
├── tests/
├── .vscode/
├── main.py
├── requirements.txt
├── build.sh
├── build.bat
├── run.sh
├── facturacion_completa.spec
├── Facturacion.desktop
├── LICENSE
└── README.md
```

---

## Base de datos

KLP SYSTEM utiliza almacenamiento local para la información de la aplicación.

La base de datos utilizada durante el desarrollo **no se incluye en el ejecutable final** durante el proceso de compilación. Los scripts de construcción eliminan los archivos de base de datos de desarrollo de `dist/` antes de ejecutar PyInstaller.

---

## Estado del proyecto

> **KLP SYSTEM se encuentra actualmente en desarrollo.**

La arquitectura y las funcionalidades del sistema continúan evolucionando y pueden cambiar entre versiones.

---

## Licencia

Este proyecto se distribuye bajo la **MIT License**.

Copyright © 2026 **Kenyel**

Consulta el archivo [`LICENSE`](./LICENSE) para conocer los términos completos de la licencia.
