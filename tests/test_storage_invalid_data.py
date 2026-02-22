import tempfile
import unittest
from pathlib import Path

from source.customer import CustomerRepository
from source.hotel import HotelRepository


class TestInvalidDataHandling(unittest.TestCase):
    def test_invalid_json_file_does_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "customers.json"
            # JSON corrupto
            path.write_text("{esto no es json", encoding="utf-8")

            repo = CustomerRepository(path)
            # No debe explotar, debe continuar y permitir crear
            customer = repo.create_customer("Joel", "joel@test.com")
            self.assertTrue(customer.customer_id)

    def test_invalid_schema_records_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "hotels.json"
            # Lista con registros inválidos
            path.write_text(
                '[{"hotel_id": "1", "name": "X"}]',
                encoding="utf-8",
            )

            repo = HotelRepository(path)
            # Debe ignorar el registro inválido y permitir crear uno válido
            hotel = repo.create_hotel("Ok", "CDMX", 3)
            self.assertTrue(hotel.hotel_id)