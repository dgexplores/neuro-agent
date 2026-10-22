"""Local demonstration case storage. Use synthetic inputs, not patient records."""

import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException


class SQLiteCaseStore:
    """Store completed responses and enforce owner scope in every lookup.

    A new connection per operation supports FastAPI worker threads. SQLite is
    suitable for a local demo; it is not a shared database for Lambda replicas.
    """

    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path, timeout=10)) as connection, connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS cases ("
                "case_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, "
                "response_json TEXT NOT NULL)"
            )

    def save(self, owner_id: str, response: dict[str, Any]) -> None:
        if not owner_id:
            raise ValueError("An owner is required")
        payload = json.dumps(response, allow_nan=False)
        with closing(sqlite3.connect(self.path, timeout=10)) as connection, connection:
            # INSERT rather than REPLACE prevents another owner overwriting a case.
            connection.execute(
                "INSERT INTO cases (case_id, owner_id, response_json) VALUES (?, ?, ?)",
                (response["case_id"], owner_id, payload),
            )

    def get(self, owner_id: str, case_id: str) -> dict[str, Any] | None:
        with closing(sqlite3.connect(self.path, timeout=10)) as connection, connection:
            row = connection.execute(
                "SELECT response_json FROM cases WHERE case_id = ? AND owner_id = ?",
                (case_id, owner_id),
            ).fetchone()
        return json.loads(row[0]) if row else None


class DynamoDBCaseStore:
    """Shared cloud storage using the original case_id partition key."""

    def __init__(self, table_name: str, table=None):
        if not table_name:
            raise ValueError("DYNAMODB_TABLE_NAME is required")
        self.table = table if table is not None else boto3.resource(
            "dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1")
        ).Table(table_name)

    def save(self, owner_id: str, response: dict[str, Any]) -> None:
        if not owner_id:
            raise ValueError("An owner is required")
        self.table.put_item(
            Item={"case_id": response["case_id"], "owner_id": owner_id,
                  "response_json": json.dumps(response, allow_nan=False)},
            ConditionExpression="attribute_not_exists(case_id)",
        )

    def get(self, owner_id: str, case_id: str) -> dict[str, Any] | None:
        item = self.table.get_item(Key={"case_id": case_id}, ConsistentRead=True).get("Item")
        if item is None or item.get("owner_id") != owner_id:
            return None
        return json.loads(item["response_json"])


def get_case_store() -> SQLiteCaseStore | DynamoDBCaseStore:
    """FastAPI dependency: override for tests or configure a durable local path."""
    try:
        backend = os.getenv("CASE_STORE_BACKEND", "sqlite")
        if backend == "dynamodb":
            return DynamoDBCaseStore(os.getenv("DYNAMODB_TABLE_NAME", ""))
        if backend != "sqlite":
            raise ValueError("Unsupported case store backend")
        return SQLiteCaseStore(os.getenv("CASE_DB_PATH", "data/cases.sqlite3"))
    except (OSError, sqlite3.Error, ValueError, BotoCoreError, ClientError):
        raise HTTPException(status_code=503, detail="Case storage unavailable")
