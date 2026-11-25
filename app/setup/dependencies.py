from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from packaging.requirements import Requirement
from packaging.version import Version

from app.core.paths import application_path


PACKAGE_MODULES = {
    "reportlab": "reportlab",
    "pyinstaller": "PyInstaller",
    "pillow": "PIL",
    "pyinstaller-hooks-contrib": "pyinstaller_hooks_contrib",
    "charset-normalizer": "charset_normalizer",
    "altgraph": "altgraph",
    "setuptools": "setuptools",
    "packaging": "packaging",
}


@dataclass
class DependencyResult:
    name: str
    module: str
    requirement: str
    installed: bool
    required: bool = True


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_requirements_path() -> Path:
    return Path(application_path()) / "requirements.txt"


def read_requirements() -> list[str]:
    path = get_requirements_path()
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró requirements.txt: {path}")
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def get_package_name(requirement: str) -> str:
    return Requirement(requirement).name


def get_module_name(package_name: str) -> str:
    return PACKAGE_MODULES.get(package_name.lower(), package_name.replace("-", "_"))


def check_package(package_name: str, requirement: str) -> DependencyResult:
    parsed = Requirement(requirement)
    module_name = get_module_name(package_name)
    installed = False
    if parsed.marker is None or parsed.marker.evaluate():
        try:
            installed_version = Version(version(package_name))
            installed = parsed.specifier.contains(installed_version, prereleases=True)
        except (PackageNotFoundError, ValueError):
            installed = False
        if installed and importlib.util.find_spec(module_name) is None:
            installed = False
    return DependencyResult(package_name, module_name, requirement, installed)


def check_dependencies() -> list[DependencyResult]:
    if is_frozen():
        return [DependencyResult("KLP SYSTEM", "", "bundled", True)]
    results = []
    for requirement in read_requirements():
        parsed = Requirement(requirement)
        if parsed.marker is not None and not parsed.marker.evaluate():
            continue
        results.append(check_package(parsed.name, requirement))
    return results


def dependencies_ready() -> bool:
    return all(result.installed for result in check_dependencies() if result.required)


def get_missing_dependencies() -> list[DependencyResult]:
    return [result for result in check_dependencies() if result.required and not result.installed]
