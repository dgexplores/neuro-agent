"""Opt-in fictional demonstrations with durable, fail-closed inference budgets."""

from copy import deepcopy
from contextlib import closing
from datetime import datetime, timedelta, timezone
import os
import sqlite3

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import Depends, HTTPException

from .case_store import SQLiteCaseStore, get_case_store

DEMO_TTL_SECONDS = 900
DAILY_LIMIT = 10

# Invented for this portfolio. No real patient, expected diagnosis, or user text.
SAMPLES = {
    "fictional-headache": {
        "id": "fictional-headache",
        "name": "Fictional headache example",
        "summary": "An invented adult with a recurring headache and light sensitivity.",
        "request": {
            "patient_info": {"age": 32, "gender": "female", "medical_history": [],
                             "current_medications": [], "allergies": []},
            "symptoms": [
                {"name": "headache", "severity": "moderate", "duration_days": 2,
                 "description": "Invented recurring headache for a software demonstration"},
                {"name": "light sensitivity", "severity": "mild", "duration_days": 2},
            ],
            "vital_signs": {"bp_systolic": 120, "bp_diastolic": 80, "heart_rate": 72},
            "lab_results": {}, "imaging_studies": [],
            "chief_complaint": "Fictional recurring headache with light sensitivity",
            "history_present_illness": "This invented person has had intermittent headaches for two days. "
                                       "No real person's information is included.",
        },
    },
}


def demo_enabled() -> bool:
    return os.getenv("DEMO_ACCESS_ENABLED", "false").lower() == "true"


def require_demo_enabled() -> None:
    if not demo_enabled():
        raise HTTPException(status_code=404, detail="Synthetic demonstration is disabled")


def demo_config() -> dict:
    if not demo_enabled():
        return {"enabled": False}
    return {"enabled": True, "expires_in": DEMO_TTL_SECONDS,
            "attempts_per_session": 1, "attempts_per_day": DAILY_LIMIT,
            "samples": deepcopy(list(SAMPLES.values()))}


def quota_exceeded() -> HTTPException:
    return HTTPException(status_code=429, detail="Demo inference budget reached. "
                         "Each session allows one attempt; the site allows ten per UTC day.")


class SQLiteDemoBudget:
    def __init__(self, path: str):
        self.path = path
        with closing(sqlite3.connect(path, timeout=10)) as connection, connection:
            connection.execute("CREATE TABLE IF NOT EXISTS demo_budget ("
                               "quota_key TEXT PRIMARY KEY, used INTEGER NOT NULL)")

    def reserve(self, owner_id: str, *, now: datetime | None = None) -> None:
        day = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).date().isoformat()
        # The write lock covers both checks and both writes, including other workers.
        with closing(sqlite3.connect(self.path, timeout=10)) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            used = connection.execute("SELECT used FROM demo_budget WHERE quota_key = ?",
                                      ("day:" + day,)).fetchone()
            session = connection.execute("SELECT used FROM demo_budget WHERE quota_key = ?",
                                         ("session:" + owner_id,)).fetchone()
            if session or (used and used[0] >= DAILY_LIMIT):
                raise quota_exceeded()
            connection.execute("INSERT INTO demo_budget VALUES (?, 1) ON CONFLICT(quota_key) "
                               "DO UPDATE SET used = used + 1", ("day:" + day,))
            connection.execute("INSERT INTO demo_budget VALUES (?, 1)", ("session:" + owner_id,))


class DynamoDBDemoBudget:
    def __init__(self, table_name: str, client=None):
        self.table_name = table_name
        self.client = client if client is not None else boto3.client(
            "dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))

    def reserve(self, owner_id: str, *, now: datetime | None = None) -> None:
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        day = current.date().isoformat()
        expires_at = str(int((current + timedelta(days=2)).timestamp()))
        try:
            self.client.transact_write_items(TransactItems=[
                {"Update": {
                    "TableName": self.table_name,
                    "Key": {"case_id": {"S": "__demo_day__" + day}},
                    "UpdateExpression": "SET expires_at = if_not_exists(expires_at, :expiry) ADD #used :one",
                    "ConditionExpression": "attribute_not_exists(#used) OR #used < :limit",
                    "ExpressionAttributeNames": {"#used": "used"},
                    "ExpressionAttributeValues": {":one": {"N": "1"}, ":limit": {"N": str(DAILY_LIMIT)},
                                                  ":expiry": {"N": expires_at}},
                }},
                {"Put": {
                    "TableName": self.table_name,
                    "Item": {"case_id": {"S": "__demo_session__" + owner_id}, "used": {"N": "1"},
                             "expires_at": {"N": expires_at}},
                    "ConditionExpression": "attribute_not_exists(case_id)",
                }},
            ])
        except ClientError as error:
            reasons = error.response.get("CancellationReasons", [])
            if (error.response["Error"]["Code"] == "TransactionCanceledException"
                    and any(reason.get("Code") == "ConditionalCheckFailed" for reason in reasons)):
                raise quota_exceeded()
            raise


def get_demo_budget(case_store=Depends(get_case_store)):
    try:
        if isinstance(case_store, SQLiteCaseStore):
            return SQLiteDemoBudget(case_store.path)
        return DynamoDBDemoBudget(os.environ["DYNAMODB_TABLE_NAME"])
    except (sqlite3.Error, OSError, KeyError, BotoCoreError, ClientError):
        raise HTTPException(status_code=503, detail="Demo storage unavailable")
