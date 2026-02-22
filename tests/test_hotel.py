import json
import tempfile
import unittest
from pathlib import Path

from source.exceptions import NotFoundError, ValidationError
from source.hotel import HotelRepository


class TestHotelRepository(unittest.TestCase):
    """Pruebas unitarias de HotelRepository."""

    def setUp(self) -> None:
        """Crea un entorno aislado por cada test."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.hotels_path = Path(self.tmpdir.name) / "hotels.json"
        self.repo = HotelRepository(self.hotels_path)

    def tearDown(self) -> None:
        """Limpia el entorno temporal."""
        self.tmpdir.cleanup()

    def _write_json(self, items) -> None:
        """Helper: escribe lista de dicts como JSON en el archivo temporal."""
        self.hotels_path.write_text(
            json.dumps(items, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # -------------------------
    # CRUD básico
    # -------------------------

    def test_create_hotel_persists_record(self) -> None:
        """Debe crear un hotel válido y persistirlo en JSON."""
        created = self.repo.create_hotel("Hilton", "CDMX", 10)

        data = json.loads(self.hotels_path.read_text(encoding="utf-8"))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["hotel_id"], created.hotel_id)
        self.assertEqual(data[0]["name"], "Hilton")
        self.assertEqual(data[0]["city"], "CDMX")
        self.assertEqual(data[0]["total_rooms"], 10)
        self.assertEqual(data[0]["reserved_rooms"], 0)

    def test_create_hotel_invalid_name_raises(self) -> None:
        """Nombre vacío debe disparar ValidationError."""
        with self.assertRaises(ValidationError):
            self.repo.create_hotel("   ", "CDMX", 10)

    def test_create_hotel_invalid_city_raises(self) -> None:
        """Ciudad vacía debe disparar ValidationError."""
        with self.assertRaises(ValidationError):
            self.repo.create_hotel("Hotel", "   ", 10)

    def test_create_hotel_invalid_total_rooms_raises(self) -> None:
        """total_rooms <= 0 debe disparar ValidationError."""
        with self.assertRaises(ValidationError):
            self.repo.create_hotel("Hotel", "CDMX", 0)

    def test_get_hotel_not_found_raises(self) -> None:
        """Si no existe el id, debe disparar NotFoundError."""
        with self.assertRaises(NotFoundError):
            self.repo.get_hotel("no-existe")

    def test_display_hotel_contains_key_info(self) -> None:
        """display_hotel debe incluir nombre, ciudad y disponibilidad."""
        created = self.repo.create_hotel("Hotel Centro", "CDMX", 3)
        text = self.repo.display_hotel(created.hotel_id)
        self.assertIn("Hotel[", text)
        self.assertIn("Hotel Centro", text)
        self.assertIn("CDMX", text)
        self.assertIn("available", text)

    def test_modify_hotel_updates_record(self) -> None:
        """Debe modificar name/city/total_rooms respetando consistencia."""
        created = self.repo.create_hotel("A", "C1", 5)
        updated = self.repo.modify_hotel(created.hotel_id, "B", "C2", 7)

        self.assertEqual(updated.name, "B")
        self.assertEqual(updated.city, "C2")
        self.assertEqual(updated.total_rooms, 7)
        self.assertEqual(updated.reserved_rooms, 0)

        # Verificar persistencia
        fetched = self.repo.get_hotel(created.hotel_id)
        self.assertEqual(fetched.total_rooms, 7)

    def test_modify_hotel_not_found_raises(self) -> None:
        """Modificar un id inexistente debe disparar NotFoundError."""
        with self.assertRaises(NotFoundError):
            self.repo.modify_hotel("no-existe", "X", "Y", 5)

    def test_modify_hotel_invalid_total_rooms_raises(self) -> None:
        """Modificar con total_rooms <= 0 debe disparar ValidationError."""
        created = self.repo.create_hotel("A", "C1", 5)
        with self.assertRaises(ValidationError):
            self.repo.modify_hotel(created.hotel_id, "A", "C1", 0)

    def test_modify_hotel_cannot_reduce_below_reserved(self) -> None:
        """No se debe permitir total_rooms < reserved_rooms."""
        created = self.repo.create_hotel("A", "C1", 2)
        # Reservar 2 cuartos (hotel queda sin disponibilidad)
        self.repo.reserve_room(created.hotel_id)
        self.repo.reserve_room(created.hotel_id)

        with self.assertRaises(ValidationError):
            self.repo.modify_hotel(created.hotel_id, "A", "C1", 1)

    def test_delete_hotel_removes_record(self) -> None:
        """delete_hotel debe eliminar el registro."""
        created = self.repo.create_hotel("A", "CDMX", 3)
        self.repo.delete_hotel(created.hotel_id)

        with self.assertRaises(NotFoundError):
            self.repo.get_hotel(created.hotel_id)

    def test_delete_hotel_not_found_raises(self) -> None:
        """Eliminar un id inexistente debe disparar NotFoundError."""
        with self.assertRaises(NotFoundError):
            self.repo.delete_hotel("no-existe")

    # -------------------------
    # Reservar / cancelar habitación
    # -------------------------

    def test_reserve_room_increments_reserved(self) -> None:
        """reserve_room debe incrementar reserved_rooms."""
        created = self.repo.create_hotel("A", "CDMX", 2)
        self.repo.reserve_room(created.hotel_id)

        fetched = self.repo.get_hotel(created.hotel_id)
        self.assertEqual(fetched.reserved_rooms, 1)
        self.assertEqual(fetched.available_rooms, 1)

    def test_reserve_room_no_availability_raises(self) -> None:
        """Si no hay disponibilidad, reserve_room debe fallar."""
        created = self.repo.create_hotel("A", "CDMX", 1)
        self.repo.reserve_room(created.hotel_id)

        with self.assertRaises(ValidationError):
            self.repo.reserve_room(created.hotel_id)

    def test_reserve_room_not_found_raises(self) -> None:
        """Reservar en hotel inexistente debe disparar NotFoundError."""
        with self.assertRaises(NotFoundError):
            self.repo.reserve_room("no-existe")

    def test_cancel_room_reservation_decrements_reserved(self) -> None:
        """cancel_room_reservation debe decrementar reserved_rooms."""
        created = self.repo.create_hotel("A", "CDMX", 2)
        self.repo.reserve_room(created.hotel_id)
        self.repo.cancel_room_reservation(created.hotel_id)

        fetched = self.repo.get_hotel(created.hotel_id)
        self.assertEqual(fetched.reserved_rooms, 0)
        self.assertEqual(fetched.available_rooms, 2)

    def test_cancel_room_reservation_when_none_raises(self) -> None:
        """Si no hay reservaciones, cancelar debe fallar."""
        created = self.repo.create_hotel("A", "CDMX", 2)
        with self.assertRaises(ValidationError):
            self.repo.cancel_room_reservation(created.hotel_id)

    def test_cancel_room_reservation_not_found_raises(self) -> None:
        """Cancelar reservación en hotel inexistente debe disparar NotFoundError."""
        with self.assertRaises(NotFoundError):
            self.repo.cancel_room_reservation("no-existe")

    # -------------------------
    # Carga desde JSON con inválidos
    # -------------------------

    def test_load_all_ignores_invalid_records_from_json(self) -> None:
        """Debe ignorar registros inválidos del archivo y cargar solo los válidos."""
        self._write_json(
            [
                {
                    "hotel_id": "h-001",
                    "name": "Hotel Centro",
                    "city": "CDMX",
                    "total_rooms": 10,
                    "reserved_rooms": 2,
                },
                {
                    "hotel_id": "h-002",
                    "name": "Hotel Playa",
                    "city": "Cancún",
                    "total_rooms": 5,
                    "reserved_rooms": 5,
                },
                {"hotel_id": "bad-001", "name": "Faltan campos"},
                {
                    "hotel_id": "bad-002",
                    "name": "No rooms",
                    "city": "X",
                    "total_rooms": "abc",
                    "reserved_rooms": 0,
                },
                {
                    "hotel_id": "bad-003",
                    "name": "Total <= 0",
                    "city": "X",
                    "total_rooms": 0,
                    "reserved_rooms": 0,
                },
                {
                    "hotel_id": "bad-004",
                    "name": "Reserved negativo",
                    "city": "X",
                    "total_rooms": 5,
                    "reserved_rooms": -1,
                },
                {
                    "hotel_id": "bad-005",
                    "name": "Reserved > total",
                    "city": "X",
                    "total_rooms": 5,
                    "reserved_rooms": 6,
                },
                {
                    "hotel_id": "   ",
                    "name": "Id vacio",
                    "city": "X",
                    "total_rooms": 5,
                    "reserved_rooms": 0,
                },
            ]
        )

        # Los válidos deben existir
        h1 = self.repo.get_hotel("h-001")
        h2 = self.repo.get_hotel("h-002")
        self.assertEqual(h1.city, "CDMX")
        self.assertEqual(h2.available_rooms, 0)

        # Los inválidos deben haber sido ignorados (no encontrados)
        with self.assertRaises(NotFoundError):
            self.repo.get_hotel("bad-001")

    def test_load_all_with_non_list_json_is_safe(self) -> None:
        """Si el JSON no es lista, debe manejarlo sin crash (regresa vacío)."""
        self.hotels_path.write_text('{"a": 1}', encoding="utf-8")
        with self.assertRaises(NotFoundError):
            self.repo.get_hotel("h-001")