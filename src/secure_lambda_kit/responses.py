"""
Standardized, safe response helpers for AWS Lambda functions behind
API Gateway.

Core principle: never let a raw internal exception reach the caller.
Whoever called the API gets a clean, generic message; the real error
still gets logged (CloudWatch, if running in Lambda) so the developer
can debug it. This is the generalized version of the try/except pattern
used in lionhall-serverless-lead-intake's lambda_function.py.
"""
from __future__ import annotations

import json
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def response(status_code: int, payload: dict) -> dict:
    """Build a raw API Gateway-compatible Lambda response."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload),
    }


def success(payload: dict, status_code: int = 200) -> dict:
    return response(status_code, payload)


def error(message: str, status_code: int = 400) -> dict:
    return response(status_code, {"error": message})


class _Outcome:
    """Carries the result of a safe_execute block back out to the caller."""

    def __init__(self) -> None:
        self.failed = False
        self.response: dict | None = None


@contextmanager
def safe_execute(generic_message: str = "Something went wrong, please try again."):
    """
    Wrap a risky call (a database write, an external API call) so that
    any exception is logged in full detail internally, while the caller
    of the Lambda function only ever sees a clean, generic 500 — never
    the raw exception, which could leak internal details like table
    names or account structure.

    Usage:
        with safe_execute() as outcome:
            table.put_item(Item=item)
        if outcome.failed:
            return outcome.response
        return success({"message": "Saved"})
    """
    outcome = _Outcome()
    try:
        yield outcome
    except Exception:  # noqa: BLE001 - intentionally broad, see docstring
        logger.exception("safe_execute caught an exception")
        outcome.failed = True
        outcome.response = error(generic_message, status_code=500)
