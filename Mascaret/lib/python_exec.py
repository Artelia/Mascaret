"""Helpers to resolve a reliable Python interpreter in PyQGIS contexts."""

import os
import shutil
import sys
from pathlib import Path


def resolve_python_executable():
    """Return a reliable Python interpreter path in PyQGIS contexts.

    Some deployments expose a QGIS launcher in sys.executable. We prefer a
    real Python binary and keep sys.executable only as a last resort.
    """
    candidates = []

    for env_var in ("PYTHON_EXECUTABLE", "QGIS_PYTHON_EXECUTABLE"):
        value = os.environ.get(env_var)
        if value:
            candidates.append(Path(value))

    stdlib_path = Path(os.__file__).resolve()
    py_name = "python.exe" if os.name == "nt" else "python3"
    candidates.append(stdlib_path.parents[1] / py_name)

    if sys.executable:
        candidates.append(Path(sys.executable))

    for candidate in candidates:
        name = candidate.name.lower()
        if candidate.exists() and "python" in name:
            return str(candidate)

    for cmd in ("python3", "python"):
        path = shutil.which(cmd)
        if path:
            return path

    return sys.executable
