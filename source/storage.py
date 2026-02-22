"""Capa de persistencia en archivos JSON.

Requisitos importantes:
- Manejar archivos inválidos sin detener la ejecución.
- Imprimir el error en consola y continuar.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _safe_print(message: str) -> None:
    """Imprime mensajes de error/advertencia sin romper el flujo."""
    print(message)  # noqa: T201 (permitimos print por requerimiento)
