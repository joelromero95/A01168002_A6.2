"""Unit tests for storage helpers.

Covers load_json_list and save_json_list behavior for missing/empty/invalid JSON,
filtering of non-dict items, safe writes, and graceful handling of I/O errors.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from source.storage import load_json_list, save_json_list


class TestStorage(unittest.TestCase):
    """Pruebas unitarias para storage.py."""

    def test_load_json_list_file_not_exists_returns_empty(self) -> None:
        """Si el archivo no existe, debe regresar [] y avisar en consola."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "no-existe.json"
            with patch("builtins.print") as mocked_print:
                data = load_json_list(path)

            self.assertEqual(data, [])
            mocked_print.assert_called()
            # No dependemos del texto exacto, solo que avisó.

    def test_load_json_list_empty_file_returns_empty(self) -> None:
        """Si el archivo está vacío, debe regresar [] y avisar en consola."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "vacio.json"
            path.write_text("", encoding="utf-8")

            with patch("builtins.print") as mocked_print:
                data = load_json_list(path)

            self.assertEqual(data, [])
            mocked_print.assert_called()

    def test_load_json_list_whitespace_file_returns_empty(self) -> None:
        """Si el archivo contiene solo espacios, debe regresar [] y avisar."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spaces.json"
            path.write_text("   \n  ", encoding="utf-8")

            with patch("builtins.print") as mocked_print:
                data = load_json_list(path)

            self.assertEqual(data, [])
            mocked_print.assert_called()

    def test_load_json_list_invalid_json_returns_empty(self) -> None:
        """Si el JSON está corrupto, debe regresar [] y avisar en consola."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "corrupto.json"
            path.write_text("{esto no es json", encoding="utf-8")

            with patch("builtins.print") as mocked_print:
                data = load_json_list(path)

            self.assertEqual(data, [])
            mocked_print.assert_called()

    def test_load_json_list_json_not_list_returns_empty(self) -> None:
        """Si el JSON válido no es una lista, debe regresar [] y avisar."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dict.json"
            path.write_text('{"a": 1}', encoding="utf-8")

            with patch("builtins.print") as mocked_print:
                data = load_json_list(path)

            self.assertEqual(data, [])
            mocked_print.assert_called()

    def test_load_json_list_filters_non_dict_items(self) -> None:
        """Debe filtrar elementos que no sean dict e ignorarlos con aviso."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mix.json"
            items = [{"a": 1}, 2, "x", ["list"], {"b": 2}]
            path.write_text(json.dumps(items), encoding="utf-8")

            with patch("builtins.print") as mocked_print:
                data = load_json_list(path)

            self.assertEqual(data, [{"a": 1}, {"b": 2}])
            # Debió haber avisos por los elementos no dict
            self.assertTrue(mocked_print.called)

    def test_save_json_list_creates_dir_and_writes_file(self) -> None:
        """Debe crear el directorio padre y guardar el archivo JSON."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "subdir" / "data.json"
            content = [{"x": 1}, {"y": "áéíóú"}]

            save_json_list(path, content)

            self.assertTrue(path.exists())
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded, content)

    def test_save_json_list_handles_write_error(self) -> None:
        """Si ocurre un error de escritura, debe avisar y no crashear."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.json"

            # Forzamos error de escritura mockeando write_text
            with patch.object(Path, "write_text", side_effect=OSError("boom")):
                with patch("builtins.print") as mocked_print:
                    save_json_list(path, [{"a": 1}])

            mocked_print.assert_called()
