
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
            self.tickets, "T001", "Victor"
        )
        self.assertEqual(ticket["assigned_to"], "Victor")

    def test_reject_empty_staff_name(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "   ")

        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_reject_assignment_to_resolved_ticket(self):
        self.tickets[0]["status"] = "resolved"

        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Victor")

        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_reject_unassigned_ticket_start(self):
        with self.assertRaises(ValueError):
            change_status(
                self.tickets, "T001", "in_progress"
            )

        self.assertEqual(self.tickets[0]["status"], "open")

    def test_assigned_ticket_can_progress(self):
        self.tickets[0]["assigned_to"] = "Victor"

        ticket = change_status(
            self.tickets, "T001", "in_progress"
        )

        self.assertEqual(ticket["status"], "in_progress")

    def test_ticket_can_be_resolved(self):
        self.tickets[0]["assigned_to"] = "Victor"
        self.tickets[0]["status"] = "in_progress"

        ticket = change_status(
            self.tickets, "T001", "resolved"
        )

        self.assertEqual(ticket["status"], "resolved")

    def test_cannot_resolve_open_ticket(self):
        self.tickets[0]["assigned_to"] = "Victor"

        with self.assertRaises(ValueError):
            change_status(
                self.tickets, "T001", "resolved"
            )

        self.assertEqual(self.tickets[0]["status"], "open")

    def test_reject_invalid_status(self):
        with self.assertRaises(ValueError):
            change_status(
                self.tickets, "T001", "cancelled"
            )

        self.assertEqual(self.tickets[0]["status"], "open")

    def test_reopen_resolved_ticket(self):
        self.tickets[0]["status"] = "resolved"

        ticket = reopen_ticket(self.tickets, "T001")

        self.assertEqual(ticket["status"], "open")

    def test_cannot_reopen_open_ticket(self):
        with self.assertRaises(ValueError):
            reopen_ticket(self.tickets, "T001")

        self.assertEqual(self.tickets[0]["status"], "open")

    def test_queue_priority_and_ticket_id_order(self):
        self.tickets = [
            make_ticket("T010", "high"),
            make_ticket("T003", "critical"),
            make_ticket("T002", "high"),
            make_ticket("T001", "low"),
            make_ticket("T004", "medium", "resolved"),
        ]

        queue = get_work_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T003", "T002", "T010", "T001"],
        )

    def test_queue_does_not_reorder_original_list(self):
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

        self.assertEqual(get_work_queue(self.tickets), [])

if __name__ == "__main__":
    unittest.main()

    def test_work_queue_excludes_in_progress_tickets(self):
        tickets = [
            {
                "id": "T001",
                "title": "Open issue",
                "priority": "high",
                "status": "open",
            },
            {
                "id": "T002",
                "title": "In progress issue",
                "priority": "critical",
                "status": "in_progress",
            },
        ]

        queue = get_work_queue(tickets)

        self.assertEqual([ticket["id"] for ticket in queue], ["T001"])
