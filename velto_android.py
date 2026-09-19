import json
import os


class VeltoAndroidError(Exception):
    pass


class AndroidProject:
    def __init__(
        self,
        name,
        package_name,
        version="1.0.0",
        min_sdk=23
    ):
        self.name = str(name)
        self.package_name = str(package_name)
        self.version = str(version)
        self.min_sdk = int(min_sdk)

    def config(self):
        return {
            "name": self.name,
            "package": self.package_name,
            "version": self.version,
            "min_sdk": self.min_sdk
        }

    def create(self, directory):
        directory = os.path.abspath(directory)

        os.makedirs(directory, exist_ok=True)

        config_path = os.path.join(
            directory,
            "android.json"
        )

        with open(
            config_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.config(),
                file,
                indent=4
            )

        source_directory = os.path.join(
            directory,
            "src"
        )

        assets_directory = os.path.join(
            directory,
            "assets"
        )

        os.makedirs(
            source_directory,
            exist_ok=True
        )

        os.makedirs(
            assets_directory,
            exist_ok=True
        )

        main_file = os.path.join(
            source_directory,
            "main.vlt"
        )

        if not os.path.exists(main_file):
            with open(
                main_file,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(
                    'say "Hello from Velto Android!"\n'
                )

        return True

    def info(self):
        return self.config()


def create_android_project(
    name,
    package_name,
    directory,
    version="1.0.0",
    min_sdk=23
):
    project = AndroidProject(
        name,
        package_name,
        version,
        min_sdk
    )

    project.create(directory)

    return project
