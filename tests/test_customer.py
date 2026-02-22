import tempfile
import unittest
from pathlib import Path

from source.customer import CustomerRepository
from source.exceptions import NotFoundError, ValidationError


class TestCustomerRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.tmpdir.name) / "customers.json"
        self.repo = CustomerRepository(self.data_path)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_create_and_get_customer(self) -> None:
        created = self.repo.create_customer("Joel", "joel@test.com")
        fetched = self.repo.get_customer(created.customer_id)
        self.assertEqual(created, fetched)

    def test_create_customer_invalid_email(self) -> None:
        with self.assertRaises(ValidationError):
            self.repo.create_customer("Joel", "correo_invalido")

    def test_delete_customer_not_found(self) -> None:
        with self.assertRaises(NotFoundError):
            self.repo.delete_customer("no-existe")

    def test_modify_customer(self) -> None:
        created = self.repo.create_customer("A", "a@test.com")
        updated = self.repo.modify_customer(created.customer_id, "B", "b@test.com")
        self.assertEqual(updated.name, "B")
        self.assertEqual(updated.email, "b@test.com")