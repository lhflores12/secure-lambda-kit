"""
Least-privilege IAM policy helpers for AWS Lambda functions.

This module makes no AWS calls at all. It's a small generator plus a
checklist that makes it fast, and hard to get wrong, to write a tightly
scoped IAM policy for a Lambda function instead of reaching for a broad
managed policy "to be safe."

Principle: if this function is ever compromised, the damage should be
capped at exactly the one resource it actually needs, nothing more.
"""
from __future__ import annotations


def least_privilege_policy(resource_arn: str, actions: list[str] | None = None) -> dict:
    """
    Build a minimal IAM policy document granting only the given actions
    on a single resource ARN (and, for DynamoDB, its indexes) — nothing
    broader.

    Example:
        policy = least_privilege_policy(
            "arn:aws:dynamodb:us-east-1:123456789012:table/Leads",
            actions=["dynamodb:PutItem"],
        )
    """
    actions = actions or ["dynamodb:PutItem", "dynamodb:GetItem"]
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": actions,
                "Resource": [resource_arn, f"{resource_arn}/index/*"],
            }
        ],
    }


LEAST_PRIVILEGE_CHECKLIST = [
    "Does this function's role grant access to exactly one resource (one table, one bucket), not a wildcard '*'?",
    "Are the listed actions the minimum the function actually calls (e.g. 'dynamodb:PutItem', not 'dynamodb:*')?",
    "Does the role avoid any IAM, admin, or cross-account permissions it doesn't strictly need?",
    "Is CloudWatch Logs access the only broad permission granted (for debugging), with everything else scoped to one resource?",
    "If this function were fully compromised, is the worst-case blast radius limited to one resource and some log noise, not the whole AWS account?",
]
