import sys
import os


class VeltoDebugger:
    def __init__(self):
        self.enabled = False
        self.variables = {}
        self.steps = []

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def set_variable(self, name, value):
        self.variables[str(name)] = value

    def get_variable(self, name):
        return self.variables.get(str(name))

    def has_variable(self, name):
        return str(name) in self.variables

    def remove_variable(self, name):
        self.variables.pop(str(name), None)

    def clear(self):
        self.variables.clear()
        self.steps.clear()

    def trace(self, line, source):
        if not self.enabled:
            return

        self.steps.append(
            {
                "line": int(line),
                "source": str(source)
            }
        )

    def variables_info(self):
        return dict(self.variables)

    def trace_info(self):
        return list(self.steps)

    def show_variables(self):
        if not self.variables:
            print("No variables")

            return

        print("Variables:")

        for name, value in self.variables.items():
            print(
                "  "
                + name
                + " = "
                + repr(value)
            )

    def show_trace(self):
        if not self.steps:
            print("No trace information")

            return

        print("Execution Trace:")

        for step in self.steps:
            print(
                "  Line "
                + str(step["line"])
                + ": "
                + step["source"]
            )


def debug_file(path):
    if not os.path.isfile(path):
        print(
            "Velto Debugger Error: File not found"
        )
        return 1

    debugger = VeltoDebugger()
    debugger.enable()

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        lines = file.readlines()

    for number, raw_line in enumerate(lines, 1):
        source = raw_line.strip()

        if not source:
            continue

        debugger.trace(
            number,
            source
        )

        if "=" in source:
            parts = source.split("=", 1)

            name = parts[0].strip()
            value = parts[1].strip()

            if name.isidentifier():
                debugger.set_variable(
                    name,
                    value
                )

    print(
        "Velto Debugger"
    )

    print(
        "File:",
        path
    )

    print("")

    debugger.show_variables()

    print("")

    debugger.show_trace()

    return 0


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python velto_debugger.py <file.vlt>"
        )
        return 1

    return debug_file(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
