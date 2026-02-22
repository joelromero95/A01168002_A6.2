import tempfile
import unittest
from pathlib import Path

from source.exceptions import NotFoundError, ValidationError
from source.hotel import HotelRepository


class TestHotelRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.tmpdir.name) / "hotels.json"
        self.repo = HotelRepository(self.data_path)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_create_and_display_hotel(self) -> None:
        hotel = self.repo.create_hotel("Hilton", "CDMX", 10)
        info = self.repo.display_hotel(hotel.hotel_id)
        self.assertIn("Hilton", info)

    def test_reserve_and_cancel_room(self) -> None:
        hotel = self.repo.create_hotel("X", "Y", 1)
        self.repo.reserve_room(hotel.hotel_id)
        hotel2 = self.repo.get_hotel(hotel.hotel_id)
        self.assertEqual(hotel2.available_rooms, 0)

        self.repo.cancel_room_reservation(hotel.hotel_id)
        hotel3 = self.repo.get_hotel(hotel.hotel_id)
        self.assertEqual(hotel3.available_rooms, 1)

    def test_reserve_no_availability(self) -> None:
        hotel = self.repo.create_hotel("X", "Y", 1)
        self.repo.reserve_room(hotel.hotel_id)
        with self.assertRaises(ValidationError):
            self.repo.reserve_room(hotel.hotel_id)

    def test_delete_hotel_not_found(self) -> None:
        with self.assertRaises(NotFoundError):
            self.repo.delete_hotel("no-existe")