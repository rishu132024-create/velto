import sys


def format_code(source):
    lines = source.splitlines()
    result = []

    indent = 0

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            if result and result[-1] != "":
                result.append("")
            continue

        if line.startswith("}"):
            indent = max(0, indent - 1)

        if line.endswith(":"):
            result.append(
                "    " * indent + line
            )
            indent += 1
            continue

        result.append(
            "    " * indent + line
        )

    while result and result[-1] == "":
        result.pop()

    return "\n".join(result) + "\n"


def format_file(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        source = file.read()

    formatted = format_code(source)

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(formatted)

    return True


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python velto_formatter.py <file.vlt>"
        )
        return 1

    path = sys.argv[1]

    try:
        format_file(path)
    except Exception as error:
        print(
            "Velto Formatter Error:",
            error
        )
        return 1

    print(
        "Formatted:",
        path
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
