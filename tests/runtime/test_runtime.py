import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "velto_cli.py"


class VeltoRuntimeTests(unittest.TestCase):

    def run_velto(self, code):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "test.vlt"
            source.write_text(code, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(CLI), str(source)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10
            )

            self.assertEqual(
                result.returncode,
                0,
                msg=result.stdout + result.stderr
            )

            return result.stdout

    def test_string(self):
        output = self.run_velto('say "Hello Velto"')
        self.assertIn("Hello Velto", output)

    def test_arithmetic(self):
        output = self.run_velto("say 10 + 20")
        self.assertIn("30", output)

    def test_variable(self):
        output = self.run_velto(
            'name = "Velto"\nsay name'
        )
        self.assertIn("Velto", output)

    def test_boolean_condition(self):
        output = self.run_velto(
            'if 10 > 5:\n    say "Boolean works"'
        )
        self.assertIn("Boolean works", output)


if __name__ == "__main__":
    unittest.main()
