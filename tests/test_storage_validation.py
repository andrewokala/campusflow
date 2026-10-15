
"""Tests for safe ticket storage and validation."""

import json
import os
import tempfile
import unittest

from campusflow.storage import load_tickets, save_tickets


def make_ticket(ticket_id="T001"):
    return {
        "id": ticket_id,
        "title": "Network issue",
        "category": "network",
        "urgency": "high",
        "affected_users": 12,
        "priority": "critical",
        "status": "open",
        "assigned_to": None,
    }


class TestStorageValidation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.temp_dir.name, "tickets.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_rejects_duplicate_ticket_ids(self):
        with open(self.filepath, "w", encoding="utf-8") as file:
            json.dump(
                [make_ticket("T001"), make_ticket("T001")],
                file,
            )

        with self.assertRaisesRegex(ValueError, "Duplicate ticket ID"):
            load_tickets(self.filepath)

    def test_load_rejects_record_missing_required_fields(self):
        with open(self.filepath, "w", encoding="utf-8") as file:
            json.dump([{"id": "T001"}], file)

        with self.assertRaisesRegex(ValueError, "missing required fields"):
            load_tickets(self.filepath)

    def test_load_rejects_non_list_json(self):
        with open(self.filepath, "w", encoding="utf-8") as file:
            json.dump({"id": "T001"}, file)

        with self.assertRaisesRegex(ValueError, "expected a list"):
            load_tickets(self.filepath)

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_tickets(self.filepath), [])

    def test_save_rejects_duplicate_ticket_ids(self):
        with self.assertRaisesRegex(ValueError, "Duplicate ticket ID"):
            save_tickets(
                [make_ticket("T001"), make_ticket("T001")],
                self.filepath,
            )

        self.assertFalse(os.path.exists(self.filepath))


if __name__ == "__main__":
    unittest.main()
