from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from app.core.database import connect_database
from app.core.paths import application_path
from app.setup.dependencies import check_dependencies


class Initializer:
    """
    Coordina las tareas necesarias para preparar KLP SYSTEM
    antes de mostrar el inicio de sesión.
    """

    def __init__(
        self,
        progress_callback: Callable[[int, str], None] | None = None,
    ):
        self.progress_callback = progress_callback
        self.base_path = Path(application_path())

    # =============================================================
    # PROGRESO
    # =============================================================

    def update_progress(
        self,
        progress: int,
        message: str,
    ) -> None:
        """
        Envía una actualización de progreso al SplashScreen.
        """

        if self.progress_callback:
            self.progress_callback(
                progress,
                message,
            )

    # =============================================================
    # EJECUTAR
    # =============================================================

    def run(self) -> bool:
        """
        Ejecuta todas las tareas necesarias para preparar
        KLP SYSTEM.

        Devuelve True si la inicialización terminó correctamente.
        """

        try:
            # =====================================================
            # 1. INICIO
            # =====================================================

            self.update_progress(
                5,
                "Iniciando sistema...",
            )

            # =====================================================
            # 2. PREPARAR DIRECTORIO DE DATOS
            # =====================================================

            self.update_progress(
                10,
                "Preparando directorios...",
            )

            self.base_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            # =====================================================
            # 3. DEPENDENCIAS
            # =====================================================

            self.update_progress(
                15,
                "Verificando dependencias...",
            )

            dependencies = check_dependencies()

            total = len(dependencies)

            if total == 0:
                raise RuntimeError(
                    "No se encontraron dependencias en requirements.txt."
                )

            for index, dependency in enumerate(
                dependencies,
                start=1,
            ):
                progress = 15 + int(
                    (index / total) * 30
                )

                if not dependency.installed:
                    self.update_progress(
                        progress,
                        f"Falta la dependencia: {dependency.name}",
                    )

                    return False

                self.update_progress(
                    progress,
                    f"Verificando {dependency.name}...",
                )

            self.update_progress(
                45,
                "Dependencias verificadas.",
            )

            # =====================================================
            # 4. CONFIGURACIÓN
            # =====================================================

            self.update_progress(
                50,
                "Verificando configuración...",
            )

            config_path = self.base_path / "config"

            config_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.update_progress(
                60,
                "Configuración preparada.",
            )

            # =====================================================
            # 5. BASE DE DATOS
            # =====================================================

            self.update_progress(
                65,
                "Inicializando base de datos...",
            )

            database_path = (
                self.base_path / "facturacion.db"
            )

            connection = None

            try:
                connection = connect_database(
                    database_path
                )

                # La llamada a connect_database()
                # ejecuta las migraciones y crea
                # las tablas necesarias.
                connection.execute(
                    "SELECT 1"
                )

            finally:
                if connection:
                    connection.close()

            self.update_progress(
                82,
                "Base de datos preparada.",
            )

            # =====================================================
            # 6. RECURSOS
            # =====================================================

            self.update_progress(
                87,
                "Verificando recursos...",
            )

            assets_path = self.base_path / "assets"

            assets_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.update_progress(
                92,
                "Recursos preparados.",
            )

            # =====================================================
            # 7. FINAL
            # =====================================================

            self.update_progress(
                97,
                "Preparando interfaz...",
            )

            self.update_progress(
                100,
                "Sistema listo.",
            )

            return True

        except Exception as error:
            import traceback

            print("\n" + "=" * 70)
            print("ERROR DURANTE LA INICIALIZACIÓN DE KLP SYSTEM")
            print("=" * 70)
            print(f"{type(error).__name__}: {error}")
            traceback.print_exc()
            print("=" * 70 + "\n")

            self.update_progress(
                0,
                f"Error: {error}",
            )

            return False