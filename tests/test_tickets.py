import unittest

from campusflow.tickets import (
    calculate_priority,
    create_ticket,
    generate_ticket_id,
)


class TestTickets(unittest.TestCase):

    def test_priority_critical_boundary(self):
        # High urgency + 12 affected users -> critical
        self.assertEqual(calculate_priority("high", 12), "critical")
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_priority_high_boundary(self):
        # High urgency + 2 affected users -> high
        self.assertEqual(calculate_priority("high", 2), "high")
        # Low urgency + 10 affected users -> high
        self.assertEqual(calculate_priority("low", 10), "high")

    def test_priority_medium_boundary(self):
        # Low urgency + 4 affected users -> medium
        self.assertEqual(calculate_priority("low", 4), "medium")
        # Medium urgency + 1 affected user -> medium
        self.assertEqual(calculate_priority("medium", 1), "medium")
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_priority_low_boundary(self):
        # Low urgency + 1 affected user -> low
        self.assertEqual(calculate_priority("low", 1), "low")

    def test_reject_zero_or_negative_affected_users(self):
        with self.assertRaises(ValueError):
            calculate_priority("high", 0)
        with self.assertRaises(ValueError):
            calculate_priority("high", -5)

    def test_create_valid_ticket(self):
        tickets = []
        ticket = create_ticket(
            tickets,
            title="Wi-Fi outage in Lab 2",
            category="Network",
            urgency="high",
            affected_users=15,
        )
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])
        self.assertEqual(len(tickets), 1)

    def test_reject_blank_title(self):
        tickets = []
        with self.assertRaises(ValueError):
            create_ticket(tickets, "   ", "Network", "high", 5)

    def test_reject_invalid_category(self):
        tickets = []
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Broken chair", "Furniture", "low", 1)

    def test_reject_invalid_urgency(self):
        tickets = []
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Server down", "Network", "emergency", 5)

    def test_case_normalization(self):
        tickets = []
        ticket = create_ticket(
            tickets,
            title="Printer issue",
            category="hardware",
            urgency="HIGH",
            affected_users=2,
        )
        self.assertEqual(ticket["category"], "Hardware")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["priority"], "high")

    def test_auto_incrementing_ids(self):
        tickets = []
        t1 = create_ticket(tickets, "Issue 1", "Software", "low", 1)
        t2 = create_ticket(tickets, "Issue 2", "Software", "low", 1)
        self.assertEqual(t1["id"], "T001")
        self.assertEqual(t2["id"], "T002")


if __name__ == "__main__":
    unittest.main()
