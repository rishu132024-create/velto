import re
import sys


def lint_code(source):
    issues = []
    lines = source.splitlines()

    for number, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip()

        if "\t" in line:
            issues.append(
                (
                    number,
                    "Tabs are not recommended; use spaces"
                )
            )

        if line.endswith(" "):
            issues.append(
                (
                    number,
                    "Trailing whitespace"
                )
            )

        if len(line) > 100:
            issues.append(
                (
                    number,
                    "Line is longer than 100 characters"
                )
            )

        if re.search(
            r"\bTODO\b",
            line,
            re.IGNORECASE
        ):
            issues.append(
                (
                    number,
                    "TODO found"
                )
            )

        if "==" in line and line.strip().startswith("if"):
            if line.rstrip().endswith(":") is False:
                issues.append(
                    (
                        number,
                        "If statement should end with :"
                    )
                )

        if line.strip().startswith("for "):
            if line.rstrip().endswith(":") is False:
                issues.append(
                    (
                        number,
                        "For statement should end with :"
                    )
                )

        if line.strip().startswith("while "):
            if line.rstrip().endswith(":") is False:
                issues.append(
                    (
                        number,
                        "While statement should end with :"
                    )
                )

    return issues


def lint_file(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        source = file.read()

    return lint_code(source)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python velto_linter.py <file.vlt>"
        )
        return 1

    path = sys.argv[1]

    try:
        issues = lint_file(path)
    except Exception as error:
        print(
            "Velto Linter Error:",
            error
        )
        return 1

    if not issues:
        print(
            "No lint issues found"
        )
        return 0

    print(
        "Velto Lint Issues:"
    )

    for line, message in issues:
        print(
            "Line "
            + str(line)
            + ": "
            + message
        )

    print(
        "Total issues:",
        len(issues)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
