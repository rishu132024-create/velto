import sys
import os
import re

variables = {}
functions = {}
modules = {}
current_file = ""
current_line = 0

class VeltoError(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(message)

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

def error(message):
    raise VeltoError(message, current_line)

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
        else:
            if char in ['"', "'"]:
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

    if quote:
        error("Unclosed string")

    if depth != 0:
        error("Unclosed brackets")

    if current.strip():
        args.append(current.strip())

    return args

def builtin_function(name, args):
    try:
        if name == "len":
            if len(args) != 1:
                error("len() expects 1 argument")
            return len(args[0])

        if name == "str":
            if len(args) != 1:
                error("str() expects 1 argument")
            return str(args[0])

        if name == "int":
            if len(args) != 1:
                error("int() expects 1 argument")
            return int(args[0])

        if name == "float":
            if len(args) != 1:
                error("float() expects 1 argument")
            return float(args[0])

        if name == "abs":
            if len(args) != 1:
                error("abs() expects 1 argument")
            return abs(args[0])

        if name == "min":
            if len(args) < 1:
                error("min() expects at least 1 argument")
            return min(args)

        if name == "max":
            if len(args) < 1:
                error("max() expects at least 1 argument")
            return max(args)

        if name == "range":
            if len(args) == 1:
                return list(range(args[0]))

            if len(args) == 2:
                return list(range(args[0], args[1]))

            if len(args) == 3:
                return list(range(args[0], args[1], args[2]))

            error("range() expects 1 to 3 arguments")

        return None

    except VeltoError:
        raise
    except ValueError:
        error("Invalid value for " + name + "()")
    except TypeError:
        error("Invalid argument type for " + name + "()")

def is_builtin(name):
    return name in [
        "len",
        "str",
        "int",
        "float",
        "abs",
        "min",
        "max",
        "range"
    ]

def get_value(expression, local_vars=None):
    expression = expression.strip()

    if not expression:
        error("Empty expression")

    env = {}
    env.update(variables)

    if local_vars:
        env.update(local_vars)

    for module_name, module_data in modules.items():
        env[module_name] = module_data

    expression = re.sub(r"\btrue\b", "True", expression)
    expression = re.sub(r"\bfalse\b", "False", expression)
    expression = re.sub(r"\bnull\b", "None", expression)

    call_match = re.fullmatch(
        r"([A-Za-z_][A-Za-z0-9_\.]*)\s*\((.*)\)",
        expression
    )

    if call_match:
        function_name = call_match.group(1)
        args_text = call_match.group(2)
        args = split_arguments(args_text)

        values = []

        for arg in args:
            values.append(get_value(arg, local_vars))

        if "." not in function_name and is_builtin(function_name):
            return builtin_function(function_name, values)

        return execute_function_call(
            function_name,
            values,
            local_vars
        )

    try:
        return eval(
            expression,
            {"__builtins__": {}},
            env
        )

    except NameError:
        name_match = re.search(
            r"[A-Za-z_][A-Za-z0-9_]*",
            expression
        )

        if name_match:
            name = name_match.group(0)

            if name not in env and not is_builtin(name):
                error("Variable not found: " + name)

        error("Invalid expression: " + expression)

    except SyntaxError:
        error("Invalid syntax: " + expression)

    except TypeError:
        error("Invalid operation: " + expression)

    except IndexError:
        error("List or string index out of range")

    except Exception:
        error("Could not evaluate: " + expression)

def execute_function_call(function_name, args, caller_vars=None):
    if "." in function_name:
        parts = function_name.split(".", 1)
        module_name = parts[0]
        function_part = parts[1]

        if module_name not in modules:
            error("Module not found: " + module_name)

        module_data = modules[module_name]

        if function_part not in module_data["functions"]:
            error(
                "Function not found: "
                + function_name
            )

        return execute_function(
            module_data["functions"][function_part],
            args,
            module_data["variables"]
        )

    if function_name not in functions:
        error("Function not found: " + function_name)

    return execute_function(
        functions[function_name],
        args,
        caller_vars
    )

def execute_function(function_data, args, parent_vars=None):
    params = function_data["params"]
    body = function_data["body"]

    if len(args) != len(params):
        error(
            "Function expects "
            + str(len(params))
            + " argument(s), got "
            + str(len(args))
        )

    local_vars = {}

    if parent_vars:
        for key, value in parent_vars.items():
            if not key.startswith("__"):
                local_vars[key] = value

    for index, param in enumerate(params):
        local_vars[param] = args[index]

    try:
        execute_block(body, local_vars)
    except ReturnValue as result:
        return result.value

    return None

def collect_block(lines, start, indent):
    block = []
    j = start

    while j < len(lines):
        next_line = lines[j]

        if not next_line.strip():
            block.append(next_line)
            j += 1
            continue

        next_indent = len(next_line) - len(
            next_line.lstrip(" ")
        )

        if next_indent <= indent:
            break

        if next_indent < indent + 4:
            error("Invalid indentation")

        block.append(next_line[4:])
        j += 1

    return block, j

def execute_block(lines, local_vars=None):
    global current_line

    i = 0

    while i < len(lines):
        current_line = i + 1

        raw_line = lines[i]
        stripped = raw_line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("function ") and stripped.endswith(":"):
            match = re.match(
                r"function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\):",
                stripped
            )

            if not match:
                error("Invalid function definition")

            name = match.group(1)
            params_text = match.group(2)

            params = []

            if params_text.strip():
                params = [
                    x.strip()
                    for x in params_text.split(",")
                ]

            for param in params:
                if not re.fullmatch(
                    r"[A-Za-z_][A-Za-z0-9_]*",
                    param
                ):
                    error(
                        "Invalid parameter name: "
                        + param
                    )

            indent = len(raw_line) - len(
                raw_line.lstrip(" ")
            )

            body, j = collect_block(
                lines,
                i + 1,
                indent
            )

            functions[name] = {
                "params": params,
                "body": body
            }

            i = j
            continue

        if stripped.startswith("import "):
            module_name = stripped[7:].strip()

            if not re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*",
                module_name
            ):
                error(
                    "Invalid module name: "
                    + module_name
                )

            base_dir = os.getcwd()

            if local_vars and "__base_dir__" in local_vars:
                base_dir = local_vars["__base_dir__"]

            load_module(
                module_name,
                base_dir
            )

            i += 1
            continue

        if stripped.startswith("if ") and stripped.endswith(":"):
            condition = stripped[3:-1].strip()

            if not condition:
                error("Empty if condition")

            condition_value = get_value(
                condition,
                local_vars
            )

            indent = len(raw_line) - len(
                raw_line.lstrip(" ")
            )

            true_block, j = collect_block(
                lines,
                i + 1,
                indent
            )

            false_block = []

            if j < len(lines):
                if lines[j].strip() == "else:":
                    false_block, j = collect_block(
                        lines,
                        j + 1,
                        indent
                    )

            if condition_value:
                execute_block(
                    true_block,
                    local_vars
                )
            else:
                execute_block(
                    false_block,
                    local_vars
                )

            i = j
            continue

        if stripped.startswith("while ") and stripped.endswith(":"):
            condition = stripped[6:-1].strip()

            if not condition:
                error("Empty while condition")

            indent = len(raw_line) - len(
                raw_line.lstrip(" ")
            )

            loop_block, j = collect_block(
                lines,
                i + 1,
                indent
            )

            guard = 0

            while get_value(
                condition,
                local_vars
            ):
                execute_block(
                    loop_block,
                    local_vars
                )

                guard += 1

                if guard > 100000:
                    error("Possible infinite loop")

            i = j
            continue

        if stripped.startswith("for ") and stripped.endswith(":"):
            match = re.match(
                r"for\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\s+(.+):",
                stripped
            )

            if not match:
                error("Invalid for loop")

            variable_name = match.group(1)
            iterable_expression = match.group(2)

            iterable = get_value(
                iterable_expression,
                local_vars
            )

            try:
                iterator = iter(iterable)
            except TypeError:
                error(
                    "Value is not iterable: "
                    + iterable_expression
                )

            indent = len(raw_line) - len(
                raw_line.lstrip(" ")
            )

            loop_block, j = collect_block(
                lines,
                i + 1,
                indent
            )

            for item in iterator:
                if local_vars is not None:
                    local_vars[variable_name] = item
                else:
                    variables[variable_name] = item

                execute_block(
                    loop_block,
                    local_vars
                )

            i = j
            continue

        if stripped == "else:":
            error("Unexpected else")

        if stripped.startswith("return "):
            expression = stripped[7:].strip()

            value = get_value(
                expression,
                local_vars
            )

            raise ReturnValue(value)

        if stripped == "return":
            raise ReturnValue(None)

        if stripped.startswith("say "):
            expression = stripped[4:].strip()

            value = get_value(
                expression,
                local_vars
            )

            print(value)

            i += 1
            continue

        list_assignment = re.match(
            r"^([A-Za-z_][A-Za-z0-9_]*)\[(.+)\]\s*=\s*(.+)$",
            stripped
        )

        if list_assignment:
            variable_name = list_assignment.group(1)
            index_expression = list_assignment.group(2)
            value_expression = list_assignment.group(3)

            if (
                local_vars is not None
                and variable_name in local_vars
            ):
                target_list = local_vars[variable_name]
            elif variable_name in variables:
                target_list = variables[variable_name]
            else:
                error(
                    "Variable not found: "
                    + variable_name
                )

            index = get_value(
                index_expression,
                local_vars
            )

            value = get_value(
                value_expression,
                local_vars
            )

            try:
                target_list[index] = value
            except TypeError:
                error(
                    "Value does not support index assignment: "
                    + variable_name
                )
            except IndexError:
                error("List index out of range")

            i += 1
            continue

        assignment = re.match(
            r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$",
            stripped
        )

        if assignment:
            variable_name = assignment.group(1)
            expression = assignment.group(2)

            value = get_value(
                expression,
                local_vars
            )

            if local_vars is not None:
                local_vars[variable_name] = value
            else:
                variables[variable_name] = value

            i += 1
            continue

        get_value(
            stripped,
            local_vars
        )

        i += 1

def load_module(module_name, base_dir):
    if module_name in modules:
        return

    possible_files = [
        os.path.join(
            base_dir,
            module_name + ".vlt"
        ),
        os.path.join(
            os.getcwd(),
            module_name + ".vlt"
        ),
        os.path.join(
            os.getcwd(),
            "examples",
            module_name + ".vlt"
        )
    ]

    filename = None

    for path in possible_files:
        if os.path.exists(path):
            filename = path
            break

    if filename is None:
        error(
            "Module not found: "
            + module_name
            + ".vlt"
        )

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as file:
        module_lines = file.readlines()

    module_variables = {
        "__base_dir__": os.path.dirname(
            os.path.abspath(filename)
        )
    }

    module_functions = {}

    modules[module_name] = {
        "variables": module_variables,
        "functions": module_functions
    }

    old_functions = functions.copy()

    try:
        execute_module(
            module_lines,
            module_variables,
            module_functions
        )
    except Exception:
        modules.pop(module_name, None)
        functions.clear()
        functions.update(old_functions)
        raise

def execute_module(
    lines,
    module_variables,
    module_functions
):
    global current_line

    i = 0

    while i < len(lines):
        current_line = i + 1

        raw_line = lines[i]
        stripped = raw_line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("function ") and stripped.endswith(":"):
            match = re.match(
                r"function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\):",
                stripped
            )

            if not match:
                error("Invalid function definition")

            name = match.group(1)
            params_text = match.group(2)

            params = []

            if params_text.strip():
                params = [
                    x.strip()
                    for x in params_text.split(",")
                ]

            indent = len(raw_line) - len(
                raw_line.lstrip(" ")
            )

            body, j = collect_block(
                lines,
                i + 1,
                indent
            )

            module_functions[name] = {
                "params": params,
                "body": body
            }

            i = j
            continue

        if stripped.startswith("say "):
            expression = stripped[4:].strip()

            value = get_value(
                expression,
                module_variables
            )

            print(value)

            i += 1
            continue

        assignment = re.match(
            r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$",
            stripped
        )

        if assignment:
            variable_name = assignment.group(1)
            expression = assignment.group(2)

            value = get_value(
                expression,
                module_variables
            )

            module_variables[variable_name] = value

            i += 1
            continue

        i += 1

def load_program(filename):
    global variables
    global functions
    global modules
    global current_file
    global current_line

    variables = {}
    functions = {}
    modules = {}
    current_file = filename
    current_line = 0

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as file:
        lines = file.readlines()

    base_dir = os.path.dirname(
        os.path.abspath(filename)
    )

    program_vars = {
        "__base_dir__": base_dir
    }

    execute_block(
        lines,
        program_vars
    )

def main():
    global current_file

    if len(sys.argv) != 2:
        print(
            "Usage: python velto.py <file.vlt>"
        )
        return

    filename = sys.argv[1]

    if not os.path.exists(filename):
        print(
            "Velto Error: File not found: "
            + filename
        )
        return

    current_file = filename

    try:
        load_program(filename)

    except ReturnValue:
        print(
            "Velto Error: "
            + filename
            + ":"
            + str(current_line)
            + ": return outside function"
        )

    except VeltoError as exc:
        if exc.line:
            print(
                "Velto Error: "
                + filename
                + ":"
                + str(exc.line)
            )
            print(exc.message)
        else:
            print(
                "Velto Error: "
                + filename
            )
            print(exc.message)

    except FileNotFoundError:
        print(
            "Velto Error: File not found: "
            + filename
        )

    except Exception as exc:
        print(
            "Velto Error: "
            + filename
            + ":"
            + str(current_line)
        )
        print(str(exc))

if __name__ == "__main__":
   
    main()
