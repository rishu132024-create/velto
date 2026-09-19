import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

VELTO_HOME = os.path.expanduser("~/velto")

if VELTO_HOME not in sys.path:
    sys.path.insert(0, VELTO_HOME)


class VeltoIDEHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def send_json(self, status, data):
        body = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, filename, content_type):
        path = os.path.join(
            os.path.dirname(__file__),
            filename
        )

        if not os.path.isfile(path):
            self.send_error(404)
            return

        with open(
            path,
            "rb"
        ) as file:
            body = file.read()

        self.send_response(200)
        self.send_header(
            "Content-Type",
            content_type
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.send_file(
                "index.html",
                "text/html; charset=utf-8"
            )
            return

        if self.path == "/style.css":
            self.send_file(
                "style.css",
                "text/css; charset=utf-8"
            )
            return

        if self.path == "/script.js":
            self.send_file(
                "script.js",
                "application/javascript; charset=utf-8"
            )
            return

        self.send_error(404)

    def do_POST(self):
        if self.path != "/run":
            self.send_json(
                404,
                {
                    "error": "Route not found"
                }
            )
            return

        length = int(
            self.headers.get(
                "Content-Length",
                "0"
            )
        )

        body = self.rfile.read(length)

        try:
            data = json.loads(
                body.decode("utf-8")
            )
        except Exception:
            self.send_json(
                400,
                {
                    "error": "Invalid JSON"
                }
            )
            return

        code = data.get("code", "")

        if not isinstance(code, str):
            self.send_json(
                400,
                {
                    "error": "Code must be text"
                }
            )
            return

        self.send_json(
            200,
            {
                "output": "Velto Web IDE received your code.\n\nExecution backend will be connected in the next stage."
            }
        )


def main():
    server = HTTPServer(
        ("127.0.0.1", 8095),
        VeltoIDEHandler
    )

    print(
        "Velto Web IDE running"
    )

    print(
        "http://127.0.0.1:8095"
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
