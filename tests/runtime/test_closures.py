import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "velto_cli.py"


class VeltoClosureTests(unittest.TestCase):

    def run_velto(self, code):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "closure_test.vlt"
            source.write_text(code, encoding="utf-8")

            return subprocess.run(
                [sys.executable, str(CLI), str(source)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10
            )

    def test_nested_function(self):
        result = self.run_velto(
            'function outer(x):\n'
            '    function inner(y):\n'
            '        return x + y\n'
            '    return inner(5)\n'
            'say outer(10)'
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr
        )
        self.assertIn("15", result.stdout)

    def test_nested_function_uses_outer_variable(self):
        result = self.run_velto(
            'function calculate():\n'
            '    number = 100\n'
            '    function add(value):\n'
            '        return number + value\n'
            '    return add(25)\n'
            'say calculate()'
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr
        )
        self.assertIn("125", result.stdout)

    def test_nested_function_with_multiple_levels(self):
        result = self.run_velto(
            'function first(a):\n'
            '    function second(b):\n'
            '        function third(c):\n'
            '            return a + b + c\n'
            '        return third(3)\n'
            '    return second(2)\n'
            'say first(1)'
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=result.stdout + result.stderr
        )
        self.assertIn("6", result.stdout)


if __name__ == "__main__":
    unittest.main()
