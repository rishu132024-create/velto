import json
import os

REGISTRY_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "registry"
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

def search_packages(query=""):
    data = load_index()

    query = query.lower()

    results = []

    for package in data.get("packages", []):
        name = package.get("name", "").lower()
        description = package.get(
            "description",
            ""
        ).lower()

        if (
            not query
            or query in name
            or query in description
        ):
            results.append(package)

    return results

def show_packages(query=""):
    results = search_packages(query)

    if not results:
        print("No packages found")
        return 0

    print("Velto packages:")

    for package in results:
        name = package.get("name", "")
        version = package.get("version", "")
        description = package.get(
            "description",
            ""
        )

        print(
            name
            + " "
            + version
            + " - "
            + description
        )

    return 0

if __name__ == "__main__":
    import sys

    query = ""

    if len(sys.argv) > 1:
        query = sys.argv[1]

    raise SystemExit(
        show_packages(query)
    )
