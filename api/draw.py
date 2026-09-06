#!/usr/bin/env python3
"""Vercel HTTP adapter for the canonical tarot/plum randomizer.

This file intentionally contains no RNG / deck / hexagram implementation.
It imports the canonical implementation from ../randomizer.py so Web/API
orchestration cannot silently become a third algorithm authority.
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from randomizer import make_result, package  # noqa: E402

API_VERSION = "1"
MAX_BATCH_QUESTIONS = 24


def _one(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _parse_count(value, default=3):
    if value is None or value == "":
        return default
    try:
        count = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("count must be an integer between 1 and 24") from exc
    if not 1 <= count <= 24:
        raise ValueError("count must be between 1 and 24")
    return count


def _parse_counts(value):
    if value is None:
        raise ValueError("counts is required for batch mode")
    if isinstance(value, list):
        raw_values = value
    else:
        raw_values = [part.strip() for part in str(value).split(",") if part.strip()]
    if not raw_values:
        raise ValueError("counts cannot be empty")
    if len(raw_values) > MAX_BATCH_QUESTIONS:
        raise ValueError(f"batch supports at most {MAX_BATCH_QUESTIONS} questions")
    counts = [_parse_count(item) for item in raw_values]
    return counts


def build_payload(params):
    method = str(_one(params.get("method")) or "").lower().strip()
    if method not in {"tarot", "plum", "both", "batch"}:
        raise ValueError("method must be tarot, plum, both, or batch")

    if method == "tarot":
        results = [make_result("tarot", _parse_count(_one(params.get("count"))))]
    elif method == "plum":
        results = [make_result("plum")]
    elif method == "both":
        results = [make_result("both", _parse_count(_one(params.get("count"))))]
    else:
        counts = _parse_counts(params.get("counts"))
        batch_method = str(_one(params.get("batch_method")) or "tarot").lower().strip()
        if batch_method not in {"tarot", "both"}:
            raise ValueError("batch_method must be tarot or both")
        results = [make_result(batch_method, count) for count in counts]

    source_commit = os.environ.get("VERCEL_GIT_COMMIT_SHA") or None
    payload = package(results, source_commit=source_commit)
    payload["transport"] = "vercel-api"
    payload["api_version"] = API_VERSION
    payload["endpoint"] = "/api/draw"
    return payload


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _run(self, params):
        try:
            self._send_json(200, build_payload(params))
        except ValueError as exc:
            self._send_json(
                400,
                {
                    "error": "invalid_request",
                    "message": str(exc),
                    "api_version": API_VERSION,
                },
            )
        except Exception:
            self._send_json(
                500,
                {
                    "error": "runtime_failure",
                    "message": "Canonical randomizer execution failed.",
                    "api_version": API_VERSION,
                },
            )

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query, keep_blank_values=True)
        self._run(query)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self._send_json(
                400,
                {
                    "error": "invalid_json",
                    "message": str(exc),
                    "api_version": API_VERSION,
                },
            )
            return
        self._run(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.end_headers()
