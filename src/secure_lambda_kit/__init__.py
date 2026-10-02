"""
secure-lambda-kit

Small, dependency-free building blocks for writing secure, well-behaved
AWS Lambda APIs: input validation, safe error responses that never leak
internals, and least-privilege IAM policy helpers.

Generalized from a real production project
(lionhall-serverless-lead-intake) rather than written as a tutorial from
scratch.
"""
from .validation import ValidationError, validate, require_fields, validate_phone, validate_email
from .responses import success, error, response, safe_execute
from .iam import least_privilege_policy, LEAST_PRIVILEGE_CHECKLIST

__all__ = [
    "ValidationError",
    "validate",
    "require_fields",
    "validate_phone",
    "validate_email",
    "success",
    "error",
    "response",
    "safe_execute",
    "least_privilege_policy",
    "LEAST_PRIVILEGE_CHECKLIST",
]

__version__ = "0.1.0"
