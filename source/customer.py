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


class CustomerRepository:
    """Repositorio de Customers persistido en JSON."""

    def __init__(self, data_path: Path) -> None:
        self._path = data_path

    def _validate_record(self, record: Dict[str, Any]) -> Optional[Customer]:
        """Valida y convierte un registro a Customer. Si es inválido, regresa None."""
        missing = [f for f in REQUIRED_FIELDS if f not in record]
        if missing:
            print(  # noqa: T201
                f"[ERROR] Customer inválido (faltan {missing}). Se ignora registro."
            )
            return None

        customer_id = str(record["customer_id"]).strip()
        name = str(record["name"]).strip()
        email = str(record["email"]).strip()

        if not customer_id or not name or not email:
            print(  # noqa: T201
                "[ERROR] Customer inválido (campos vacíos). Se ignora registro."
            )
            return None

        return Customer(customer_id=customer_id, name=name, email=email)

    def _load_all(self) -> List[Customer]:
        records = load_json_list(self._path)
        customers: List[Customer] = []
        for record in records:
            customer = self._validate_record(record)
            if customer is not None:
                customers.append(customer)
        return customers

    def _save_all(self, customers: List[Customer]) -> None:
        save_json_list(self._path, [asdict(c) for c in customers])

    def create_customer(self, name: str, email: str) -> Customer:
        """Crea un Customer y lo persiste."""
        name = name.strip()
        email = email.strip()

        if not name:
            raise ValidationError("El nombre del cliente no puede estar vacío.")
        if "@" not in email or "." not in email:
            raise ValidationError("El email del cliente no es válido.")

        customer = Customer(customer_id=str(uuid4()), name=name, email=email)
        customers = self._load_all()
        customers.append(customer)
        self._save_all(customers)
        return customer

    def get_customer(self, customer_id: str) -> Customer:
        """Obtiene un Customer por id."""
        customers = self._load_all()
        for customer in customers:
            if customer.customer_id == customer_id:
                return customer
        raise NotFoundError(f"Customer no encontrado: {customer_id}")

    def display_customer(self, customer_id: str) -> str:
        """Regresa un string con información del cliente (para consola/log)."""
        customer = self.get_customer(customer_id)
        return f"Customer[{customer.customer_id}] {customer.name} <{customer.email}>"

    def modify_customer(self, customer_id: str, name: str, email: str) -> Customer:
        """Modifica datos del cliente."""
        name = name.strip()
        email = email.strip()

        if not name:
            raise ValidationError("El nombre del cliente no puede estar vacío.")
        if "@" not in email or "." not in email:
            raise ValidationError("El email del cliente no es válido.")

        customers = self._load_all()
        updated: List[Customer] = []
        found = False
        for customer in customers:
            if customer.customer_id == customer_id:
                updated.append(Customer(customer_id=customer_id, name=name, email=email))
                found = True
            else:
                updated.append(customer)

        if not found:
            raise NotFoundError(f"Customer no encontrado: {customer_id}")

        self._save_all(updated)
        return self.get_customer(customer_id)

    def delete_customer(self, customer_id: str) -> None:
        """Elimina un cliente por id."""
        customers = self._load_all()
        new_list = [c for c in customers if c.customer_id != customer_id]
        if len(new_list) == len(customers):
            raise NotFoundError(f"Customer no encontrado: {customer_id}")
        self._save_all(new_list)