import sys
import re

VERSION = "0.1.0"


class VeltoError(Exception):
    pass


def calculate(expression, variables):
    expression = expression.strip()

    expression = re.sub(r'\btrue\b', 'True', expression)
    expression = re.sub(r'\bfalse\b', 'False', expression)

    try:
        return eval(
            expression,
            {"__builtins__": {}},
            variables
        )
    except NameError:
        raise VeltoError(
            f"Unknown variable in: {expression}"
        )
    except Exception:
        raise VeltoError(
            f"Invalid expression: {expression}"
        )


def get_value(text, variables):
    text = text.strip()

    if (
        len(text) >= 2
        and text[0] == '"'
        and text[-1] == '"'
    ):
        return text[1:-1]

    return calculate(text, variables)


def run(code):
    variables = {}

    for line_number, original_line in enumerate(
        code.splitlines(), 1
    ):
        line = original_line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        try:

            if line.startswith("say "):
                value = get_value(
                    line[4:],
                    variables
                )
                print(value)

            elif "=" in line:
                name, expression = line.split(
                    "=",
                    1
                )

                name = name.strip()
                expression = expression.strip()

                if not re.match(
                    r'^[a-zA-Z_][a-zA-Z0-9_]*$',
                    name
                ):
                    raise VeltoError(
                        f"Invalid variable name: {name}"
                    )

                variables[name] = get_value(
                    expression,
                    variables
                )

            else:
                raise VeltoError(
                    f"Unknown command: {line}"
                )

        except VeltoError as error:
            print()
            print(
                f"Velto Error on line "
                f"{line_number}:"
            )
            print(
                f"  {original_line}"
            )
            print(
                f"  {error}"
            )


def main():

    if len(sys.argv) != 2:
        print(f"Velto {VERSION}")
        print(
            "Usage: python velto.py "
            "<file.vlt>"
        )
        return

    filename = sys.argv[1]

    try:
        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:
            code = file.read()

        run(code)

    except FileNotFoundError:
        print(
            f"Velto Error: "
            f"File not found: {filename}"
        )


if __name__ == "__main__":
    main()
