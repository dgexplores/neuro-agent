"""Oracle configuration boundaries; no Docker, SSH, keys, or provider calls."""

import json
from pathlib import Path
import stat

import pytest

from deploy.oracle.prepare import ROOT, prepare
from deploy.oracle import verify

SHA = "a" * 40


def test_private_persistent_config_and_isolated_routes(tmp_path):
    key = tmp_path / "test-key"
    key.write_text("AQ.synthetic-key-for-tests-only-123456789")
    state = tmp_path / "state"
    compose = prepare(state, "neuro.example.test", SHA, key)
    saved_secret = json.loads((state / "credentials.json").read_text())
    assert len(saved_secret["jwt_secret_key"]) >= 32
    backend = compose["services"]["backend"]
    assert backend["ports"] == ["127.0.0.1:8081:8000"]
    assert backend["networks"]["edge"]["aliases"] == ["neuro-api"]
    assert compose["networks"]["edge"] == {"external": True, "name": "portfolio-edge"}
    assert backend["mem_limit"] == "512m"
    assert backend["read_only"] is True
    assert backend["environment"]["MODEL_PROVIDER"] == "gemini"
    assert backend["environment"]["DEMO_ACCESS_ENABLED"] == "true"
    assert backend["environment"]["CASE_DB_PATH"] == "/data/cases.sqlite3"
    assert backend["environment"]["ALLOWED_ORIGINS"] == "https://neuro.example.test"
    assert compose["volumes"]["cases"]["name"] == "neuro-cases"
    assert "AQ.synthetic" not in (state / "compose.json").read_text()
    for name in ("credentials.json", "agents.env", "compose.json", "neuro.caddy"):
        assert stat.S_IMODE((state / name).stat().st_mode) == 0o600
    assert stat.S_IMODE(state.stat().st_mode) == 0o700
    site = (state / "neuro.caddy").read_text()
    assert "reverse_proxy neuro-api:8000" in site
    assert "@assets path /assets/* *.js *.css" in site
    assert "try_files {path} /index.html" in site
    rerendered = prepare(state, "neuro.example.test", "b" * 40)
    assert json.loads((state / "credentials.json").read_text()) == saved_secret
    assert rerendered["services"]["backend"]["image"] == "neuro-api:" + "b" * 40


@pytest.mark.parametrize("hostname,revision", [("https://example.test", SHA), ("bad\nname", SHA),
                                               ("example.test", "main"), ("-bad.example", SHA)])
def test_rejects_shell_and_hostname_injection_before_writing(tmp_path, hostname, revision):
    with pytest.raises(ValueError):
        prepare(tmp_path / "state", hostname, revision)
    assert not (tmp_path / "state").exists()


def test_rejects_state_inside_git_and_requires_private_key_file(tmp_path):
    with pytest.raises(ValueError, match="outside"):
        prepare(ROOT / "data" / "forbidden-state", "example.test", SHA)
    with pytest.raises(ValueError, match="private local file"):
        prepare(tmp_path / "state", "example.test", SHA)
    assert not (tmp_path / "state" / "agents.env").exists()


def test_verification_checks_real_routing_but_never_starts_a_session_or_model(monkeypatch):
    calls = []
    def fake_fetch(url, *, data=None):
        calls.append((url, data))
        if url.endswith("/health"):
            return 200, "application/json", b'{"services":{"gemini":"not_checked"}}'
        if "/assets/" in url:
            return 404, "text/plain", b"missing"
        if url.endswith("/api/v1/demo/config"):
            return 200, "application/json", b'{"enabled":true}'
        if "/api/" in url:
            return 401, "application/json", b'{"detail":"Not authenticated"}'
        return 200, "text/html", b'<html><div id="root"></div></html>'
    monkeypatch.setattr(verify, "fetch", fake_fetch)
    verify.verify("example.test", timeout=1)
    assert not any("/demo/session" in url or "/demo/diagnosis" in url for url, _ in calls)
    assert [url for url, payload in calls if payload] == ["https://example.test/api/v1/diagnosis"]
