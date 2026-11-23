import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "velto_cli.py"


class VeltoFunctionScopeTests(unittest.TestCase):

    def run_velto(self, code):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "function_test.vlt"
            source.write_text(code, encoding="utf-8")

            return subprocess.run(
                [sys.executable, str(CLI), str(source)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10
            )

    def test_return_value(self):
        result = self.run_velto(
            'function add(a, b):\n'
            '    return a + b\n'
            'result = add(10, 20)\n'
            'say result'
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr
        )
        self.assertIn("30", result.stdout)

    def test_recursive_function(self):
        result = self.run_velto(
            'function factorial(n):\n'
            '    if n <= 1:\n'
            '        return 1\n'
            '    else:\n'
            '        return n * factorial(n - 1)\n'
            'say factorial(5)'
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr
        )
        self.assertIn("120", result.stdout)

    def test_function_without_return(self):
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
