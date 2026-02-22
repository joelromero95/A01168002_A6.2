import json
import tempfile
import unittest
from pathlib import Path

from source.customer import CustomerRepository
from source.exceptions import NotFoundError, ValidationError
from source.hotel import HotelRepository
from source.reservation import ReservationRepository


class TestReservationRepository(unittest.TestCase):
    """Pruebas unitarias de ReservationRepository."""

    def setUp(self) -> None:
        """Crea un entorno aislado por cada test."""
        self.tmpdir = tempfile.TemporaryDirectory()
        base = Path(self.tmpdir.name)

        # Cada repo usa su propio archivo dentro del temp dir
        self.hotels_path = base / "hotels.json"
        self.customers_path = base / "customers.json"
        self.reservations_path = base / "reservations.json"

        self.hotel_repo = HotelRepository(self.hotels_path)
        self.customer_repo = CustomerRepository(self.customers_path)
        self.res_repo = ReservationRepository(
            self.reservations_path,
            hotel_repo=self.hotel_repo,
            customer_repo=self.customer_repo,
        )

    def tearDown(self) -> None:
        """Limpia el entorno temporal."""
        self.tmpdir.cleanup()

    def _write_json(self, path: Path, items) -> None:
        """Helper: escribe lista de dicts como JSON en un path dado."""
        path.write_text(
            json.dumps(items, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # -------------------------
    # create_reservation
    # -------------------------

    def test_create_reservation_persists_and_reserves_room(self) -> None:
        """Crear reservación debe persistir y aumentar reserved_rooms del hotel."""
        hotel = self.hotel_repo.create_hotel("Hotel A", "CDMX", 2)
        customer = self.customer_repo.create_customer("Ana", "ana@test.com")

        reservation = self.res_repo.create_reservation(
            customer.customer_id,
            hotel.hotel_id,
        )

        # Verificar que existe en archivo
        saved = json.loads(self.reservations_path.read_text(encoding="utf-8"))
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]["reservation_id"], reservation.reservation_id)
        self.assertEqual(saved[0]["customer_id"], customer.customer_id)
        self.assertEqual(saved[0]["hotel_id"], hotel.hotel_id)

        # Verificar efecto colateral en hotel (reserved_rooms incrementó)
        updated_hotel = self.hotel_repo.get_hotel(hotel.hotel_id)
        self.assertEqual(updated_hotel.reserved_rooms, 1)
        self.assertEqual(updated_hotel.available_rooms, 1)

    def test_create_reservation_customer_not_found_raises(self) -> None:
        """Si customer no existe, debe lanzar NotFoundError."""
        hotel = self.hotel_repo.create_hotel("Hotel A", "CDMX", 1)
        with self.assertRaises(NotFoundError):
            self.res_repo.create_reservation("no-existe", hotel.hotel_id)

    def test_create_reservation_hotel_not_found_raises(self) -> None:
        """Si hotel no existe, debe lanzar NotFoundError."""
        customer = self.customer_repo.create_customer("Ana", "ana@test.com")
        with self.assertRaises(NotFoundError):
            self.res_repo.create_reservation(customer.customer_id, "no-existe")

    def test_create_reservation_no_rooms_raises(self) -> None:
        """Si el hotel no tiene disponibilidad, debe lanzar ValidationError."""
        hotel = self.hotel_repo.create_hotel("Hotel A", "CDMX", 1)
        customer = self.customer_repo.create_customer("Ana", "ana@test.com")

        _ = self.res_repo.create_reservation(customer.customer_id, hotel.hotel_id)
        with self.assertRaises(ValidationError):
            self.res_repo.create_reservation(customer.customer_id, hotel.hotel_id)

    # -------------------------
    # display_reservation
    # -------------------------

    def test_display_reservation_ok(self) -> None:
        """display_reservation debe mostrar customer_id y hotel_id."""
        hotel = self.hotel_repo.create_hotel("Hotel A", "CDMX", 1)
        customer = self.customer_repo.create_customer("Ana", "ana@test.com")

        reservation = self.res_repo.create_reservation(
            customer.customer_id,
            hotel.hotel_id,
        )
        text = self.res_repo.display_reservation(reservation.reservation_id)

        self.assertIn("Reservation[", text)
        self.assertIn(customer.customer_id, text)
        self.assertIn(hotel.hotel_id, text)

    def test_display_reservation_not_found_raises(self) -> None:
        """Si la reservación no existe, debe lanzar NotFoundError."""
        with self.assertRaises(NotFoundError):
            self.res_repo.display_reservation("no-existe")

    # -------------------------
    # cancel_reservation
    # -------------------------

    def test_cancel_reservation_removes_and_frees_room(self) -> None:
        """Cancelar debe eliminar el registro y disminuir reserved_rooms del hotel."""
        hotel = self.hotel_repo.create_hotel("Hotel A", "CDMX", 2)
        customer = self.customer_repo.create_customer("Ana", "ana@test.com")

        reservation = self.res_repo.create_reservation(
            customer.customer_id,
            hotel.hotel_id,
        )

        # Antes: reserved_rooms = 1
        self.assertEqual(self.hotel_repo.get_hotel(hotel.hotel_id).reserved_rooms, 1)

        self.res_repo.cancel_reservation(reservation.reservation_id)

        # Debe desaparecer del archivo
        saved = json.loads(self.reservations_path.read_text(encoding="utf-8"))
        self.assertEqual(saved, [])

        # Debe liberar habitación
        updated_hotel = self.hotel_repo.get_hotel(hotel.hotel_id)
        self.assertEqual(updated_hotel.reserved_rooms, 0)
        self.assertEqual(updated_hotel.available_rooms, 2)

        # display ya no debe encontrarla
        with self.assertRaises(NotFoundError):
            self.res_repo.display_reservation(reservation.reservation_id)

    def test_cancel_reservation_not_found_raises(self) -> None:
        """Cancelar una reservación inexistente debe lanzar NotFoundError."""
        with self.assertRaises(NotFoundError):
            self.res_repo.cancel_reservation("no-existe")

    # -------------------------
    # Carga desde JSON con inválidos
    # -------------------------

    def test_load_all_ignores_invalid_records_from_json(self) -> None:
        """Debe ignorar registros inválidos del archivo y cargar solo los válidos."""
        # Preparamos customers/hotels solo para que los ids "tengan sentido"
        # (Nota: ReservationRepository no valida existencia al mostrar, solo al crear.
        # Pero mantener consistencia ayuda a tu evidencia.)
        self._write_json(
            self.customers_path,
            [
                {"customer_id": "c-001", "name": "Ana", "email": "ana@test.com"},
                {"customer_id": "c-002", "name": "Luis", "email": "luis@test.com"},
            ],
        )
        self._write_json(
            self.hotels_path,
            [
                {
                    "hotel_id": "h-001",
                    "name": "Hotel Centro",
                    "city": "CDMX",
                    "total_rooms": 10,
                    "reserved_rooms": 0,
                },
                {
                    "hotel_id": "h-002",
                    "name": "Hotel Playa",
                    "city": "Cancún",
                    "total_rooms": 5,
                    "reserved_rooms": 0,
                },
            ],
        )

        # 2 válidas + 5 inválidas
        self._write_json(
            self.reservations_path,
            [
                {
                    "reservation_id": "r-001",
                    "customer_id": "c-001",
                    "hotel_id": "h-001",
                },

                {
                    "reservation_id": "r-002",
                    "customer_id": "c-002",
                    "hotel_id": "h-002",
                },

                {
                    "reservation_id": "bad-001",
                    "customer_id": "c-001",
                },

                {
                    "reservation_id": "bad-002",
                    "hotel_id": "h-001",
                },

                {
                    "reservation_id": "   ",
                    "customer_id": "c-001",
                    "hotel_id": "h-001",
                },

                {
                    "reservation_id": "bad-004",
                    "customer_id": "   ",
                    "hotel_id": "h-001",
                },

                {
                    "reservation_id": "bad-005",
                    "customer_id": "c-001",
                    "hotel_id": "   ",
                },
            ],
        )

        # Válidas deben mostrarse
        text1 = self.res_repo.display_reservation("r-001")
        text2 = self.res_repo.display_reservation("r-002")
        self.assertIn("customer=c-001", text1)
        self.assertIn("hotel=h-002", text2)

        # Inválidas no deben existir porque se ignoran al cargar
        with self.assertRaises(NotFoundError):
            self.res_repo.display_reservation("bad-001")

    def test_load_all_with_non_list_json_is_safe(self) -> None:
        """Si el JSON no es lista, debe manejarlo sin crash (regresa vacío)."""
        self.reservations_path.write_text('{"a": 1}', encoding="utf-8")
        with self.assertRaises(NotFoundError):
            self.res_repo.display_reservation("r-001")
