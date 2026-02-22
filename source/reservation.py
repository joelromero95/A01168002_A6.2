"""Modelo y operaciones de Reservation con persistencia JSON."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .customer import CustomerRepository
from .exceptions import NotFoundError, ValidationError
from .hotel import HotelRepository
from .storage import load_json_list, save_json_list


REQUIRED_FIELDS = ("reservation_id", "customer_id", "hotel_id")


@dataclass(frozen=True)
class Reservation:
    """Representa una reservación Customer-Hotel."""

    reservation_id: str
    customer_id: str
    hotel_id: str


class ReservationRepository:
    """Repositorio de Reservations persistido en JSON."""

    def __init__(
        self,
        data_path: Path,
        hotel_repo: HotelRepository,
        customer_repo: CustomerRepository,
    ) -> None:
        self._path = data_path
        self._hotel_repo = hotel_repo
        self._customer_repo = customer_repo

    def _validate_record(self, record: Dict[str, Any]) -> Optional[Reservation]:
        missing = [f for f in REQUIRED_FIELDS if f not in record]
        if missing:
            print(  # noqa: T201
                f"[ERROR] Reservation inválida (faltan {missing}). Se ignora."
            )
            return None

        reservation_id = str(record["reservation_id"]).strip()
        customer_id = str(record["customer_id"]).strip()
        hotel_id = str(record["hotel_id"]).strip()

        if not reservation_id or not customer_id or not hotel_id:
            print("[ERROR] Reservation inválida (campos vacíos). Se ignora.")  # noqa: T201
            return None

        return Reservation(
            reservation_id=reservation_id,
            customer_id=customer_id,
            hotel_id=hotel_id,
        )