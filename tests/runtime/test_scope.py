import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "velto_cli.py"


class VeltoScopeTests(unittest.TestCase):

    def run_velto(self, code):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "scope_test.vlt"
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

    def test_global_variable_read(self):
        output = self.run_velto(
            'name = "Velto"\n'
            'function show():\n'
            '    say name\n'
            'show()'
        )
        self.assertIn("Velto", output)

    def test_local_variable(self):
        output = self.run_velto(
            'function show():\n'
            '    message = "Local"\n'
            '    say message\n'
            'show()'
        )
        self.assertIn("Local", output)

    def test_local_variable_isolation(self):
        output = self.run_velto(
            'value = 10\n'
            'function change():\n'
            '    value = 20\n'
            'change()\n'
            'say value'
        )
        self.assertIn("10", output)
        self.assertNotIn("20", output)

    def test_function_return(self):
        output = self.run_velto(
            'function add(a, b):\n'
            '    return a + b\n'
            'result = add(10, 20)\n'
            'say result'
        )
        self.assertIn("30", output)

    def test_recursive_function(self):
        output = self.run_velto(
            'function count(n):\n'
            '    if n <= 0:\n'
            '        return 0\n'
            '    return count(n - 1) + 1\n'
            'say count(5)'
        )
        self.assertIn("5", output)


if __name__ == "__main__":
    unittest.main()
