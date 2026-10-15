
"""Follow-up notes for CampusFlow tickets."""

from datetime import datetime, timezone

from campusflow.workflow import find_ticket


def add_note(tickets, ticket_id, author, content):
    """Add a timestamped note to a ticket that is not resolved."""
    ticket = find_ticket(tickets, ticket_id)

    if ticket.get("status") == "resolved":
        raise ValueError("Reopen the ticket before adding a note.")

    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author cannot be empty.")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("Note content cannot be empty.")

    note = {
        "author": author.strip(),
        "content": content.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    ticket.setdefault("notes", []).append(note)
    return note


def get_notes(tickets, ticket_id):
    """Return a copy of a ticket's notes."""
    ticket = find_ticket(tickets, ticket_id)
    return list(ticket.get("notes", []))
