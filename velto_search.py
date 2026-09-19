import json
import os
import sys


VELTO_HOME = os.path.dirname(
    os.path.abspath(__file__)
)

INDEX_FILE = os.path.join(
    VELTO_HOME,
    "registry",
    "index",
    "packages.json"
)


def load_packages():
    if not os.path.isfile(INDEX_FILE):
        return []

    try:
        with open(
            INDEX_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)
    except Exception:
        return []

    return data.get(
        "packages",
        []
    )


def search_packages(query):
    query = str(query).strip().lower()

    packages = load_packages()
    results = []

    for package in packages:
        name = str(
            package.get("name", "")
        )

        version = str(
            package.get("version", "")
        )

        description = str(
            package.get("description", "")
        )

        text = (
            name
            + " "
            + version
            + " "
            + description
        ).lower()

        if not query or query in text:
            results.append(package)

    return results


def show_results(query):
    results = search_packages(query)

    if not results:
        print("No Velto packages found")
        return 0

    print("Velto Packages")
    print("===============")

    for package in results:
        name = package.get(
            "name",
            ""
        )

        version = package.get(
            "version",
            ""
        )

        description = package.get(
            "description",
            ""
        )

        print("")
        print(
            name
            + " "
            + version
        )

        if description:
            print(
                "  "
                + description
            )

    print("")
    print(
        "Found:",
        len(results)
    )

    return 0


def main():
    query = ""

    if len(sys.argv) > 1:
        query = " ".join(
            sys.argv[1:]
        )

    return show_results(query)


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
