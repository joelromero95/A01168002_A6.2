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

    def _validate_record(self, record: Dict[str, Any]) -> Optional[Hotel]:
        missing = [f for f in REQUIRED_FIELDS if f not in record]
        if missing:
            print(  # noqa: T201
                f"[ERROR] Hotel inválido (faltan {missing}). Se ignora registro."
            )
            return None

        hotel_id = str(record["hotel_id"]).strip()
        name = str(record["name"]).strip()
        city = str(record["city"]).strip()

        try:
            total_rooms = int(record["total_rooms"])
            reserved_rooms = int(record["reserved_rooms"])
        except (ValueError, TypeError):
            print("[ERROR] Hotel inválido (rooms no numéricas). Se ignora.")  # noqa: T201
            return None

        if not hotel_id or not name or not city:
            print("[ERROR] Hotel inválido (campos vacíos). Se ignora.")  # noqa: T201
            return None
        if total_rooms <= 0:
            print("[ERROR] Hotel inválido (total_rooms <= 0). Se ignora.")  # noqa: T201
            return None
        if reserved_rooms < 0 or reserved_rooms > total_rooms:
            print("[ERROR] Hotel inválido (reserved_rooms fuera de rango). Se ignora.")  # noqa: T201
            return None

        return Hotel(
            hotel_id=hotel_id,
            name=name,
            city=city,
            total_rooms=total_rooms,
            reserved_rooms=reserved_rooms,
        )

    def _load_all(self) -> List[Hotel]:
        records = load_json_list(self._path)
        hotels: List[Hotel] = []
        for record in records:
            hotel = self._validate_record(record)
            if hotel is not None:
                hotels.append(hotel)
        return hotels

