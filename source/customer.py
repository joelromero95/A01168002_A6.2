"""Modelo y operaciones de Customer con persistencia JSON."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .exceptions import NotFoundError, ValidationError
from .storage import load_json_list, save_json_list


REQUIRED_FIELDS = ("customer_id", "name", "email")


@dataclass(frozen=True)
class Customer:
    """Representa un cliente del sistema."""

    customer_id: str
    name: str
    email: str