#!/usr/bin/env python3
"""Render private configuration for an explicitly selected Oracle/Gemini demo."""

import argparse
import json
import os
from pathlib import Path
import re
import secrets

ROOT = Path(__file__).resolve().parents[2]


def private_write(path: Path, contents: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with os.fdopen(os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w") as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(contents)
    temporary.replace(path)


def prepare(state_dir: Path, hostname: str, revision: str, key_file: Path | None = None,
            *, demo_enabled: bool = True) -> dict:
    state_dir = state_dir.resolve()
    if state_dir == ROOT or ROOT in state_dir.parents:
        raise ValueError("State must be outside the source repository")
    if not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?", hostname):
        raise ValueError("A bare public hostname is required")
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("A complete Git commit SHA is required")
    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    state_dir.chmod(0o700)
    env_path = state_dir / "agents.env"
    previous = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            key, separator, value = line.partition("=")
            if separator:
                previous[key] = value
    credentials_path = state_dir / "credentials.json"
    credentials = json.loads(credentials_path.read_text()) if credentials_path.exists() else {
        "jwt_secret_key": previous.get("JWT_SECRET_KEY") or secrets.token_urlsafe(48),
    }
    signing_secret = credentials.get("jwt_secret_key", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{32,}", signing_secret):
        raise ValueError("Stored JWT secret is invalid")
    api_key = key_file.read_text().strip() if key_file else previous.get("GEMINI_API_KEY", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{20,300}", api_key):
        raise ValueError("Save a valid single-line Gemini key in a private local file first")
    private_write(credentials_path, json.dumps(credentials, indent=2) + "\n")
    private_write(env_path, f"JWT_SECRET_KEY={signing_secret}\nGEMINI_API_KEY={api_key}\n")
    compose = {
        "name": "neuro",
        "services": {
            "backend": {
                "image": "neuro-api:" + revision,
                "build": {"context": str(ROOT), "dockerfile": "deploy/oracle/Dockerfile"},
                "env_file": [str(env_path)],
                "environment": {
                    "MODEL_PROVIDER": "gemini", "GEMINI_MODEL": "gemini-3.5-flash-lite",
                    "ENV": "production", "DEMO_ACCESS_ENABLED": str(demo_enabled).lower(),
                    "CASE_STORE_BACKEND": "sqlite", "CASE_DB_PATH": "/data/cases.sqlite3",
                    "ALLOWED_ORIGINS": "https://" + hostname, "AWS_EC2_METADATA_DISABLED": "true",
                },
                "ports": ["127.0.0.1:8081:8000"],
                "volumes": ["cases:/data"],
                "networks": {"edge": {"aliases": ["neuro-api"]}},
                "restart": "unless-stopped", "mem_limit": "512m", "cpus": "0.50",
                "read_only": True, "tmpfs": ["/tmp:size=64m,mode=1777"],
                "cap_drop": ["ALL"], "security_opt": ["no-new-privileges:true"],
                "pids_limit": 128,
                "logging": {"driver": "json-file", "options": {"max-size": "5m", "max-file": "2"}},
            },
        },
        "volumes": {"cases": {"name": "neuro-cases"}},
        "networks": {"edge": {"external": True, "name": "portfolio-edge"}},
    }
    private_write(state_dir / "compose.json", json.dumps(compose, indent=2) + "\n")
    site = f"""{hostname} {{
    encode zstd gzip
    @api path /api /api/* /health /openapi.json /docs /docs/* /redoc
    handle @api {{
        reverse_proxy neuro-api:8000
    }}
    @assets path /assets/* *.js *.css *.map *.png *.jpg *.jpeg *.svg *.ico *.woff *.woff2
    handle @assets {{
        root * /srv/portfolio/neuro
        file_server
    }}
    handle {{
        root * /srv/portfolio/neuro
        try_files {{path}} /index.html
        file_server
    }}
}}
"""
    private_write(state_dir / "neuro.caddy", site)
    return compose


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--hostname", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--gemini-key-file", type=Path)
    parser.add_argument("--disable-demo", action="store_true")
    args = parser.parse_args()
    prepare(args.state_dir, args.hostname, args.revision, args.gemini_key_file,
            demo_enabled=not args.disable_demo)
    print("Private Oracle demo configuration prepared; no resources or model calls were created.")
