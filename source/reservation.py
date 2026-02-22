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