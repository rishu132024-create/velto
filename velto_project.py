import os
import sys

def create_project(name):
    if not name:
        print("Velto Error: Project name is required")
        return 1

    if os.path.exists(name):
        print("Velto Error: Project already exists")
        return 1

    os.makedirs(os.path.join(name, "packages"))

    with open(os.path.join(name, "main.vlt"), "w", encoding="utf-8") as file:
        file.write('say "Hello from Velto!"\n')

    with open(os.path.join(name, "velto.toml"), "w", encoding="utf-8") as file:
        file.write(
            '[project]\n'
            'name = "' + name + '"\n'
            'version = "0.1.0"\n'
            'language = "velto"\n'
        )

    print("Created Velto project: " + name)
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python velto_project.py <project-name>")
        sys.exit(1)

    sys.exit(create_project(sys.argv[1]))
