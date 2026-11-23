import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "velto_cli.py"


class VeltoArgumentTests(unittest.TestCase):

    def run_velto(self, code):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "arguments_test.vlt"
            source.write_text(code, encoding="utf-8")

            return subprocess.run(
                [sys.executable, str(CLI), str(source)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10
            )

    def test_correct_arguments(self):
        result = self.run_velto(
            'function add(a, b):\n'
            '    say a + b\n'
            'add(10, 20)'
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr
        )
        self.assertIn("30", result.stdout)

    def test_too_few_arguments(self):
        result = self.run_velto(
            'function add(a, b):\n'
            '    say a + b\n'
            'add(10)'
        )
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expects 2 arguments, got 1", output)

    def test_too_many_arguments(self):
        result = self.run_velto(
            'function add(a, b):\n'
            '    say a + b\n'
            'add(10, 20, 30)'
        )
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expects 2 arguments, got 3", output)

    def test_zero_arguments(self):
        result = self.run_velto(
            'function hello():\n'
            '    say "Hello Velto"\n'
            'hello()'
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr
        )
        self.assertIn("Hello Velto", result.stdout)


if __name__ == "__main__":
    unittest.main()
