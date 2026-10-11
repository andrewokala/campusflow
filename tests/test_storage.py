import json
import os
import tempfile
import unittest

from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, "tickets.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file_allows_fresh_start(self):
        missing_path = os.path.join(self.temp_dir.name, "nonexistent.json")
        tickets = load_tickets(missing_path)
        self.assertEqual(tickets, [])

    def test_save_and_reload_preserves_tickets(self):
        original_tickets = [
            {
                "id": "T001",
                "title": "Outage",
                "category": "Network",
                "urgency": "high",
                "affected_users": 15,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            }
        ]
        save_tickets(original_tickets, self.test_file)
        loaded = load_tickets(self.test_file)
        self.assertEqual(loaded, original_tickets)

    def test_corrupted_json_raises_clear_error(self):
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json content ...")

        with self.assertRaises(ValueError) as ctx:
            load_tickets(self.test_file)

        self.assertIn("Corrupted or malformed JSON detected", str(ctx.exception))

    def test_create_ticket_after_reload_maintains_unique_ids(self):
        seeded = [
            {"id": "T001", "title": "First", "category": "Network", "urgency": "low", "affected_users": 1, "priority": "low", "status": "open", "assigned_to": None},
            {"id": "T002", "title": "Second", "category": "Hardware", "urgency": "low", "affected_users": 1, "priority": "low", "status": "open", "assigned_to": None},
        ]
        save_tickets(seeded, self.test_file)

        reloaded = load_tickets(self.test_file)
        new_ticket = create_ticket(reloaded, "Third", "Software", "low", 1)
        self.assertEqual(new_ticket["id"], "T003")


if __name__ == "__main__":
    unittest.main()
