"""Modelo y operaciones de Hotel con persistencia JSON."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .exceptions import NotFoundError, ValidationError
from .storage import load_json_list, save_json_list


REQUIRED_FIELDS = ("hotel_id", "name", "city", "total_rooms", "reserved_rooms")


@dataclass(frozen=True)
class Hotel:
    """Representa un hotel del sistema."""

    hotel_id: str
    name: str
    city: str
    total_rooms: int
    reserved_rooms: int

    @property
    def available_rooms(self) -> int:
        """Cuartos disponibles en el hotel."""
        return max(0, self.total_rooms - self.reserved_rooms)


class HotelRepository:
    """Repositorio de Hotels persistido en JSON."""

    def __init__(self, data_path: Path) -> None:
        self._path = data_path



