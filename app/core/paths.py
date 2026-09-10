import os
import sys
from pathlib import Path


def application_path():
    """Returns the writable data directory for source and frozen runs.

    Frozen builds keep mutable data outside the executable directory so a clean
    build cannot accidentally reuse the developer database.
    """
    if not getattr(sys, "frozen", False):
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if os.name == "nt":
        parent = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    else:
        parent = os.environ.get("XDG_DATA_HOME")

    if not parent:
        parent = os.path.join(os.path.expanduser("~"), ".local", "share")

    data_path = Path(parent) / "FacturacionApp"
    data_path.mkdir(parents=True, exist_ok=True)
    return str(data_path)
