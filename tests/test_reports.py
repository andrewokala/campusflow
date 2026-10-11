import unittest

from campusflow.reports import (
    generate_ticket_summary,
    format_report,
)


class TestReports(unittest.TestCase):

    def test_empty_ticket_list(self):
        summary = generate_ticket_summary([])
        self.assertEqual(summary["total"], 0)
        self.assertEqual(
            summary["by_status"],
            {"open": 0, "in_progress": 0, "resolved": 0},
        )
        self.assertEqual(
            summary["by_priority"],
            {"critical": 0, "high": 0, "medium": 0, "low": 0},
        )

        formatted = format_report([])
        self.assertIn("Total Tickets: 0", formatted)

    def test_summary_with_tickets(self):
        tickets = [
            {"id": "T001", "status": "open", "priority": "critical"},
            {"id": "T002", "status": "in_progress", "priority": "high"},
            {"id": "T003", "status": "resolved", "priority": "high"},
            {"id": "T004", "status": "open", "priority": "low"},
        ]
        summary = generate_ticket_summary(tickets)
        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["by_status"]["open"], 2)
        self.assertEqual(summary["by_status"]["in_progress"], 1)
        self.assertEqual(summary["by_status"]["resolved"], 1)
        self.assertEqual(summary["by_priority"]["critical"], 1)
        self.assertEqual(summary["by_priority"]["high"], 2)
        self.assertEqual(summary["by_priority"]["medium"], 0)
        self.assertEqual(summary["by_priority"]["low"], 1)

    def test_case_insensitivity(self):
        tickets = [
            {"id": "T001", "status": "OPEN", "priority": "CRITICAL"},
            {"id": "T002", "status": "In_Progress", "priority": "High"},
        ]
        summary = generate_ticket_summary(tickets)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["by_status"]["open"], 1)
        self.assertEqual(summary["by_status"]["in_progress"], 1)
        self.assertEqual(summary["by_priority"]["critical"], 1)
        self.assertEqual(summary["by_priority"]["high"], 1)

    def test_format_report_string(self):
        tickets = [
            {"id": "T001", "status": "open", "priority": "medium"}
        ]
        report_text = format_report(tickets)
        self.assertIn("Total Tickets: 1", report_text)
        self.assertIn("open: 1", report_text)
        self.assertIn("medium: 1", report_text)


if __name__ == "__main__":
    unittest.main()
