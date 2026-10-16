"""Engineer A: validated follow-up note operations."""
from campusflow.workflow import find_ticket


def next_note_id(ticket):
    """Return the next per-ticket ID without reusing an existing ID."""
    notes = ticket.get("notes", [])
    maximum = max((int(n["note_id"][1:]) for n in notes), default=0)
    return f"N{maximum + 1:03d}"


def add_note(tickets, ticket_id, author, message):
    """Validate before mutation; store one canonical message field."""
    ticket = find_ticket(tickets, ticket_id)
    if ticket.get("status") not in ("open", "in_progress"):
        raise ValueError("Reopen the ticket before adding a note.")
    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author cannot be empty.")
    if not isinstance(message, str) or not 5 <= len(message.strip()) <= 300:
        raise ValueError("Note message must contain 5 to 300 characters.")
    note_id = next_note_id(ticket)
    note = {"note_id": note_id, "author": author.strip(), "message": message.strip()}
    ticket.setdefault("notes", []).append(note)
    return note


def get_notes(tickets, ticket_id):
    """Return notes in numeric ID order without changing stored order."""
    ticket = find_ticket(tickets, ticket_id)
    return sorted(ticket.get("notes", []), key=lambda n: int(n["note_id"][1:]))
