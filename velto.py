import sys
import re

VERSION = "0.6.0"


class VeltoError(Exception):
    pass


class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value


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


def get_value(text, variables, functions):
    text = text.strip()

    if (
        len(text) >= 2
        and text[0] == '"'
        and text[-1] == '"'
    ):
        return text[1:-1]

    match = re.fullmatch(
        r'([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)',
        text
    )

    if match:
        name = match.group(1)
        argument_text = match.group(2)

        arguments = parse_arguments(
            argument_text,
            variables,
            functions
        )

        return execute_function(
            name,
            arguments,
            functions,
            variables
        )

    return calculate(
        text,
        variables
    )


def parse_arguments(
    text,
    variables,
    functions
):
    if not text.strip():
        return []

    parts = []
    current = ""
    inside_string = False

    for char in text:

        if char == '"':
            inside_string = not inside_string

        if char == "," and not inside_string:
            parts.append(current.strip())
            current = ""
        else:
            current += char

    if current.strip():
        parts.append(current.strip())

    return [
        get_value(
            part,
            variables,
            functions
        )
        for part in parts
    ]


def execute_function(
    name,
    arguments,
    functions,
    variables
):
    if name not in functions:
        raise VeltoError(
            f"Unknown function: {name}"
        )

    parameters, body = functions[name]

    if len(arguments) != len(parameters):
        raise VeltoError(
            f"Function '{name}' expects "
            f"{len(parameters)} argument(s), "
            f"but got {len(arguments)}"
        )

    local_variables = variables.copy()

    for parameter, argument in zip(
        parameters,
        arguments
    ):
        local_variables[parameter] = argument

    try:

        i = 0

        while i < len(body):

            line = body[i]

            if line.startswith("if ") and line.endswith(":"):

                condition = line[3:-1].strip()

                condition_value = get_value(
                    condition,
                    local_variables,
                    functions
                )

                i += 1

                if i < len(body):
                    next_line = body[i]

                if condition_value:
                    if i < len(body):
                        execute_line(
                            body[i],
                            local_variables,
                            functions
                        )

                i += 1
                continue

            execute_line(
                line,
                local_variables,
                functions
            )

            i += 1

    except ReturnValue as result:
        return result.value

    return None


def execute_line(
    line,
    variables,
    functions
):
    line = line.strip()

    if not line or line.startswith("#"):
        return None

    if line == "return":
        raise ReturnValue(None)

    if line.startswith("return "):

        value = get_value(
            line[7:],
            variables,
            functions
        )

        raise ReturnValue(value)

    if line.startswith("say "):

        value = get_value(
            line[4:],
            variables,
            functions
        )

        print(value)

        return None

    match = re.fullmatch(
        r'([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)',
        line
    )

    if match:

        name = match.group(1)
        argument_text = match.group(2)

        arguments = parse_arguments(
            argument_text,
            variables,
            functions
        )

        return execute_function(
            name,
            arguments,
            functions,
            variables
        )

    if line.startswith("if ") and line.endswith(":"):

        condition = line[3:-1].strip()

        return ("IF", condition)

    if line.startswith("while ") and line.endswith(":"):

        condition = line[6:-1].strip()

        return ("WHILE", condition)

    if "=" in line:

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
            variables,
            functions
        )

        return None

    raise VeltoError(
        f"Unknown command: {line}"
    )


def collect_block(lines, start):

    body = []

    i = start

    while (
        i < len(lines)
        and lines[i].startswith("    ")
    ):
        body.append(
            lines[i][4:]
        )
        i += 1

    return body, i


def run_block(
    lines,
    variables,
    functions
):
    i = 0

    while i < len(lines):

        original_line = lines[i]
        line = original_line.strip()

        if not line or line.startswith("#"):
            i += 1
            continue

        if (
            line.startswith("if ")
            and line.endswith(":")
        ):

            condition = line[3:-1].strip()

            condition_value = get_value(
                condition,
                variables,
                functions
            )

            i += 1

            if i < len(lines):
                true_line = lines[i]

            if condition_value:

                if i < len(lines):
                    execute_line(
                        true_line,
                        variables,
                        functions
                    )

            i += 1

            if (
                i < len(lines)
                and lines[i].strip() == "else:"
            ):

                i += 1

                if i < len(lines):
                    else_line = lines[i]

                    if not condition_value:
                        execute_line(
                            else_line,
                            variables,
                            functions
                        )

                i += 1

            continue

        if (
            line.startswith("while ")
            and line.endswith(":")
        ):

            condition = line[6:-1].strip()

            i += 1

            body = []

            while (
                i < len(lines)
                and lines[i].startswith("    ")
            ):
                body.append(
                    lines[i][4:]
                )
                i += 1

            while get_value(
                condition,
                variables,
                functions
            ):

                run_block(
                    body,
                    variables,
                    functions
                )

            continue

        try:

            execute_line(
                line,
                variables,
                functions
            )

        except ReturnValue:

            raise

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

            header = line[9:-1].strip()

            match = re.fullmatch(
                r'([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)',
                header
            )

            if not match:

                raise VeltoError(
                    f"Invalid function definition: {line}"
                )

            name = match.group(1)

            parameter_text = match.group(2).strip()

            if parameter_text:

                parameters = [
                    p.strip()
                    for p in parameter_text.split(",")
                ]

            else:

                parameters = []

            for parameter in parameters:

                if not re.fullmatch(
                    r'[a-zA-Z_][a-zA-Z0-9_]*',
                    parameter
                ):

                    raise VeltoError(
                        f"Invalid parameter: {parameter}"
                    )

            i += 1

            body = []

            while (
                i < len(lines)
                and lines[i].startswith("    ")
            ):

                body.append(
                    lines[i][4:]
                )

                i += 1

            functions[name] = (
                parameters,
                body
            )

            continue

        i += 1

    i = 0

    while i < len(lines):

        line = lines[i].strip()

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

                result = get_value(
                    condition,
                    variables,
                    functions
                )

                i += 1

                if i < len(lines):

                    true_line = lines[i]

                    if result:

                        execute_line(
                            true_line,
                            variables,
                            functions
                        )

                i += 1

                if (
                    i < len(lines)
                    and lines[i].strip() == "else:"
                ):

                    i += 1

                    if i < len(lines):

                        else_line = lines[i]

                        if not result:

                            execute_line(
                                else_line,
                                variables,
                                functions
                            )

                    i += 1

                continue

            if (
                line.startswith("while ")
                and line.endswith(":")
            ):

                condition = line[6:-1].strip()

                i += 1

                body = []

                while (
                    i < len(lines)
                    and lines[i].startswith("    ")
                ):

                    body.append(
                        lines[i][4:]
                    )

                    i += 1

                while get_value(
                    condition,
                    variables,
                    functions
                ):

                    run_block(
                        body,
                        variables,
                        functions
                    )

                continue

            execute_line(
                line,
                variables,
                functions
            )

        except ReturnValue:

            print(
                "Velto Error: "
                "return can only be used inside a function"
            )

        except VeltoError as error:

            print()
            print(
                f"Velto Error on line "
                f"{i + 1}:"
            )

            print(
                f"  {lines[i]}"
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

