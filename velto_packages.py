import os
import sys
import shutil

def get_project_root():
    current = os.path.abspath(os.getcwd())

    while True:
        config = os.path.join(current, "velto.toml")

        if os.path.isfile(config):
            return current

        parent = os.path.dirname(current)

        if parent == current:
            return None

        current = parent

def get_packages_dir():
    root = get_project_root()

    if root is None:
        return None

    directory = os.path.join(root, ".velto", "packages")
    os.makedirs(directory, exist_ok=True)

    return directory

def install_package(source):
    root = get_project_root()

    if root is None:
        print("Velto Error: velto.toml not found")
        return 1

    source = os.path.abspath(source)

    if not os.path.isdir(source):
        print("Velto Error: Package directory not found")
        return 1

    package_name = os.path.basename(source.rstrip(os.sep))

    if not package_name:
        print("Velto Error: Invalid package name")
        return 1

    packages_dir = get_packages_dir()
    destination = os.path.join(packages_dir, package_name)

    if os.path.exists(destination):
        print("Velto Error: Package already installed")
        return 1

    shutil.copytree(source, destination)

    print("Installed package: " + package_name)
    return 0

def list_packages():
    packages_dir = get_packages_dir()

    if packages_dir is None:
        print("Velto Error: velto.toml not found")
        return 1

    packages = []

    if os.path.isdir(packages_dir):
        packages = sorted(
            name
            for name in os.listdir(packages_dir)
            if os.path.isdir(os.path.join(packages_dir, name))
        )

    if not packages:
        print("No packages installed")
        return 0

    print("Installed packages:")

    for package in packages:
        print("  " + package)

    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python velto_packages.py install <package-path>")
        print("  python velto_packages.py list")
        return 1

    command = sys.argv[1]

    if command == "install":
        if len(sys.argv) < 3:
            print("Velto Error: Package path is required")
            return 1

        return install_package(sys.argv[2])

    if command == "list":
        return list_packages()

    print("Velto Error: Unknown package command")
    return 1

if __name__ == "__main__":
    sys.exit(main())
