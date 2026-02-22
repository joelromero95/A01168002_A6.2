import tempfile
import unittest
from pathlib import Path

from source.customer import CustomerRepository
from source.exceptions import NotFoundError, ValidationError
from source.hotel import HotelRepository
from source.reservation import ReservationRepository


class TestReservationRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        base = Path(self.tmpdir.name)

        self.hotel_repo = HotelRepository(base / "hotels.json")
        self.customer_repo = CustomerRepository(base / "customers.json")
        self.res_repo = ReservationRepository(
            base / "reservations.json",
            hotel_repo=self.hotel_repo,
            customer_repo=self.customer_repo,
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_create_and_cancel_reservation(self) -> None:
        hotel = self.hotel_repo.create_hotel("H", "C", 1)
        customer = self.customer_repo.create_customer("N", "n@test.com")

        reservation = self.res_repo.create_reservation(customer.customer_id, hotel.hotel_id)
        self.assertIn("Reservation", self.res_repo.display_reservation(reservation.reservation_id))

        self.res_repo.cancel_reservation(reservation.reservation_id)

        # Ya no existe
        with self.assertRaises(NotFoundError):
            self.res_repo.display_reservation(reservation.reservation_id)

    def test_create_reservation_no_rooms(self) -> None:
        hotel = self.hotel_repo.create_hotel("H", "C", 1)
        customer = self.customer_repo.create_customer("N", "n@test.com")

        _ = self.res_repo.create_reservation(customer.customer_id, hotel.hotel_id)
        with self.assertRaises(ValidationError):
            self.res_repo.create_reservation(customer.customer_id, hotel.hotel_id)

    def test_cancel_reservation_not_found(self) -> None:
        with self.assertRaises(NotFoundError):
            self.res_repo.cancel_reservation("no-existe")