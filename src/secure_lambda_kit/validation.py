"""
Reusable input-validation helpers for AWS Lambda APIs.

Generalized from a single hand-written validation function in a real
production Lambda project (lionhall-serverless-lead-intake). Deliberately
plain Python with zero AWS dependencies, so it can be unit tested in
total isolation and reused in any Lambda handler that parses a JSON body.
"""
from __future__ import annotations

import re
from typing import Iterable

PHONE_RE = re.compile(r"^\+?1?[\s.\-]?\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(Exception):
    """Raised when input fails validation. Carries the list of human-readable errors."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def require_fields(body: dict, required: Iterable[str]) -> list[str]:
    """Return an error list for any required fields missing or empty in body."""
    missing = [f for f in required if not body.get(f)]
    if missing:
        return [f"Missing required fields: {missing}"]
    return []


def validate_phone(value: str, field_name: str = "phone") -> list[str]:
    """Return an error if value is present but doesn't look like a real phone number."""
    if value and not PHONE_RE.match(value):
        return [f"Invalid {field_name} format: {value!r}"]
    return []


def validate_email(value: str, field_name: str = "email") -> list[str]:
    """Return an error if value is present but doesn't look like a real email address."""
    if value and not EMAIL_RE.match(value):
        return [f"Invalid {field_name} format: {value!r}"]
    return []


def validate(
    body: dict,
    required: Iterable[str] = (),
    phone_fields: Iterable[str] = (),
    email_fields: Iterable[str] = (),
) -> list[str]:
    """
    Run a full validation pass over a request body.

    Example:
        errors = validate(
            body,
            required=["name", "phone", "source"],
            phone_fields=["phone"],
            email_fields=["email"],
        )
        if errors:
            return error_response("; ".join(errors))
    """
    errors: list[str] = []
    errors += require_fields(body, required)
    for field in phone_fields:
        errors += validate_phone(body.get(field, ""), field)
    for field in email_fields:
        errors += validate_email(body.get(field, ""), field)
    return errors
