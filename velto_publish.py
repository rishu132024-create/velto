import json
import os
import shutil
import sys

from velto_config import find_config, read_config

VELTO_HOME = os.path.dirname(
    os.path.abspath(__file__)
)

REGISTRY_DIR = os.path.join(
    VELTO_HOME,
    "registry"
)

PACKAGES_DIR = os.path.join(
    REGISTRY_DIR,
    "packages"
)

INDEX_FILE = os.path.join(
    REGISTRY_DIR,
    "index",
    "packages.json"
)

def load_index():
    if not os.path.isfile(INDEX_FILE):
        return {"packages": []}

    with open(
        INDEX_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)

def save_index(data):
    os.makedirs(
        os.path.dirname(INDEX_FILE),
        exist_ok=True
    )

    with open(
        INDEX_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=4
        )

def publish():
    config_path = find_config()

    if config_path is None:
        print("Velto Error: velto.toml not found")
        return 1

    config = read_config(config_path)

    name = config.get("name", "")
    version = config.get(
        "version",
        "0.1.0"
    )

    if not name:
        print("Velto Error: Package name is required")
        return 1

    project_root = os.path.dirname(
        os.path.abspath(config_path)
    )

    package_source = os.path.join(
        project_root,
        "src"
    )

    if not os.path.isdir(package_source):
        print("Velto Error: src directory not found")
        return 1

    package_directory = os.path.join(
        PACKAGES_DIR,
        name
    )

    version_directory = os.path.join(
        package_directory,
        version
    )

    if os.path.exists(version_directory):
        print(
            "Velto Error: Package version already exists"
        )
        return 1

    os.makedirs(
        package_directory,
        exist_ok=True
    )

    shutil.copytree(
        package_source,
        version_directory
    )

    metadata = {
        "name": name,
        "version": version,
        "language": config.get(
            "language",
            "velto"
        ),
        "entry": "src"
    }

    metadata_file = os.path.join(
        version_directory,
        "package.json"
    )

    with open(
        metadata_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            metadata,
            file,
            indent=4
        )

    index = load_index()

    packages = index.setdefault(
        "packages",
        []
    )

    packages = [
        package
        for package in packages
        if not (
            package.get("name") == name
            and package.get("version") == version
        )
    ]

    packages.append(
        {
            "name": name,
            "version": version,
            "description": "Velto package"
        }
    )

    index["packages"] = sorted(
        packages,
        key=lambda package: (
            package.get("name", ""),
            package.get("version", "")
        )
    )

    save_index(index)

    print(
        "Published package: "
        + name
        + " "
        + version
    )

    return 0

if __name__ == "__main__":
    sys.exit(publish())
