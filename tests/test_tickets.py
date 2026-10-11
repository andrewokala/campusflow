import unittest
from campusflow.tickets import calculate_priority, create_ticket, get_ticket



class TicketTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []

    def test_critical_priority(self):
        self.assertEqual(calculate_priority("high", 12), "critical")

    def test_high_priority(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_medium_priority(self):
        self.assertEqual(calculate_priority("low", 4), "medium")

    def test_low_priority(self):
        self.assertEqual(calculate_priority("low", 1), "low")

    def test_creation_defaults_and_normalization(self):
        ticket = create_ticket(self.tickets, "  Wi-Fi down  ", " NETWORK ", " HIGH ", 12)
        self.assertEqual((ticket["id"], ticket["category"], ticket["status"], ticket["assigned_to"]), ("T001", "Network", "open", None))
        self.assertEqual(ticket["title"], "Wi-Fi down")
        self.assertEqual(ticket["priority"], "critical")

    def test_zero_users_does_not_mutate(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "Issue", "Other", "low", 0)
        self.assertEqual(self.tickets, [])

    def test_blank_title_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "  ", "Other", "low", 1)
        self.assertEqual(self.tickets, [])

    def test_invalid_category_rejected(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "Issue", "Finance", "low", 1)

    def test_boolean_is_not_valid_count(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "Issue", "Other", "low", True)

    def test_sequential_ids_after_reload_shape(self):
        self.tickets.append({"id": "T009"})
        self.assertEqual(create_ticket(self.tickets, "Issue", "Other", "low", 1)["id"], "T010")

    def test_lookup_unknown_id(self):
        with self.assertRaises(KeyError):
            get_ticket(self.tickets, "T999")

    def test_lookup_case_insensitive(self):
        create_ticket(self.tickets, "Issue", "Other", "low", 1)
        self.assertEqual(get_ticket(self.tickets, " t001 ")["id"], "T001")


if __name__ == "__main__":
    unittest.main()