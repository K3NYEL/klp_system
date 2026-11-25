# Arquitectura de KLP SYSTEM

## Visión general

KLP SYSTEM es una aplicación de escritorio Python. La interfaz está construida con Tkinter y ttk, la persistencia utiliza SQLite y los documentos PDF se generan con ReportLab.

El código se organiza por responsabilidades en `app/`. El punto de entrada está en `main.py`.

## Estructura

```text
app/
├── auth/
│   ├── authorization.py
│   ├── login_window.py
│   ├── password_window.py
│   ├── register_window.py
│   └── security.py
├── core/
│   ├── audit.py
│   ├── backup.py
│   ├── database.py
│   ├── inventory.py
│   ├── paths.py
│   ├── reports.py
│   ├── ui.py
│   └── user_management.py
├── services/
│   ├── customers_service.py
│   ├── invoice_service.py
│   └── products_service.py
├── setup/
│   ├── dependencies.py
│   └── initializer.py
└── ui/
    ├── components/
    ├── dashboard_cash_view.py
    ├── inventory_view.py
    ├── main_window.py
    ├── splash_screen.py
    ├── styles.py
    ├── theme.py
    ├── tk_widgets.py
    └── user_management_view.py
```

## Responsabilidades

### Punto de entrada

- `main.py` inicia la pantalla de presentación, abre el inicio de sesión y construye la ventana principal después de una autenticación correcta.
- La ventana principal se implementa en `app/ui/main_window.py`.

### Interfaz

- `app/ui/` contiene ventanas, vistas, componentes reutilizables, estilos y adaptación de widgets Tkinter/ttk.
- `tk_widgets.py` ofrece una capa de widgets utilizada por las vistas.
- `main_window.py` coordina la navegación y la composición de las secciones principales.

### Autenticación y autorización

- `app/auth/login_window.py` gestiona el inicio de sesión.
- `security.py` crea y verifica hashes de contraseñas y mantiene compatibilidad con hashes heredados.
- `authorization.py` consulta los permisos asociados a los roles.
- Las ventanas de registro y contraseña están separadas en sus propios módulos.

### Núcleo

- `database.py` abre conexiones SQLite, configura claves foráneas y modo WAL, crea el esquema y aplica migraciones aditivas.
- `paths.py` determina dónde se almacenan los datos de la aplicación en desarrollo y en modo empaquetado.
- `audit.py` registra eventos de auditoría.
- `backup.py` crea, valida y restaura copias de seguridad de SQLite.
- `inventory.py`, `reports.py` y `user_management.py` contienen utilidades centrales para sus respectivos dominios.

### Servicios

- `customers_service.py` concentra operaciones de clientes.
- `products_service.py` concentra operaciones de productos.
- `invoice_service.py` contiene cálculos y consultas de apoyo para facturación.

### Inicialización

- `setup/dependencies.py` lee `requirements.txt` y comprueba versiones e importaciones.
- `setup/initializer.py` prepara directorios, verifica dependencias y conecta la base de datos antes de continuar con el inicio.

## Flujo de inicio

```text
main.py
  |
  v
SplashScreen
  |
  v
LoginWindow
  |
  | autenticación correcta
  v
SistemaFacturacion
  |
  v
Vistas y módulos de la aplicación
```

Durante la preparación inicial se comprueban las dependencias, se crean los directorios necesarios y se inicializa la base de datos.

## Persistencia y migraciones

SQLite es la base de datos local. La conexión se crea mediante `connect_database()` en `app/core/database.py`.

Las modificaciones del esquema deben ser compatibles con bases de datos existentes. Las migraciones actuales crean tablas si no existen y agregan columnas faltantes; cualquier cambio futuro debe preservar la información ya almacenada y probarse con una copia de una base de datos anterior.

## Empaquetado

- `klp_system.spec` define los recursos y el ejecutable de PyInstaller.
- `build.sh` prepara el ejecutable Linux y el AppImage.
- `build.bat` genera el ejecutable Windows.

## Límites actuales de esta documentación

Esta descripción refleja la estructura y los módulos presentes en la rama documentada. No implica que todos los módulos estén completos ni que exista cobertura automatizada para todos los flujos. Actualiza este documento cuando cambien las responsabilidades o la estructura del proyecto.
