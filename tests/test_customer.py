"""Unit tests for CustomerRepository (JSON persistence).

Covers CRUD operations, validation rules, and resilience to invalid data in
the persisted JSON file.
"""
import json
import tempfile
import unittest
from pathlib import Path

from source.customer import CustomerRepository
from source.exceptions import NotFoundError, ValidationError


class TestCustomerRepository(unittest.TestCase):
    """Pruebas unitarias de CustomerRepository."""

    def setUp(self) -> None:
        """Crea un entorno aislado por cada test."""
        # pylint: disable=consider-using-with
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.customers_path = Path(self.tmpdir.name) / "customers.json"
        self.repo = CustomerRepository(self.customers_path)

    def _write_json(self, items) -> None:
        """Helper: escribe lista de dicts como JSON en el archivo temporal."""
        self.customers_path.write_text(
            json.dumps(items, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def test_create_customer_persists_record(self) -> None:
        """Debe crear un customer válido y persistirlo en JSON."""
        created = self.repo.create_customer("Joel", "joel@test.com")

        # Verificar que se escribió a disco
        data = json.loads(self.customers_path.read_text(encoding="utf-8"))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["customer_id"], created.customer_id)
        self.assertEqual(data[0]["name"], "Joel")
        self.assertEqual(data[0]["email"], "joel@test.com")

    def test_create_customer_invalid_name_raises(self) -> None:
        """Nombre vacío debe disparar ValidationError."""
        with self.assertRaises(ValidationError):
            self.repo.create_customer("   ", "joel@test.com")

    def test_create_customer_invalid_email_raises(self) -> None:
        """Email inválido debe disparar ValidationError."""
        with self.assertRaises(ValidationError):
            self.repo.create_customer("Joel", "correo_invalido")

    def test_get_customer_not_found_raises(self) -> None:
        """Si no existe el id, debe disparar NotFoundError."""
        with self.assertRaises(NotFoundError):
            self.repo.get_customer("no-existe")

    def test_display_customer_format(self) -> None:
        """display_customer debe regresar un string con el formato esperado."""
        created = self.repo.create_customer("Ana", "ana@test.com")
        text = self.repo.display_customer(created.customer_id)
        self.assertIn("Customer[", text)
        self.assertIn("Ana", text)
        self.assertIn("<ana@test.com>", text)

    def test_modify_customer_updates_record(self) -> None:
        """Debe modificar name/email si el customer existe."""
        created = self.repo.create_customer("A", "a@test.com")
        updated = self.repo.modify_customer(created.customer_id, "B", "b@test.com")
        self.assertEqual(updated.name, "B")
        self.assertEqual(updated.email, "b@test.com")

        # Verificar persistencia
        reloaded = self.repo.get_customer(created.customer_id)
        self.assertEqual(reloaded.name, "B")
        self.assertEqual(reloaded.email, "b@test.com")

    def test_modify_customer_not_found_raises(self) -> None:
        """Modificar un id inexistente debe disparar NotFoundError."""
        with self.assertRaises(NotFoundError):
            self.repo.modify_customer("no-existe", "X", "x@test.com")

    def test_modify_customer_invalid_email_raises(self) -> None:
        """Modificar con email inválido debe disparar ValidationError."""
        created = self.repo.create_customer("A", "a@test.com")
        with self.assertRaises(ValidationError):
            self.repo.modify_customer(created.customer_id, "A", "email_mal")

    def test_delete_customer_removes_record(self) -> None:
        """delete_customer debe eliminar el registro."""
        created = self.repo.create_customer("A", "a@test.com")
        self.repo.delete_customer(created.customer_id)

        with self.assertRaises(NotFoundError):
            self.repo.get_customer(created.customer_id)

    def test_delete_customer_not_found_raises(self) -> None:
        """Eliminar un id inexistente debe disparar NotFoundError."""
        with self.assertRaises(NotFoundError):
            self.repo.delete_customer("no-existe")

    def test_load_all_ignores_invalid_records_from_json(self) -> None:
        """Debe ignorar registros inválidos del archivo y cargar solo los válidos."""
        # 2 válidos + 5 inválidos
        self._write_json(
            [
                {"customer_id": "c-001", "name": "Ana", "email": "ana@test.com"},
                {"customer_id": "c-002", "name": "Luis", "email": "luis@test.com"},
                {"customer_id": "bad-001", "name": "Sin Email"},
                {"customer_id": "bad-002", "email": "no.name@test.com"},
                {"customer_id": "   ", "name": "Id Vacio", "email": "x@test.com"},
                {"customer_id": "bad-004", "name": "Email Vacio", "email": ""},
                {"customer_id": "bad-005", "name": "   ", "email": "y@test.com"},
            ]
        )

        # Validamos indirectamente que _load_all filtró:
        # Intentar leer los válidos debe funcionar; inválidos deben no existir.
        c1 = self.repo.get_customer("c-001")
        c2 = self.repo.get_customer("c-002")
        self.assertEqual(c1.name, "Ana")
        self.assertEqual(c2.name, "Luis")

        with self.assertRaises(NotFoundError):
            self.repo.get_customer("bad-001")

    def test_load_all_with_non_list_json_is_safe(self) -> None:
        """Si el JSON no es lista, debe manejarlo sin crash (regresa vacío)."""
        self.customers_path.write_text('{"a": 1}', encoding="utf-8")
        with self.assertRaises(NotFoundError):
            self.repo.get_customer("cualquiera")
