import contextlib
import io
import tempfile
import unittest
from unittest.mock import patch

from models import Library
from storage import JsonRepository
from tests.helpers import TODAY
from ui.cli import LibraryApp


class TestCli(unittest.TestCase):
    def _run(self, inputs, library=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        library = library or Library()
        app = LibraryApp(library, JsonRepository(tmp.name), lambda: TODAY)
        out = io.StringIO()
        with patch("builtins.input", side_effect=inputs), contextlib.redirect_stdout(out):
            app.run()
        return library, out.getvalue(), tmp.name

    def test_invalid_menu_choices_are_handled(self):
        _, output, _ = self._run(["abc", "99", "0"])
        self.assertIn("whole number", output)
        self.assertIn("at most", output)
        self.assertIn("Goodbye", output)

    def test_register_learner_and_persist(self):
        lib, _, folder = self._run(["2", "1", "1", "Ana Cruz", "5", "Narra", "0", "0"])
        self.assertEqual(lib.get_member("M001").name, "Ana Cruz")
        self.assertEqual(len(JsonRepository(folder).load_all().members()), 1)

    def test_domain_error_is_reported_not_raised(self):
        # Members -> status of unknown ID, then back, exit
        _, output, _ = self._run(["2", "3", "M999", "0", "0"])
        self.assertIn("No member with ID M999", output)


if __name__ == "__main__":
    unittest.main()
