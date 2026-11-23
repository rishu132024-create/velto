import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "velto_cli.py"


class VeltoDefaultArgumentTests(unittest.TestCase):

    def run_velto(self, code):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "default_test.vlt"
            source.write_text(code, encoding="utf-8")

            return subprocess.run(
                [sys.executable, str(CLI), str(source)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10
            )

    def test_single_default(self):
        result = self.run_velto(
            'function greet(name = "World"):\n'
            '    say "Hello " + name\n'
            'greet()'
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Hello World", result.stdout)

    def test_override_default(self):
        result = self.run_velto(
            'function greet(name = "World"):\n'
            '    say "Hello " + name\n'
            'greet("Velto")'
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Hello Velto", result.stdout)

    def test_multiple_defaults(self):
        result = self.run_velto(
            'function add(a, b = 10):\n'
            '    return a + b\n'
            'say add(5)\n'
            'say add(5, 20)'
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("15", result.stdout)
        self.assertIn("25", result.stdout)

    def test_all_default_arguments(self):
        result = self.run_velto(
            'function total(a = 10, b = 20):\n'
            '    return a + b\n'
            'say total()'
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("30", result.stdout)

    def test_required_argument_missing(self):
        result = self.run_velto(
            'function add(a, b = 10):\n'
            '    return a + b\n'
            'say add()'
        )
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expects 1 to 2 arguments, got 0", output)

    def test_too_many_arguments(self):
        result = self.run_velto(
            'function add(a, b = 10):\n'
            '    return a + b\n'
            'say add(1, 2, 3)'
        )
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expects 1 to 2 arguments, got 3", output)


if __name__ == "__main__":
    unittest.main()
