import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import unittest

from secure_lambda_kit.validation import (
    require_fields,
    validate,
    validate_email,
    validate_phone,
)


class TestRequireFields(unittest.TestCase):
    def test_no_missing_fields_returns_empty(self):
        self.assertEqual(require_fields({"name": "Leo"}, ["name"]), [])

    def test_missing_field_is_reported(self):
        errors = require_fields({}, ["name", "phone"])
        self.assertEqual(len(errors), 1)
        self.assertIn("name", errors[0])
        self.assertIn("phone", errors[0])


class TestValidatePhone(unittest.TestCase):
    def test_accepts_common_formats(self):
        for phone in ["5551234567", "555-123-4567", "(555) 123-4567", "+1 555 123 4567"]:
            self.assertEqual(validate_phone(phone), [], f"should accept {phone!r}")

    def test_rejects_garbage(self):
        self.assertTrue(validate_phone("abc"))

    def test_empty_value_is_not_an_error(self):
        # Optional fields: emptiness is require_fields' job, not format validation's.
        self.assertEqual(validate_phone(""), [])


class TestValidateEmail(unittest.TestCase):
    def test_accepts_valid_email(self):
        self.assertEqual(validate_email("a@b.com"), [])

    def test_rejects_invalid_email(self):
        self.assertTrue(validate_email("not-an-email"))


class TestValidate(unittest.TestCase):
    def test_full_pass_with_valid_data(self):
        body = {"name": "Leo", "phone": "555-123-4567", "source": "web", "email": "a@b.com"}
        errors = validate(
            body,
            required=["name", "phone", "source"],
            phone_fields=["phone"],
            email_fields=["email"],
        )
        self.assertEqual(errors, [])

    def test_collects_multiple_errors(self):
        body = {"phone": "abc"}
        errors = validate(
            body,
            required=["name", "phone"],
            phone_fields=["phone"],
        )
        # Missing-fields error plus bad-phone-format error.
        self.assertEqual(len(errors), 2)


if __name__ == "__main__":
    unittest.main()
