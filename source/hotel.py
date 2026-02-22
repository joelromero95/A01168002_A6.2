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

    def _save_all(self, hotels: List[Hotel]) -> None:
        save_json_list(self._path, [asdict(h) for h in hotels])

    def create_hotel(self, name: str, city: str, total_rooms: int) -> Hotel:
        """Crea un hotel y lo persiste."""
        name = name.strip()
        city = city.strip()
        if not name:
            raise ValidationError("El nombre del hotel no puede estar vacío.")
        if not city:
            raise ValidationError("La ciudad no puede estar vacía.")
        if total_rooms <= 0:
            raise ValidationError("total_rooms debe ser mayor que 0.")

        hotel = Hotel(
            hotel_id=str(uuid4()),
            name=name,
            city=city,
            total_rooms=total_rooms,
            reserved_rooms=0,
        )
        hotels = self._load_all()
        hotels.append(hotel)
        self._save_all(hotels)
        return hotel

    def get_hotel(self, hotel_id: str) -> Hotel:
        hotels = self._load_all()
        for hotel in hotels:
            if hotel.hotel_id == hotel_id:
                return hotel
        raise NotFoundError(f"Hotel no encontrado: {hotel_id}")

    def display_hotel(self, hotel_id: str) -> str:
        hotel = self.get_hotel(hotel_id)
        return (
            f"Hotel[{hotel.hotel_id}] {hotel.name} ({hotel.city}) "
            f"rooms: {hotel.reserved_rooms}/{hotel.total_rooms} "
            f"available: {hotel.available_rooms}"
        )

    def modify_hotel(self, hotel_id: str, name: str, city: str, total_rooms: int) -> Hotel:
        """Modifica info del hotel sin perder consistencia."""
        name = name.strip()
        city = city.strip()

        if not name:
            raise ValidationError("El nombre del hotel no puede estar vacío.")
        if not city:
            raise ValidationError("La ciudad no puede estar vacía.")
        if total_rooms <= 0:
            raise ValidationError("total_rooms debe ser mayor que 0.")

        hotels = self._load_all()
        updated: List[Hotel] = []
        found = False

        for hotel in hotels:
            if hotel.hotel_id == hotel_id:
                if hotel.reserved_rooms > total_rooms:
                    raise ValidationError(
                        "No puedes reducir total_rooms por debajo de reserved_rooms."
                    )
                updated.append(
                    Hotel(
                        hotel_id=hotel_id,
                        name=name,
                        city=city,
                        total_rooms=total_rooms,
                        reserved_rooms=hotel.reserved_rooms,
                    )
                )
                found = True
            else:
                updated.append(hotel)

        if not found:
            raise NotFoundError(f"Hotel no encontrado: {hotel_id}")

        self._save_all(updated)
        return self.get_hotel(hotel_id)

