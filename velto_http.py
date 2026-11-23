from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import json
import threading


class VeltoHTTPError(Exception):
    pass


_server = None
_thread = None


class VeltoHandler(BaseHTTPRequestHandler):
    routes = {}

    def log_message(self, format, *args):
        return

    def send_text(self, status, content):
        data = content.encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(data))
        )

        self.end_headers()

        self.wfile.write(data)

    def send_json(self, status, content):
        data = json.dumps(
            content,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(data))
        )

        self.end_headers()

        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        handler = self.routes.get(path)

        if handler is None:
            self.send_text(
                404,
                "404 Not Found"
            )
            return

        try:
            result = handler(
                "GET",
                path,
                {}
            )

            if isinstance(result, dict):
                self.send_json(200, result)
            else:
                self.send_text(
                    200,
                    str(result)
                )

        except Exception as error:
            self.send_text(
                500,
                "Internal Server Error: " + str(error)
            )

    def do_POST(self):
        path = self.path.split("?", 1)[0]

        handler = self.routes.get(path)

        if handler is None:
            self.send_text(
                404,
                "404 Not Found"
            )
            return

        try:
            length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            body = self.rfile.read(
                length
            ).decode(
                "utf-8",
                errors="replace"
            )

            result = handler(
                "POST",
                path,
                {
                    "body": body
                }
            )

            if isinstance(result, dict):
                self.send_json(200, result)
            else:
                self.send_text(
                    200,
                    str(result)
                )

        except Exception as error:
            self.send_text(
                500,
                "Internal Server Error: " + str(error)
            )


def add_route(path, handler):
    if not isinstance(path, str):
        raise VeltoHTTPError(
            "Route path must be a string"
        )

    if not path.startswith("/"):
        raise VeltoHTTPError(
            "Route path must start with /"
        )

    if not callable(handler):
        raise VeltoHTTPError(
            "Route handler must be callable"
        )

    VeltoHandler.routes[path] = handler


def start_server(host, port):
    global _server
    global _thread

    if _server is not None:
        raise VeltoHTTPError(
            "Server is already running"
        )

    try:
        _server = HTTPServer(
            (host, port),
            VeltoHandler
        )
    except OSError as error:
        raise VeltoHTTPError(
            "Unable to start server: " + str(error)
        )

    def run():
        _server.serve_forever()

    _thread = threading.Thread(
        target=run,
        daemon=True
    )

    _thread.start()

    return True


def stop_server():
    global _server
    global _thread

    if _server is None:
        return False

    _server.shutdown()
    _server.server_close()

    _server = None
    _thread = None

    VeltoHandler.routes.clear()

    return True
