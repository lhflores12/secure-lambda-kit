# secure-lambda-kit

Small, dependency-free building blocks for writing secure, well-behaved
AWS Lambda APIs: input validation, safe error responses that never leak
internal details, and least-privilege IAM policy helpers.

This isn't a tutorial project. It's generalized out of a real, deployed
production Lambda function
([lionhall-serverless-lead-intake](https://github.com/lhflores12/lionhall-serverless-lead-intake))
into something any Lambda-based API can reuse, instead of hand-rolling
the same validation/error-handling/IAM boilerplate on every project.

## Why this exists

Three small, boring mistakes show up constantly in hand-rolled Lambda
APIs, and each one has a real cost:

1. **No real input validation** — bad or incomplete data gets written
   straight into the database, where it sits as silent junk someone has
   to clean up later.
2. **Raw exceptions leaking to the caller** — a database failure or any
   unhandled error gets returned as-is to whoever called the API,
   potentially exposing internal details (table names, account
   structure) to the outside world.
3. **Overly broad IAM permissions** — "just attach `AmazonDynamoDBFullAccess`
   to be safe" turns a small, contained bug into an account-wide
   incident if the function is ever compromised.

Each module in this package is a small, tested fix for one of those three.

## Install

```bash
pip install secure-lambda-kit
```

(Not yet published to PyPI — for now, install directly from GitHub:
`pip install git+https://github.com/lhflores12/secure-lambda-kit.git`)

## Usage

```python
import boto3
from botocore.exceptions import ClientError
from secure_lambda_kit import validate, success, error, safe_execute

dynamodb = boto3.resource("dynamodb")

def lambda_handler(event, context):
    table = dynamodb.Table("Leads")
    body = event.get("body") or {}

    errors = validate(
        body,
        required=["name", "phone", "source"],
        phone_fields=["phone"],
        email_fields=["email"],
    )
    if errors:
        return error("; ".join(errors))

    with safe_execute() as outcome:
        table.put_item(Item=body)
    if outcome.failed:
        return outcome.response

    return success({"message": "Saved"})
```

## What's inside

- **`validation.py`** — `validate()` checks required fields plus phone/email
  format, returns a plain list of human-readable error strings. Zero AWS
  dependencies, so it's trivially unit-testable in isolation from Lambda
  itself.
- **`responses.py`** — `success()` / `error()` build consistent API
  Gateway-compatible responses. `safe_execute()` wraps a risky call (a
  database write, an external API call) so any exception is logged in
  full detail server-side, while the caller only ever sees a clean,
  generic message — the raw exception never leaves the function.
- **`iam.py`** — `least_privilege_policy()` generates a minimal IAM
  policy scoped to exactly one resource and exactly the actions you
  specify. `LEAST_PRIVILEGE_CHECKLIST` is a five-question gut-check for
  reviewing any Lambda execution role before you ship it.

## Running tests

```bash
python -m unittest discover tests
```

## License

MIT
