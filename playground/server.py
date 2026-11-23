import json
import os
import sys
import uuid
import time
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VELTO_HOME = Path.home() / "velto"
CLI_FILE = VELTO_HOME / "velto_cli.py"

sessions = {}
sessions_lock = threading.Lock()


class PlaygroundHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:8098")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > 100000:
            raise ValueError("Request too large")
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8") or "{}")

    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"

        file_path = (BASE_DIR / self.path.lstrip("/")).resolve()

        if BASE_DIR not in file_path.parents and file_path != BASE_DIR:
            self.send_error(403)
            return

        if not file_path.is_file():
            self.send_error(404)
            return

        content = file_path.read_bytes()

        if file_path.suffix == ".html":
            content_type = "text/html"
        elif file_path.suffix == ".css":
            content_type = "text/css"
        elif file_path.suffix == ".js":
            content_type = "application/javascript"
        else:
            content_type = "application/octet-stream"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        try:
            data = self.read_json()

            if self.path == "/start":
                self.start_program(data)
            elif self.path == "/input":
                self.send_input(data)
            elif self.path == "/poll":
                self.poll_program(data)
            elif self.path == "/stop":
                self.stop_program(data)
            else:
                self.send_json({"error": "Unknown endpoint"}, 404)

        except Exception as error:
            self.send_json({"error": str(error)}, 500)

    def start_program(self, data):
        code = data.get("code", "")

        if not isinstance(code, str) or len(code) > 20000:
            self.send_json({"error": "Invalid or oversized code"}, 400)
            return

        if not CLI_FILE.is_file():
            self.send_json({"error": "Velto CLI not found"}, 500)
            return

        session_id = str(uuid.uuid4())
        temp_dir = BASE_DIR / "sessions" / session_id
        temp_dir.mkdir(parents=True, exist_ok=True)

        source_file = temp_dir / "main.vlt"
        source_file.write_text(code, encoding="utf-8")

        process = subprocess.Popen(
            [sys.executable, str(CLI_FILE), str(source_file)],
            cwd=str(VELTO_HOME),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        session = {
            "process": process,
            "output": "",
            "running": True,
            "lock": threading.Lock(),
            "created": time.time()
        }

        with sessions_lock:
            sessions[session_id] = session

        threading.Thread(
            target=self.read_output,
            args=(session_id,),
            daemon=True
        ).start()

        threading.Thread(
            target=self.timeout_program,
            args=(session_id,),
            daemon=True
        ).start()

        self.send_json({
            "session_id": session_id,
            "running": True
        })

    def read_output(self, session_id):
        with sessions_lock:
            session = sessions.get(session_id)

        if not session:
            return

        process = session["process"]

        try:
            while True:
                char = process.stdout.read(1)

                if char == "":
                    break

                with session["lock"]:
                    session["output"] += char

        except Exception:
            pass

        process.wait()

        with session["lock"]:
            session["running"] = False

    def send_input(self, data):
        session_id = data.get("session_id", "")
        value = data.get("input", "")

        if not isinstance(value, str) or len(value) > 10000:
            self.send_json({"error": "Invalid input"}, 400)
            return

        with sessions_lock:
            session = sessions.get(session_id)

        if not session:
            self.send_json({"error": "Session not found"}, 404)
            return

        process = session["process"]

        if process.poll() is not None:
            self.send_json({"error": "Program has finished"}, 400)
            return

        try:
            process.stdin.write(value + "\n")
            process.stdin.flush()
            self.send_json({"success": True})
        except Exception:
            self.send_json({"error": "Could not send input"}, 500)

    def poll_program(self, data):
        session_id = data.get("session_id", "")

        with sessions_lock:
            session = sessions.get(session_id)

        if not session:
            self.send_json({"error": "Session not found"}, 404)
            return

        process = session["process"]

        with session["lock"]:
            output = session["output"]
            running = session["running"]

        self.send_json({
            "output": output,
            "running": running,
            "exit_code": process.poll()
        })

    def stop_program(self, data):
        session_id = data.get("session_id", "")

        with sessions_lock:
            session = sessions.get(session_id)

        if not session:
            self.send_json({"error": "Session not found"}, 404)
            return

        process = session["process"]

        if process.poll() is None:
            process.kill()

        with session["lock"]:
            session["running"] = False

        self.send_json({"success": True})

    def timeout_program(self, session_id):
        time.sleep(30)

        with sessions_lock:
            session = sessions.get(session_id)

        if not session:
            return

        process = session["process"]

        if process.poll() is None:
            process.kill()

            with session["lock"]:
                session["output"] += "\nExecution timed out (30 seconds).\n"
                session["running"] = False


if __name__ == "__main__":
    print("Velto Playground running at http://127.0.0.1:8098")
    server = ThreadingHTTPServer(("127.0.0.1", 8098), PlaygroundHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
