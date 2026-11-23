import os

def find_config(start=None):
    current = os.path.abspath(start or os.getcwd())

    while True:
        path = os.path.join(current, "velto.toml")

        if os.path.isfile(path):
            return path

        parent = os.path.dirname(current)

        if parent == current:
            return None

        current = parent

def read_config(path):
    config = {
        "name": "",
        "version": "0.1.0",
        "language": "velto",
        "dependencies": {}
    }

    section = ""

    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip()
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            if section == "project":
                if key in config:
                    config[key] = value

            elif section == "dependencies":
                config["dependencies"][key] = value

    return config
