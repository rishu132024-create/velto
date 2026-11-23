import json
import os

from velto_http import add_route
from velto_http import start_server
from velto_http import stop_server

_routes = {}

def get_project_root():
    current = os.path.abspath(os.getcwd())

    while True:
        config = os.path.join(current, "velto.toml")

        if os.path.isfile(config):
            return current

        parent = os.path.dirname(current)

        if parent == current:
            return os.path.abspath(os.getcwd())

        current = parent

def route(path, response):
    if not isinstance(path, str):
        raise ValueError("Route path must be a string")

    if not path.startswith("/"):
        raise ValueError("Route path must start with /")

    _routes[path] = response

    def handler(method, request_path, data):
        return _routes.get(request_path, "")

    add_route(path, handler)

    return True

def json_route(path, data):
    if not isinstance(data, dict):
        raise ValueError("JSON route data must be a dictionary")

    response = json.dumps(
        data,
        ensure_ascii=False
    )

    return route(path, response)

def render_template(name, values=None):
    if values is None:
        values = {}

    if not isinstance(values, dict):
        raise ValueError("Template values must be a dictionary")

    project_root = get_project_root()

    template_path = os.path.join(
        project_root,
        "templates",
        name
    )

    if not os.path.isfile(template_path):
        raise FileNotFoundError(
            "Template not found: " + template_path
        )

    with open(
        template_path,
        "r",
        encoding="utf-8"
    ) as file:
        content = file.read()

    for key, value in values.items():
        placeholder = "{{ " + str(key) + " }}"

        content = content.replace(
            placeholder,
            str(value)
        )

    return content

def template_route(path, name, values=None):
    return route(
        path,
        render_template(name, values)
    )

def start(port=8080, host="127.0.0.1"):
    return start_server(
        host,
        int(port)
    )

def stop():
    return stop_server()

def routes():
    return list(_routes.keys())
