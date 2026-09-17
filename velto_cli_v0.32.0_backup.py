import sys
from pathlib import Path

from velto_lexer import tokenize
from velto_parser import parse, ParserError
from velto_ast import run_ast, ASTInterpreterError
from velto_errors import VeltoError


def print_usage():
    print("Velto Programming Language")
    print()
    print("Usage:")
    print("  velto <file.vlt>")
    print()
    print("Example:")
    print("  velto examples/hello.vlt")


def get_source_line(source, line):
    if line is None:
        return None

    lines = source.splitlines()

    if line < 1 or line > len(lines):
        return None

    return lines[line - 1]


def run_file(filename):
    path = Path(filename)

    if not path.exists():
        error = VeltoError(
            f"File not found: {filename}",
            filename
        )

        print(error.format())
        return 1

    if not path.is_file():
        error = VeltoError(
            f"Not a file: {filename}",
            filename
        )

        print(error.format())
        return 1

    if path.suffix != ".vlt":
        error = VeltoError(
            "Source file must use .vlt extension",
            filename
        )

        print(error.format())
        return 1

    try:
        source = path.read_text(
            encoding="utf-8"
        )

        tokens = tokenize(source)
        tree = parse(tokens)

        run_ast(tree)

        return 0

    except ParserError as error:
        source_line = get_source_line(
            source,
            error.line
        )

        formatted = VeltoError(
            error.message,
            filename,
            error.line,
            source_line
        )

        print(formatted.format())
        return 1

    except ASTInterpreterError as error:
        source_line = get_source_line(
            source,
            error.line
        )

        formatted = VeltoError(
            error.message,
            filename,
            error.line,
            source_line
        )

        print(formatted.format())
        return 1

    except VeltoError as error:
        print(error.format())
        return 1

    except Exception as error:
        print(
            f"Velto Error\n"
            f"File: {filename}\n\n"
            f"Error: {error}"
        )

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
        error = VeltoError(
            "Only one source file is allowed",
            sys.argv[1]
        )

        print(error.format())
        return 1

    return run_file(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
