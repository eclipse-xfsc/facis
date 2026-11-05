#!/usr/bin/env python3
"""Local HTTP adapter for the observable Thin Slice 4 workflow."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from workflow import degraded_response, parse_request_body, run_workflow
from observability import tracing_status


HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "8080"))
ENDPOINT = "/api/airbus-challenge/thin-slice-mvp/run"


class ChallengeHandler(BaseHTTPRequestHandler):
    def _write_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != ENDPOINT:
            self._write_json(404, {"error": "not_found", "expected_path": ENDPOINT})
            return

        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        raw = self.rfile.read(max(length, 0)) if length else b""
        payload, errors = parse_request_body(raw)

        try:
            response = run_workflow(payload, request_errors=errors)
        except Exception as exc:  # Last-resort contract protection for the demo.
            response = degraded_response(
                payload,
                errors=errors + [f"Workflow degraded after {type(exc).__name__}"],
            )
        self._write_json(200, response)

    def log_message(self, *_args: object) -> None:
        return


if __name__ == "__main__":
    print(f"Thin Slice MVP listening on http://localhost:{PORT}{ENDPOINT}")
    status = tracing_status()
    if status["active"]:
        print(f"Phoenix tracing enabled: {status['endpoint']}")
    elif status["enabled"]:
        print(f"Phoenix tracing unavailable: {status['error']}")
    ThreadingHTTPServer((HOST, PORT), ChallengeHandler).serve_forever()
