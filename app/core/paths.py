import os
import sys
from pathlib import Path


APP_DATA_DIR = "KLPSystem"


def application_path() -> str:
    """
    Devuelve el directorio de datos escribible de KLP SYSTEM.

    En desarrollo:
        utiliza la raíz del proyecto.

    En una aplicación compilada:
        utiliza el directorio de datos del usuario.
    """

    if not getattr(sys, "frozen", False):
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )
        )

    if os.name == "nt":
        parent = (
            os.environ.get("LOCALAPPDATA")
            or os.environ.get("APPDATA")
        )
    else:
        parent = os.environ.get(
            "XDG_DATA_HOME"
        )

    if not parent:
        parent = os.path.join(
            os.path.expanduser("~"),
            ".local",
            "share",
        )

    data_path = Path(parent) / APP_DATA_DIR

    data_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return str(data_path)