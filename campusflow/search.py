
"""Multi-filter search for CampusFlow tickets."""


def search_tickets(
    tickets,
    ticket_id=None,
    title=None,
    category=None,
    urgency=None,
    priority=None,
    status=None,
    assigned_to=None,
):
    """Return tickets matching every supplied filter."""
    filters = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }

    results = []

    for ticket in tickets:
        matched = True

        for field, expected in filters.items():
            if expected is None:
                continue

            actual = ticket.get(field)

            if field in {"id", "title", "assigned_to"}:
                if expected.lower() not in str(actual or "").lower():
                    matched = False
                    break
            elif str(actual or "").lower() != str(expected).lower():
                matched = False
                break

        if matched:
            results.append(ticket)

    return results
