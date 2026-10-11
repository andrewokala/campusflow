"""
Reporting module for CampusFlow helpdesk tickets.
Provides summary metrics including total ticket count, status breakdown,
and priority breakdown, handling both empty and populated ticket collections.
"""


def generate_ticket_summary(tickets):
    """
    Generate summary statistics for a collection of tickets.

    Returns a dictionary with:
      - total: total number of tickets
      - by_status: dict mapping status to count (open, in_progress, resolved)
      - by_priority: dict mapping priority to count (critical, high, medium, low)
    """
    summary = {
        "total": len(tickets),
        "by_status": {
            "open": 0,
            "in_progress": 0,
            "resolved": 0,
        },
        "by_priority": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        },
    }

    for ticket in tickets:
        status = ticket.get("status", "").lower()
        if status in summary["by_status"]:
            summary["by_status"][status] += 1
        else:
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

        priority = ticket.get("priority", "").lower()
        if priority in summary["by_priority"]:
            summary["by_priority"][priority] += 1
        else:
            summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1

    return summary


def format_report(summary_or_tickets):
    """
    Format a ticket summary dictionary or list of tickets into a human-readable CLI report.
    """
    if isinstance(summary_or_tickets, list):
        summary = generate_ticket_summary(summary_or_tickets)
    else:
        summary = summary_or_tickets

    lines = [
        "========================================",
        "          CAMPUSFLOW REPORT             ",
        "========================================",
        f"Total Tickets: {summary['total']}",
        "",
        "Breakdown by Status:",
    ]
    for status, count in summary["by_status"].items():
        lines.append(f"  - {status}: {count}")

    lines.append("")
    lines.append("Breakdown by Priority:")
    for priority, count in summary["by_priority"].items():
        lines.append(f"  - {priority}: {count}")

    lines.append("========================================")
    return "\n".join(lines)
