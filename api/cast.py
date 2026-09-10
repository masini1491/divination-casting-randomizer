#!/usr/bin/env python3
"""Thin Vercel HTTP adapter over the canonical divination casting runtime."""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import randomizer  # noqa: E402

ALLOWED_METHODS = {"tarot", "plum", "liuyao"}
ALLOWED_KEYS = {"method", "count", "repeat"}
MAX_BODY_BYTES = 1024
MAX_REPEAT = 20


class RequestValidationError(ValueError):
    pass


def _require_int(value: Any, *, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RequestValidationError(f"{name} must be an integer")
    if value < minimum or value > maximum:
        raise RequestValidationError(f"{name} must be between {minimum} and {maximum}")
    return value


def validate_cast_request(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise RequestValidationError("request body must be a JSON object")

    unknown = sorted(set(data) - ALLOWED_KEYS)
    if unknown:
        raise RequestValidationError(f"unsupported field(s): {', '.join(unknown)}")

    method = data.get("method")
    if method not in ALLOWED_METHODS:
        raise RequestValidationError("method must be one of: tarot, plum, liuyao")

    count = _require_int(data.get("count", 3), name="count", minimum=1, maximum=24)
    repeat = _require_int(data.get("repeat", 1), name="repeat", minimum=1, maximum=MAX_REPEAT)

    return {"method": method, "count": count, "repeat": repeat}


def execute_cast(params: dict[str, Any]) -> dict[str, Any]:
    source_commit = os.environ.get("VERCEL_GIT_COMMIT_SHA") or "unknown"
    payload = randomizer.generate_payload(
        params["method"],
        count=params["count"],
        repeat=params["repeat"],
        source_commit=source_commit,
    )
    return randomizer.compact_ai_payload(payload)


class handler(BaseHTTPRequestHandler):
    server_version = "DivinationCastingAPI/1"

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)

    def _error(self, status: int, code: str, message: str) -> None:
        self._send_json(status, {"error": {"code": code, "message": message}})

    def do_GET(self) -> None:  # noqa: N802
        self.send_response(405)
        self.send_header("Allow", "POST, OPTIONS")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Allow", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        raw_length = self.headers.get("Content-Length")
        try:
            content_length = int(raw_length) if raw_length is not None else 0
        except ValueError:
            self._error(400, "invalid_request", "invalid Content-Length")
            return

        if content_length <= 0:
            self._error(400, "invalid_request", "request body is required")
            return
        if content_length > MAX_BODY_BYTES:
            self._error(413, "payload_too_large", f"request body must be <= {MAX_BODY_BYTES} bytes")
            return

        try:
            raw = self.rfile.read(content_length)
            data = json.loads(raw.decode("utf-8"))
            params = validate_cast_request(data)
            result = execute_cast(params)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._error(400, "invalid_json", "request body must be valid UTF-8 JSON")
            return
        except RequestValidationError as exc:
            self._error(400, "invalid_request", str(exc))
            return
        except ValueError as exc:
            self._error(400, "invalid_request", str(exc))
            return
        except Exception:
            self._error(500, "internal_error", "casting failed")
            return

        self._send_json(200, result)

    def log_message(self, format: str, *args: Any) -> None:
        # Avoid logging request bodies or divination context. Vercel still records
        # ordinary request metadata at the platform layer.
        return
