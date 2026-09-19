import json

from velto_http import add_route


_routes = {}


def _json_response(data):
    return json.dumps(
        data,
        ensure_ascii=False
    )


def get(path, handler):
    return _add_route(
        "GET",
        path,
        handler
    )


def post(path, handler):
    return _add_route(
        "POST",
        path,
        handler
    )


def _add_route(method, path, handler):
    if not isinstance(path, str):
        raise ValueError(
            "Route path must be a string"
        )

    if not path.startswith("/"):
        raise ValueError(
            "Route path must start with /"
        )

    if not callable(handler):
        raise ValueError(
            "Route handler must be callable"
        )

    _routes[(method, path)] = handler

    def route_handler(
        request_method,
        request_path,
        data
    ):
        current = _routes.get(
            (request_method, request_path)
        )

        if current is None:
            return _json_response(
                {
                    "error": "Route not found"
                }
            )

        result = current(
            request_method,
            request_path,
            data
        )

        if isinstance(result, dict):
            return _json_response(result)

        return str(result)

    add_route(
        path,
        route_handler
    )

    return True


def json_response(data):
    return _json_response(data)


def routes():
    return [
        {
            "method": method,
            "path": path
        }
        for method, path in _routes
    ]
