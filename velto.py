import sys
import re

VERSION = "0.4.0"


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


def execute_line(line, variables, functions):
    line = line.strip()

    if not line or line.startswith("#"):
        return

    if line.startswith("say "):
        value = get_value(
            line[4:],
            variables
        )
        print(value)

    elif line.endswith("()"):
        name = line[:-2].strip()

        if name not in functions:
            raise VeltoError(
                f"Unknown function: {name}"
            )

        for function_line in functions[name]:
            execute_line(
                function_line,
                variables,
                functions
            )

    elif "=" in line:
        name, expression = line.split("=", 1)

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


def run(code):
    variables = {}
    functions = {}

    lines = code.splitlines()
    i = 0

    while i < len(lines):

        line = lines[i].strip()

        if (
            line.startswith("function ")
            and line.endswith(":")
        ):

            name = line[9:-1].strip()

            if not re.match(
                r'^[a-zA-Z_][a-zA-Z0-9_]*$',
                name
            ):
                raise VeltoError(
                    f"Invalid function name: {name}"
                )

            i += 1

            block = []

            while (
                i < len(lines)
                and lines[i].startswith("    ")
            ):
                block.append(
                    lines[i].strip()
                )
                i += 1

            functions[name] = block
            continue

        i += 1

    i = 0

    while i < len(lines):

        original_line = lines[i]
        line = original_line.strip()

        if not line or line.startswith("#"):
            i += 1
            continue

        if (
            line.startswith("function ")
            and line.endswith(":")
        ):

            i += 1

            while (
                i < len(lines)
                and lines[i].startswith("    ")
            ):
                i += 1

            continue

        try:

            if (
                line.startswith("if ")
                and line.endswith(":")
            ):

                condition = line[3:-1].strip()

                result = bool(
                    calculate(
                        condition,
                        variables
                    )
                )

                i += 1

                if (
                    i < len(lines)
                    and lines[i].startswith("    ")
                ):

                    block_line = lines[i].strip()

                    if result:
                        execute_line(
                            block_line,
                            variables,
                            functions
                        )

                    i += 1

                if (
                    i < len(lines)
                    and lines[i].strip() == "else:"
                ):

                    i += 1

                    if (
                        i < len(lines)
                        and lines[i].startswith("    ")
                    ):

                        block_line = lines[i].strip()

                        if not result:
                            execute_line(
                                block_line,
                                variables,
                                functions
                            )

                        i += 1

                continue

            elif (
                line.startswith("while ")
                and line.endswith(":")
            ):

                condition = line[6:-1].strip()

                i += 1

                block = []

                while (
                    i < len(lines)
                    and lines[i].startswith("    ")
                ):

                    block.append(
                        lines[i].strip()
                    )

                    i += 1

                while bool(
                    calculate(
                        condition,
                        variables
                    )
                ):

                    for block_line in block:

                        execute_line(
                            block_line,
                            variables,
                            functions
                        )

                continue

            else:

                execute_line(
                    line,
                    variables,
                    functions
                )

        except VeltoError as error:

            print()
            print(
                f"Velto Error on line "
                f"{i + 1}:"
            )

            print(
                f"  {original_line}"
            )

            print(
                f"  {error}"
            )

        i += 1


def main():

    if len(sys.argv) != 2:

        print(
            f"Velto {VERSION}"
        )

        print(
            "Usage: python velto.py <file.vlt>"
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
