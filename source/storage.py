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


def load_json_list(path: Path) -> List[Dict[str, Any]]:
    """Carga una lista de diccionarios desde JSON.

    Si el archivo no existe o está corrupto, se reporta y se regresa [].
    """
    if not path.exists():
        _safe_print(f"[WARN] Archivo no existe: {path}. Se usará lista vacía.")
        return []

    try:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            _safe_print(f"[WARN] Archivo vacío: {path}. Se usará lista vacía.")
            return []

        data = json.loads(raw)
        if not isinstance(data, list):
            _safe_print(
                f"[ERROR] JSON inválido (no es lista) en {path}. Se usará []."
            )
            return []
        # Filtramos solo elementos que sean dict
        cleaned: List[Dict[str, Any]] = []
        for idx, item in enumerate(data):
            if isinstance(item, dict):
                cleaned.append(item)
            else:
                _safe_print(
                    f"[ERROR] Registro no dict en {path} índice={idx}. Se ignora."
                )
        return cleaned
    except (json.JSONDecodeError, OSError) as exc:
        _safe_print(f"[ERROR] No se pudo leer {path}: {exc}. Se usará [].")
        return []


def save_json_list(path: Path, data: List[Dict[str, Any]]) -> None:
    """Guarda una lista de diccionarios en JSON de forma segura."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(data, indent=2, ensure_ascii=False)
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        # Requerimiento: no detener ejecución. Reportamos.
        _safe_print(f"[ERROR] No se pudo escribir {path}: {exc}.")
