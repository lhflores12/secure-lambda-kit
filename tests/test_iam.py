import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import unittest

from secure_lambda_kit.iam import LEAST_PRIVILEGE_CHECKLIST, least_privilege_policy


class TestLeastPrivilegePolicy(unittest.TestCase):
    def test_default_actions_are_minimal(self):
        policy = least_privilege_policy("arn:aws:dynamodb:us-east-1:123:table/Leads")
        statement = policy["Statement"][0]
        self.assertEqual(statement["Effect"], "Allow")
        self.assertIn("dynamodb:PutItem", statement["Action"])
        self.assertNotIn("dynamodb:*", statement["Action"])

    def test_resource_is_scoped_to_one_table(self):
        arn = "arn:aws:dynamodb:us-east-1:123:table/Leads"
        policy = least_privilege_policy(arn)
        statement = policy["Statement"][0]
        self.assertIn(arn, statement["Resource"])
        self.assertNotIn("*", statement["Resource"][0])

    def test_custom_actions_are_respected(self):
        policy = least_privilege_policy(
            "arn:aws:dynamodb:us-east-1:123:table/Leads",
            actions=["dynamodb:Query"],
        )
        self.assertEqual(policy["Statement"][0]["Action"], ["dynamodb:Query"])


class TestChecklist(unittest.TestCase):
    def test_checklist_is_nonempty_and_all_strings(self):
        self.assertTrue(len(LEAST_PRIVILEGE_CHECKLIST) >= 5)
        self.assertTrue(all(isinstance(item, str) for item in LEAST_PRIVILEGE_CHECKLIST))


if __name__ == "__main__":
    unittest.main()
