import unittest

from campusflow.search import search_tickets


class TestSearchTickets(unittest.TestCase):

    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Campus Wi-Fi outage",
                "category": "Network",
                "urgency": "high",
                "affected_users": 20,
                "priority": "critical",
                "status": "open",
                "assigned_to": "Victor",
            },
            {
                "id": "T002",
                "title": "Broken laboratory computer",
                "category": "Hardware",
                "urgency": "medium",
                "affected_users": 2,
                "priority": "medium",
                "status": "in_progress",
                "assigned_to": "Andrew",
            },
        ]

    def test_search_by_priority(self):
        results = search_tickets(self.tickets, priority="critical")
        self.assertEqual([ticket["id"] for ticket in results], ["T001"])

    def test_filters_combine_with_and(self):
        results = search_tickets(
            self.tickets,
            category="Network",
            status="open",
        )
        self.assertEqual([ticket["id"] for ticket in results], ["T001"])

    def test_non_matching_filters_return_empty_list(self):
        results = search_tickets(
            self.tickets,
            category="Network",
            status="resolved",
        )
        self.assertEqual(results, [])

    def test_search_is_case_insensitive(self):
        results = search_tickets(self.tickets, title="WI-FI")
        self.assertEqual([ticket["id"] for ticket in results], ["T001"])


if __name__ == "__main__":
    unittest.main()