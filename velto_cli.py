import sys
from pathlib import Path

from velto_lexer import tokenize
from velto_parser import parse
from velto_ast import run_ast


def print_usage():
    print("Velto Programming Language")
    print()
    print("Usage:")
    print("  velto <file.vlt>")
    print()
    print("Example:")
    print("  velto examples/hello.vlt")


def run_file(filename):
    path = Path(filename)

    if not path.exists():
        print(f"Velto Error: File not found: {filename}")
        return 1

    if not path.is_file():
        print(f"Velto Error: Not a file: {filename}")
        return 1

    if path.suffix != ".vlt":
        print("Velto Error: Source file must use .vlt extension")
        return 1

    try:
        source = path.read_text(encoding="utf-8")
        tokens = tokenize(source)
        tree = parse(tokens)
        run_ast(tree)
        return 0

    except Exception as error:
        print(f"Velto Error: {error}")
        return 1


def main():
    if len(sys.argv) == 1:
        print_usage()
        return 0

    if sys.argv[1] in {
        "--help",
        "-h"
    }:
        print_usage()
        return 0

    if len(sys.argv) > 2:
        print("Velto Error: Only one source file is allowed")
        print_usage()
        return 1

    return run_file(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
