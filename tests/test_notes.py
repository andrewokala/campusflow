
import unittest

from campusflow.notes import add_note, get_notes


class TestTicketNotes(unittest.TestCase):
    def setUp(self):
        self.tickets = [{
            "id": "T001",
            "title": "Campus Wi-Fi outage",
            "category": "Network",
            "urgency": "high",
            "affected_users": 20,
            "priority": "critical",
            "status": "open",
            "assigned_to": "Victor",
        }]

    def test_add_note(self):
        note = add_note(self.tickets, "T001", "Victor", "Investigating.")
        self.assertEqual(note["author"], "Victor")
        self.assertEqual(note["content"], "Investigating.")
        self.assertIn("created_at", note)
        self.assertEqual(len(get_notes(self.tickets, "T001")), 1)

    def test_reject_blank_note(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "Victor", "   ")
        self.assertNotIn("notes", self.tickets[0])

    def test_reject_blank_author(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "  ", "Checking.")

    def test_reject_note_on_resolved_ticket(self):
        self.tickets[0]["status"] = "resolved"
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "Victor", "Checking.")
        self.assertNotIn("notes", self.tickets[0])

    def test_unknown_ticket(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T999", "Victor", "Checking.")


if __name__ == "__main__":
    unittest.main()
