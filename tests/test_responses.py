import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import unittest

from secure_lambda_kit.responses import error, safe_execute, success


class TestSuccessAndError(unittest.TestCase):
    def test_success_default_status_is_200(self):
        result = success({"message": "ok"})
        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(json.loads(result["body"]), {"message": "ok"})

    def test_error_default_status_is_400(self):
        result = error("bad input")
        self.assertEqual(result["statusCode"], 400)
        self.assertEqual(json.loads(result["body"]), {"error": "bad input"})


class TestSafeExecute(unittest.TestCase):
    def test_no_exception_leaves_outcome_unfailed(self):
        with safe_execute() as outcome:
            1 + 1  # no-op, nothing risky happens
        self.assertFalse(outcome.failed)
        self.assertIsNone(outcome.response)

    def test_exception_is_caught_and_outcome_marked_failed(self):
        with safe_execute() as outcome:
            raise RuntimeError("raw internal database error, table=SecretTable")

        self.assertTrue(outcome.failed)
        self.assertEqual(outcome.response["statusCode"], 500)
        # The raw exception message must never leak into the response body.
        self.assertNotIn("SecretTable", outcome.response["body"])

    def test_custom_generic_message_is_used(self):
        with safe_execute(generic_message="try later") as outcome:
            raise ValueError("boom")
        self.assertIn("try later", outcome.response["body"])


if __name__ == "__main__":
    unittest.main()
