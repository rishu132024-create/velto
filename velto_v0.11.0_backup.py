import sys
import os
import re

variables = {}
functions = {}
modules = {}

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

    if current.strip():
        args.append(current.strip())

    return args

def get_value(expression, local_vars=None):
    expression = expression.strip()

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

        return execute_function_call(function_name, values, local_vars)

    try:
        return eval(expression, {"__builtins__": {}}, env)
    except Exception:
        if expression in env:
            return env[expression]
        raise Exception("Invalid expression: " + expression)

def execute_function_call(function_name, args, caller_vars=None):
    if "." in function_name:
        parts = function_name.split(".", 1)
        module_name = parts[0]
        function_part = parts[1]

        if module_name in modules:
            module_data = modules[module_name]

            if function_part in module_data["functions"]:
                function_data = module_data["functions"][function_part]
                return execute_function(
                    function_data,
                    args,
                    module_data["variables"]
                )

    if function_name not in functions:
        raise Exception("Function not found: " + function_name)

    return execute_function(
        functions[function_name],
        args,
        caller_vars
    )

def execute_function(function_data, args, parent_vars=None):
    params = function_data["params"]
    body = function_data["body"]

    local_vars = {}

    if parent_vars:
        local_vars.update(parent_vars)

    for index, param in enumerate(params):
        if index < len(args):
            local_vars[param] = args[index]
        else:
            local_vars[param] = None

    try:
        execute_block(body, local_vars)
    except ReturnValue as result:
        return result.value

    return None

def execute_block(lines, local_vars=None):
    i = 0

    while i < len(lines):
        raw_line = lines[i]
        stripped = raw_line.strip()

        if not stripped:
            i += 1
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if stripped.startswith("function ") and stripped.endswith(":"):
            match = re.match(
                r"function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\):",
                stripped
            )

            if not match:
                raise Exception("Invalid function definition")

            name = match.group(1)
            params_text = match.group(2)

            params = []
            if params_text.strip():
                params = [x.strip() for x in params_text.split(",")]

            body = []
            j = i + 1

            while j < len(lines):
                next_line = lines[j]

                if not next_line.strip():
                    body.append(next_line)
                    j += 1
                    continue

                next_indent = len(next_line) - len(next_line.lstrip(" "))

                if next_indent <= indent:
                    break

                body.append(next_line[4:])
                j += 1

            target = functions

            if local_vars is not None and "__module__" in local_vars:
                target = local_vars["__module_functions__"]

            target[name] = {
                "params": params,
                "body": body
            }

            i = j
            continue

        if stripped.startswith("import "):
            module_name = stripped[7:].strip()

            base_dir = local_vars.get(
                "__base_dir__",
                os.getcwd()
            ) if local_vars else os.getcwd()

            load_module(module_name, base_dir)

            i += 1
            continue

        if stripped.startswith("if ") and stripped.endswith(":"):
            condition = stripped[3:-1].strip()
            condition_value = get_value(condition, local_vars)

            true_block = []
            false_block = []

            j = i + 1

            while j < len(lines):
                next_line = lines[j]

                if not next_line.strip():
                    j += 1
                    continue

                next_indent = len(next_line) - len(next_line.lstrip(" "))

                if next_indent <= indent:
                    break

                true_block.append(next_line[4:])
                j += 1

            if j < len(lines) and lines[j].strip() == "else:":
                j += 1

                while j < len(lines):
                    next_line = lines[j]

                    if not next_line.strip():
                        j += 1
                        continue

                    next_indent = len(next_line) - len(next_line.lstrip(" "))

                    if next_indent <= indent:
                        break

                    false_block.append(next_line[4:])
                    j += 1

            if condition_value:
                execute_block(true_block, local_vars)
            else:
                execute_block(false_block, local_vars)

            i = j
            continue

        if stripped.startswith("while ") and stripped.endswith(":"):
            condition = stripped[6:-1].strip()

            loop_block = []
            j = i + 1

            while j < len(lines):
                next_line = lines[j]

                if not next_line.strip():
                    j += 1
                    continue

                next_indent = len(next_line) - len(next_line.lstrip(" "))

                if next_indent <= indent:
                    break

                loop_block.append(next_line[4:])
                j += 1

            guard = 0

            while get_value(condition, local_vars):
                execute_block(loop_block, local_vars)

                guard += 1

                if guard > 100000:
                    raise Exception("Possible infinite loop")

            i = j
            continue

        if stripped.startswith("for ") and stripped.endswith(":"):
            match = re.match(
                r"for\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\s+(.+):",
                stripped
            )

            if not match:
                raise Exception("Invalid for loop")

            variable_name = match.group(1)
            iterable_expression = match.group(2)

            iterable = get_value(iterable_expression, local_vars)

            loop_block = []
            j = i + 1

            while j < len(lines):
                next_line = lines[j]

                if not next_line.strip():
                    j += 1
                    continue

                next_indent = len(next_line) - len(next_line.lstrip(" "))

                if next_indent <= indent:
                    break

                loop_block.append(next_line[4:])
                j += 1

            for item in iterable:
                if local_vars is not None:
                    local_vars[variable_name] = item
                else:
                    variables[variable_name] = item

                execute_block(loop_block, local_vars)

            i = j
            continue

        if stripped.startswith("return "):
            expression = stripped[7:].strip()
            value = get_value(expression, local_vars)
            raise ReturnValue(value)

        if stripped == "return":
            raise ReturnValue(None)

        if stripped.startswith("say "):
            expression = stripped[4:].strip()
            value = get_value(expression, local_vars)
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

            if local_vars is not None and variable_name in local_vars:
                target_list = local_vars[variable_name]
            elif variable_name in variables:
                target_list = variables[variable_name]
            else:
                raise Exception("Variable not found: " + variable_name)

            index = get_value(index_expression, local_vars)
            value = get_value(value_expression, local_vars)

            target_list[index] = value

            i += 1
            continue

        assignment = re.match(
            r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$",
            stripped
        )

        if assignment:
            variable_name = assignment.group(1)
            expression = assignment.group(2)

            value = get_value(expression, local_vars)

            if local_vars is not None:
                local_vars[variable_name] = value
            else:
                variables[variable_name] = value

            i += 1
            continue

        get_value(stripped, local_vars)

        i += 1

def load_module(module_name, base_dir):
    if module_name in modules:
        return

    possible_files = [
        os.path.join(base_dir, module_name + ".vlt"),
        os.path.join(os.getcwd(), module_name + ".vlt"),
        os.path.join(os.getcwd(), "examples", module_name + ".vlt")
    ]

    filename = None

    for path in possible_files:
        if os.path.exists(path):
            filename = path
            break

    if filename is None:
        raise Exception("Module not found: " + module_name + ".vlt")

    with open(filename, "r", encoding="utf-8") as file:
        module_lines = file.readlines()

    module_variables = {
        "__base_dir__": os.path.dirname(os.path.abspath(filename))
    }

    module_functions = {}

    module_variables["__module__"] = module_name
    module_variables["__module_functions__"] = module_functions

    old_variables = variables.copy()
    old_functions = functions.copy()

    modules[module_name] = {
        "variables": module_variables,
        "functions": module_functions
    }

    try:
        execute_block(module_lines, module_variables)
    except Exception:
        modules.pop(module_name, None)
        variables.clear()
        variables.update(old_variables)
        functions.clear()
        functions.update(old_functions)
        raise

def load_program(filename):
    global variables
    global functions
    global modules

    variables = {}
    functions = {}
    modules = {}

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    base_dir = os.path.dirname(os.path.abspath(filename))

    program_vars = {
        "__base_dir__": base_dir
    }

    execute_block(lines, program_vars)

def main():
    if len(sys.argv) != 2:
        print("Usage: python velto.py <file.vlt>")
        return

    filename = sys.argv[1]

    if not os.path.exists(filename):
        print("Velto Error: File not found: " + filename)
        return

    try:
        load_program(filename)
    except ReturnValue:
        print("Velto Error: return outside function")
    except Exception as error:
        print("Velto Error: " + str(error))

if __name__ == "__main__":
    main()
