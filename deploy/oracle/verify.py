#!/usr/bin/env python3
"""Verify deployed routing/authentication without issuing tokens or model calls."""

import argparse
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch(url: str, *, data: dict | None = None) -> tuple[int, str, bytes]:
    request = Request(url, data=None if data is None else json.dumps(data).encode(),
                      headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=15) as response:
            return response.status, response.headers.get("Content-Type", ""), response.read()
    except HTTPError as error:
        return error.code, error.headers.get("Content-Type", ""), error.read()


def verify(hostname: str, *, timeout: int = 300) -> None:
    deadline = time.monotonic() + timeout
    while True:
        try:
            status, _, payload = fetch("http://127.0.0.1:8081/health")
            assert status == 200 and json.loads(payload)["services"]["gemini"] == "not_checked"
            break
        except (OSError, URLError, AssertionError, ValueError, KeyError):
            if time.monotonic() >= deadline:
                raise RuntimeError("Backend did not become healthy") from None
            time.sleep(3)
    base = "https://" + hostname
    while True:
        try:
            assert fetch(base + "/health")[0] == 200
            break
        except (OSError, URLError, AssertionError):
            if time.monotonic() >= deadline:
                raise RuntimeError("Public HTTPS route did not become healthy") from None
            time.sleep(3)
    for path in ("/", "/demo", "/history"):
        status, content_type, body = fetch(base + path)
        assert status == 200 and "text/html" in content_type and b'id="root"' in body, path
    assert fetch(base + "/assets/nonexistent-deployment-probe.js")[0] == 404
    assert fetch(base + "/api/v1/cases/unauthenticated-probe")[0] == 401
    payload = {"patient_info": {"age": 30, "gender": "other"},
               "symptoms": [{"name": "fictional", "severity": "mild", "duration_days": 1}],
               "chief_complaint": "Synthetic routing probe", "history_present_illness": "Fictional input"}
    assert fetch(base + "/api/v1/diagnosis", data=payload)[0] == 401
    status, _, payload = fetch(base + "/api/v1/demo/config")
    assert status == 200 and json.loads(payload)["enabled"] is True
    print("PASS: backend health, HTTPS SPA/API routes, missing asset 404, and unauthenticated API 401.")
    print("No demo session or model inference was created; live model validation is separate.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hostname", required=True)
    parser.add_argument("--timeout", type=int, default=300)
    arguments = parser.parse_args()
    verify(arguments.hostname, timeout=arguments.timeout)
