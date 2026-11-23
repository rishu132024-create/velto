import unittest

from velto_errors import VeltoError, format_error


class VeltoErrorTests(unittest.TestCase):

    def test_basic_error(self):
        error = VeltoError("Unknown variable")
        self.assertIn("Unknown variable", error.format())

    def test_filename(self):
        error = VeltoError(
            "Invalid syntax",
            filename="main.vlt"
        )
        self.assertIn("main.vlt", error.format())

    def test_line_number(self):
        error = VeltoError(
            "Invalid syntax",
            filename="main.vlt",
            line=5
        )
        self.assertIn("Line: 5", error.format())

    def test_source_line(self):
        error = VeltoError(
            "Unknown variable",
            filename="main.vlt",
            line=2,
            source_line="say unknown"
        )
        self.assertIn("say unknown", error.format())
        self.assertIn("^", error.format())

    def test_column(self):
        error = VeltoError(
            "Invalid syntax",
            source_line="say hello",
            column=5
        )
        self.assertIn("    ^", error.format())

    def test_hint(self):
        error = VeltoError(
            "Unknown variable",
            hint="Check the variable name"
        )
        self.assertIn("Hint:", error.format())


if __name__ == "__main__":
    unittest.main()
