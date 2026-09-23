from __future__ import annotations

import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from app.core.paths import application_path


# ============================================================
# CONFIGURACIÓN
# ============================================================

PACKAGE_MODULES = {
    "customtkinter": "customtkinter",
    "reportlab": "reportlab",
    "pyinstaller": "PyInstaller",
}


# ============================================================
# MODELO DE RESULTADO
# ============================================================

@dataclass
class DependencyResult:
    """Resultado de la comprobación de una dependencia."""

    name: str
    module: str
    requirement: str
    installed: bool
    required: bool = True


# ============================================================
# DETECCIÓN DEL ENTORNO
# ============================================================

def is_frozen() -> bool:
    """
    Indica si KLP SYSTEM está ejecutándose como
    una aplicación compilada con PyInstaller.
    """

    return getattr(sys, "frozen", False)


# ============================================================
# REQUIREMENTS
# ============================================================

def get_requirements_path() -> Path:
    """
    Obtiene la ruta de requirements.txt.

    En desarrollo:
        ~/Escritorio/klp_system/requirements.txt
    """

    return Path(application_path()) / "requirements.txt"


def read_requirements() -> list[str]:
    """
    Lee las dependencias definidas en requirements.txt.

    Ignora:
        - líneas vacías
        - comentarios
    """

    requirements_path = get_requirements_path()

    if not requirements_path.exists():
        raise FileNotFoundError(
            f"No se encontró requirements.txt: "
            f"{requirements_path}"
        )

    requirements: list[str] = []

    with requirements_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            requirements.append(line)

    return requirements


# ============================================================
# NOMBRES DE PAQUETES
# ============================================================

def get_package_name(requirement: str) -> str:
    """
    Extrae el nombre del paquete desde una línea
    de requirements.txt.

    Ejemplo:

        customtkinter>=5.2,<7

    devuelve:

        customtkinter
    """

    match = re.match(
        r"^([A-Za-z0-9_.-]+)",
        requirement,
    )

    if not match:
        return requirement

    return match.group(1)


def get_module_name(package_name: str) -> str:
    """
    Convierte el nombre del paquete al nombre
    real del módulo importable.

    Ejemplo:

        PyInstaller -> PyInstaller
        customtkinter -> customtkinter
        reportlab -> reportlab
    """

    normalized_name = package_name.lower()

    return PACKAGE_MODULES.get(
        normalized_name,
        package_name,
    )


# ============================================================
# COMPROBACIÓN INDIVIDUAL
# ============================================================

def check_package(
    package_name: str,
    requirement: str,
) -> DependencyResult:
    """
    Comprueba si un paquete puede ser encontrado
    por el intérprete actual.
    """

    module_name = get_module_name(
        package_name
    )

    installed = (
        importlib.util.find_spec(
            module_name
        )
        is not None
    )

    return DependencyResult(
        name=package_name,
        module=module_name,
        requirement=requirement,
        installed=installed,
    )


# ============================================================
# COMPROBACIÓN GENERAL
# ============================================================

def check_dependencies() -> list[DependencyResult]:
    """
    Comprueba las dependencias necesarias para KLP SYSTEM.

    En desarrollo:
        utiliza requirements.txt.

    En una aplicación compilada con PyInstaller:
        las dependencias ya están incluidas
        dentro del ejecutable.

        Por lo tanto, NO se necesita
        requirements.txt.
    """

    # --------------------------------------------------------
    # APLICACIÓN COMPILADA
    # --------------------------------------------------------

    if is_frozen():
        return [
            DependencyResult(
                name="KLP SYSTEM",
                module="",
                requirement="bundled",
                installed=True,
            )
        ]

    # --------------------------------------------------------
    # ENTORNO DE DESARROLLO
    # --------------------------------------------------------

    requirements = read_requirements()

    results: list[DependencyResult] = []

    for requirement in requirements:

        package_name = get_package_name(
            requirement
        )

        result = check_package(
            package_name,
            requirement,
        )

        results.append(result)

    return results


# ============================================================
# ESTADO GENERAL
# ============================================================

def dependencies_ready() -> bool:
    """
    Devuelve True cuando todas las dependencias
    obligatorias están disponibles.
    """

    results = check_dependencies()

    return all(
        result.installed
        for result in results
        if result.required
    )


def get_missing_dependencies() -> list[DependencyResult]:
    """
    Devuelve una lista con las dependencias
    obligatorias que no están instaladas.
    """

    results = check_dependencies()

    return [
        result
        for result in results
        if result.required
        and not result.installed
    ]