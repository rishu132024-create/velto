import sys
import re


class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value


def split_arguments(text):
    args = []
    current = ""
    depth = 0
    quote = None

    for char in text:
        if quote:
            current += char
            if char == quote:
                quote = None
            continue

        if char in ('"', "'"):
            quote = char
            current += char
        elif char in "([{":
            depth += 1
            current += char
        elif char in ")]}":
            depth -= 1
            current += char
        elif char == "," and depth == 0:
            args.append(current.strip())
            current = ""
        else:
            current += char

    if current.strip():
        args.append(current.strip())

    return args


def prepare_expression(expr):
    expr = re.sub(r"\btrue\b", "True", expr)
    expr = re.sub(r"\bfalse\b", "False", expr)
    return expr


def calculate(expr, variables, functions):
    expr = expr.strip()

    match = re.fullmatch(r"([A-Za-z_]\w*)\((.*)\)", expr)

    if match:
        name = match.group(1)
        args_text = match.group(2)

        if name in functions:
            args = []

            if args_text.strip():
                for arg in split_arguments(args_text):
                    args.append(get_value(arg, variables, functions))

            return execute_function(name, args, functions)

    env = {}

    for name, value in variables.items():
        env[name] = value

    prepared = prepare_expression(expr)

    try:
        return eval(
            prepared,
            {"__builtins__": {}},
            env
        )

    except NameError as e:
        raise ValueError(f"Unknown value: {e}")

    except IndexError:
        raise ValueError("Index out of range")

    except TypeError as e:
        raise ValueError(str(e))

    except SyntaxError:
        raise ValueError(f"Invalid expression: {expr}")

    except Exception as e:
        raise ValueError(str(e))


def get_value(text, variables, functions):
    text = text.strip()

    if not text:
        return ""

    match = re.fullmatch(r"([A-Za-z_]\w*)\((.*)\)", text)

    if match:
        name = match.group(1)
        args_text = match.group(2)

        if name in functions:
            args = []

            if args_text.strip():
                for arg in split_arguments(args_text):
                    args.append(get_value(arg, variables, functions))

            return execute_function(name, args, functions)

    if (
        len(text) >= 2
        and text[0] in ('"', "'")
        and text[-1] == text[0]
    ):
        return text[1:-1]

    if text == "true":
        return True

    if text == "false":
        return False

    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        pass

    try:
        return calculate(text, variables, functions)
    except ValueError:
        pass

    if text in variables:
        return variables[text]

    raise ValueError(f"Unknown value: {text}")


def format_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, list):
        return "[" + ", ".join(format_value(x) for x in value) + "]"

    if isinstance(value, str):
        return f'"{value}"'

    return str(value)


def execute_function(name, args, functions):
    if name not in functions:
        raise ValueError(f"Unknown function: {name}")

    params, body = functions[name]

    if len(args) != len(params):
        raise ValueError(
            f"Function '{name}' expects {len(params)} argument(s), got {len(args)}"
        )

    local_variables = {}

    for param, value in zip(params, args):
        local_variables[param] = value

    try:
        execute_lines(body, local_variables, functions)
    except ReturnValue as ret:
        return ret.value

    return None


def collect_block(lines, start_index):
    body = []
    i = start_index

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            body.append(line)
            i += 1
            continue

        if line.startswith("    "):
            body.append(line[4:])
            i += 1
        else:
            break

    return body, i


def execute_lines(lines, variables, functions):
    i = 0
    loop_counter = 0
    max_loops = 100000

    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.strip()

        if not line:
            i += 1
            continue

        if line.startswith("#"):
            i += 1
            continue

        if line.startswith("function "):
            match = re.match(
                r"function\s+([A-Za-z_]\w*)\s*\((.*?)\)\s*:",
                line
            )

            if not match:
                raise ValueError("Invalid function declaration")

            name = match.group(1)
            params_text = match.group(2)

            if params_text.strip():
                params = [
                    p.strip()
                    for p in split_arguments(params_text)
                ]
            else:
                params = []

            body, next_index = collect_block(lines, i + 1)

            functions[name] = (params, body)

            i = next_index
            continue

        if line.startswith("return"):
            value_text = line[6:].strip()

            if value_text:
                value = get_value(
                    value_text,
                    variables,
                    functions
                )
            else:
                value = None

            raise ReturnValue(value)

        if line.startswith("if ") and line.endswith(":"):
            condition = line[3:-1].strip()

            condition_value = get_value(
                condition,
                variables,
                functions
            )

            true_body, next_index = collect_block(lines, i + 1)

            false_body = []
            final_index = next_index

            if (
                next_index < len(lines)
                and lines[next_index].strip() == "else:"
            ):
                false_body, final_index = collect_block(
                    lines,
                    next_index + 1
                )

            if condition_value:
                execute_lines(
                    true_body,
                    variables,
                    functions
                )
            else:
                execute_lines(
                    false_body,
                    variables,
                    functions
                )

            i = final_index
            continue

        if line.startswith("while ") and line.endswith(":"):
            condition = line[6:-1].strip()

            body, next_index = collect_block(
                lines,
                i + 1
            )

            while get_value(
                condition,
                variables,
                functions
            ):
                loop_counter += 1

                if loop_counter > max_loops:
                    raise ValueError(
                        "Loop stopped: too many iterations"
                    )

                execute_lines(
                    body,
                    variables,
                    functions
                )

            i = next_index
            continue

        if line.startswith("for ") and line.endswith(":"):
            match = re.match(
                r"for\s+([A-Za-z_]\w*)\s+in\s+(.+):",
                line
            )

            if not match:
                raise ValueError("Invalid for loop")

            variable_name = match.group(1)
            collection_expression = match.group(2).strip()

            collection = get_value(
                collection_expression,
                variables,
                functions
            )

            if not isinstance(collection, (list, str)):
                raise ValueError(
                    "for loop needs a list or string"
                )

            body, next_index = collect_block(
                lines,
                i + 1
            )

            for item in collection:
                loop_counter += 1

                if loop_counter > max_loops:
                    raise ValueError(
                        "Loop stopped: too many iterations"
                    )

                variables[variable_name] = item

                execute_lines(
                    body,
                    variables,
                    functions
                )

            i = next_index
            continue

        if line.startswith("say "):
            expression = line[4:].strip()

            value = get_value(
                expression,
                variables,
                functions
            )

            print(format_value(value))

            i += 1
            continue

        match = re.match(
            r"^([A-Za-z_]\w*)\[(.+)\]\s*=\s*(.+)$",
            line
        )

        if match:
            variable_name = match.group(1)
            index_expression = match.group(2)
            value_expression = match.group(3)

            if variable_name not in variables:
                raise ValueError(
                    f"Unknown variable: {variable_name}"
                )

            collection = variables[variable_name]

            index = get_value(
                index_expression,
                variables,
                functions
            )

            value = get_value(
                value_expression,
                variables,
                functions
            )

            try:
                collection[index] = value
            except IndexError:
                raise ValueError(
                    "Index out of range"
                )
            except TypeError:
                raise ValueError(
                    "Invalid index assignment"
                )

            i += 1
            continue

        match = re.match(
            r"^([A-Za-z_]\w*)\s*=\s*(.+)$",
            line
        )

        if match:
            variable_name = match.group(1)
            expression = match.group(2).strip()

            value = get_value(
                expression,
                variables,
                functions
            )

            variables[variable_name] = value

            i += 1
            continue

        match = re.fullmatch(
            r"([A-Za-z_]\w*)\((.*)\)",
            line
        )

        if match:
            name = match.group(1)
            args_text = match.group(2)

            if name not in functions:
                raise ValueError(
                    f"Unknown function: {name}"
                )

            args = []

            if args_text.strip():
                for arg in split_arguments(args_text):
                    args.append(
                        get_value(
                            arg,
                            variables,
                            functions
                        )
                    )

            execute_function(
                name,
                args,
                functions
            )

            i += 1
            continue

        raise ValueError(
            f"Unknown statement: {line}"
        )


def run_file(filename):
    try:
        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:
            lines = file.readlines()

        variables = {}
        functions = {}

        execute_lines(
            lines,
            variables,
            functions
        )

    except ReturnValue:
        print("Velto Error: return outside function")

    except Exception as e:
        print(f"Velto Error: {e}")


def main():
    if len(sys.argv) != 2:
        print("Velto 0.9.0")
        print("Usage: python velto.py <file.vlt>")
        return

    filename = sys.argv[1]

    if not filename.endswith(".vlt"):
        print("Velto Error: file must end with .vlt")
        return

    run_file(filename)


if __name__ == "__main__":
    main()
