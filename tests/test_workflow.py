import unittest

from campusflow.workflow import (
    find_ticket,
    assign_ticket,
    change_status,
    reopen_ticket,
    get_work_queue,
)


def make_ticket(
    ticket_id="T001",
    priority="high",
    status="open",
    assigned_to=None,
):
    return {
        "id": ticket_id,
        "title": "Campus Wi-Fi is down",
        "category": "Network",
        "urgency": "high",
        "affected_users": 15,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


class TestWorkflow(unittest.TestCase):

    def setUp(self):
        self.tickets = [
            make_ticket()
        ]

    def test_find_ticket(self):
        ticket = find_ticket(self.tickets, "T001")

        self.assertEqual(ticket["id"], "T001")

    def test_find_unknown_ticket(self):
        with self.assertRaises(ValueError):
            find_ticket(self.tickets, "T999")

    def test_assign_ticket(self):
        ticket = assign_ticket(
            self.tickets,
            "T001",
            "Victor",
        )

        self.assertEqual(ticket["assigned_to"], "Victor")

    def test_change_status(self):
        assign_ticket(
            self.tickets,
            "T001",
            "Victor",
        )

        ticket = change_status(
            self.tickets,
            "T001",
            "in_progress",
        )

        self.assertEqual(ticket["status"], "in_progress")

    def test_reopen_ticket(self):
        self.tickets[0]["status"] = "resolved"

        ticket = reopen_ticket(
            self.tickets,
            "T001",
        )

        self.assertEqual(ticket["status"], "open")

    def test_work_queue_sorts_by_priority_and_id(self):
        self.tickets = [
            make_ticket("T010", "critical"),
            make_ticket("T003", "critical"),
            make_ticket("T002", "high"),
            make_ticket("T001", "low"),
            make_ticket("T004", "medium", "resolved"),
        ]

        queue = get_work_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T003", "T010", "T002", "T001"],
        )

    def test_queue_does_not_reorder_original_list(self):
        self.tickets = [
            make_ticket("T002", "low"),
            make_ticket("T001", "high"),
        ]

        original_ids = [
            ticket["id"] for ticket in self.tickets
        ]

        get_work_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in self.tickets],
            original_ids,
        )

    def test_queue_excludes_resolved_tickets(self):
        self.tickets[0]["status"] = "resolved"

        self.assertEqual(
            get_work_queue(self.tickets),
            [],
        )

    def test_work_queue_excludes_in_progress_tickets(self):
        tickets = [
            make_ticket(
                ticket_id="T001",
                priority="high",
                status="open",
            ),
            make_ticket(
                ticket_id="T002",
                priority="critical",
                status="in_progress",
            ),
        ]

        queue = get_work_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T001"],
        )

    def test_work_queue_contains_only_open_tickets(self):
        tickets = [
            make_ticket("T001", "high", "open"),
            make_ticket("T002", "critical", "in_progress"),
            make_ticket("T003", "medium", "resolved"),
            make_ticket("T004", "low", "open"),
        ]

        queue = get_work_queue(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T001", "T004"],
        )

        self.assertTrue(
            all(ticket["status"] == "open" for ticket in queue)
        )


if __name__ == "__main__":
    unittest.main()