import os
import sys

def create_project(name):
    if not name:
        print("Velto Error: Project name is required")
        return 1

    if os.path.exists(name):
        print("Velto Error: Project already exists")
        return 1

    project_path = os.path.abspath(name)

    directories = [
        "src",
        "tests",
        "packages"
    ]

    for directory in directories:
        os.makedirs(os.path.join(project_path, directory))

    main_file = os.path.join(project_path, "src", "main.vlt")

    with open(main_file, "w", encoding="utf-8") as file:
        file.write('say "Hello from Velto!"\n')

    config_file = os.path.join(project_path, "velto.toml")

    with open(config_file, "w", encoding="utf-8") as file:
        file.write(
            '[project]\n'
            'name = "' + name + '"\n'
            'version = "0.1.0"\n'
            'language = "velto"\n'
        )

    readme_file = os.path.join(project_path, "README.md")

    with open(readme_file, "w", encoding="utf-8") as file:
        file.write(
            "# " + name + "\n\n"
            "A Velto project.\n\n"
            "## Run\n\n"
            "```bash\n"
            "velto run src/main.vlt\n"
            "```\n"
        )

    gitignore_file = os.path.join(project_path, ".gitignore")

    with open(gitignore_file, "w", encoding="utf-8") as file:
        file.write(
            "__pycache__/\n"
            "*.pyc\n"
            ".velto/\n"
        )

    print("Created Velto project: " + name)
    print("")
    print(name + "/")
    print("├── src/")
    print("│   └── main.vlt")
    print("├── tests/")
    print("├── packages/")
    print("├── velto.toml")
    print("├── README.md")
    print("└── .gitignore")

    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python velto_project.py <project-name>")
        sys.exit(1)

    sys.exit(create_project(sys.argv[1]))
