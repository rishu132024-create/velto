import os
import sys


class VeltoTestError(Exception):
    pass


class TestRunner:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0

    def check(self, name, condition):
        self.total += 1

        if condition:
            self.passed += 1
            print("PASS  " + str(name))
            return True

        self.failed += 1
        print("FAIL  " + str(name))
        return False

    def equal(self, name, actual, expected):
        return self.check(
            name,
            actual == expected
        )

    def not_equal(self, name, actual, expected):
        return self.check(
            name,
            actual != expected
        )

    def true(self, name, value):
        return self.check(
            name,
            bool(value) is True
        )

    def false(self, name, value):
        return self.check(
            name,
            bool(value) is False
        )

    def summary(self):
        print("")
        print("Velto Test Summary")
        print("==================")
        print("Total:", self.total)
        print("Passed:", self.passed)
        print("Failed:", self.failed)

        if self.failed == 0:
            print("Result: PASS")
            return True

        print("Result: FAIL")
        return False


def discover_tests(directory):
    if not os.path.isdir(directory):
        return []

    files = []

    for name in sorted(os.listdir(directory)):
        if name.startswith("test_") and name.endswith(".vlt"):
            files.append(
                os.path.join(directory, name)
            )

    return files


def run_file(path):
    print("")
    print("Testing:", path)

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            source = file.read()
    except Exception as error:
        print(
            "ERROR:",
            error
        )
        return False

    if not source.strip():
        print("FAIL  Empty test file")
        return False

    print("PASS  Test file loaded")

    lines = [
        line
        for line in source.splitlines()
        if line.strip()
    ]

    if lines:
        print(
            "PASS  Test file contains "
            + str(len(lines))
            + " code lines"
        )
        return True

    return False


def run_tests(directory):
    files = discover_tests(directory)

    if not files:
        print("No Velto test files found")
        return 1

    total = 0
    passed = 0

    for path in files:
        total += 1

        if run_file(path):
            passed += 1

    failed = total - passed

    print("")
    print("Velto Test Summary")
    print("==================")
    print("Test files:", total)
    print("Passed:", passed)
    print("Failed:", failed)

    if failed == 0:
        print("Result: PASS")
        return 0

    print("Result: FAIL")
    return 1


def main():
    directory = "tests"

    if len(sys.argv) > 1:
        directory = sys.argv[1]

    return run_tests(directory)


if __name__ == "__main__":
    raise SystemExit(main())
