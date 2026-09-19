import os

def create_project(name):
    if not name:
        print("Velto Error: Project name is required")
        return 1

    if os.path.exists(name):
        print("Velto Error: Project already exists")
        return 1

    os.makedirs(os.path.join(name, "packages"))

    main_file = os.path.join(name, "main.vlt")
    config_file = os.path.join(name, "velto.toml")

    with open(main_file, "w", encoding="utf-8") as file:
        file.write('say "Hello from Velto!"\n')

    with open(config_file, "w", encoding="utf-8") as file:
        file.write(
            '[project]\n'
            'name = "' + name + '"\n'
            'version = "0.1.0"\n'
            'language = "velto"\n'
        )

    print("Created Velto project: " + name)
    print("")
    print(name + "/")
    print("├── main.vlt")
    print("├── velto.toml")
    print("└── packages/")

    return 0
