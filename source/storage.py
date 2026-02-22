"""Capa de persistencia en archivos JSON.

Requisitos importantes:
- Manejar archivos inválidos sin detener la ejecución.
- Imprimir el error en consola y continuar.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List