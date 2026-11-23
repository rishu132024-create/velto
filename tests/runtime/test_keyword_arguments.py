import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "velto_cli.py"


class VeltoKeywordArgumentTests(unittest.TestCase):

    def run_velto(self, code):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "keyword_test.vlt"
            source.write_text(code, encoding="utf-8")

            return subprocess.run(
                [sys.executable, str(CLI), str(source)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10
            )

    def test_keyword_arguments(self):
        result = self.run_velto(
            'function introduce(name, age):\n'
            '    say name\n'
            '    say age\n'
            'introduce(name = "Velto", age = 1)'
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Velto", result.stdout)
        self.assertIn("1", result.stdout)

    def test_keyword_arguments_reordered(self):
        result = self.run_velto(
            'function add(a, b):\n'
            '    return a + b\n'
            'say add(b = 5, a = 15)'
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("20", result.stdout)

    def test_positional_and_keyword_arguments(self):
        result = self.run_velto(
            'function add(a, b, c):\n'
            '    return a + b + c\n'
            'say add(10, c = 30, b = 20)'
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("60", result.stdout)

    def test_keyword_with_default(self):
        result = self.run_velto(
            'function greet(name, message = "Hello"):\n'
            '    say message + " " + name\n'
            'greet(name = "Velto")'
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Hello Velto", result.stdout)

    def test_unexpected_keyword(self):
        result = self.run_velto(
            'function greet(name):\n'
            '    say name\n'
            'greet(age = 10)'
        )
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected keyword argument: age", output)

    def test_duplicate_argument(self):
        result = self.run_velto(
            'function add(a, b):\n'
            '    return a + b\n'
            'say add(10, a = 20)'
        )
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("multiple values for argument: a", output)

    def test_duplicate_keyword(self):
        result = self.run_velto(
            'function add(a, b):\n'
            '    return a + b\n'
            'say add(a = 10, a = 20)'
        )
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Duplicate keyword argument: a", output)


if __name__ == "__main__":
    unittest.main()
