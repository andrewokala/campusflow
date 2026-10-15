
"""Safe JSON persistence for CampusFlow tickets."""

import json
import os
import re
import tempfile

DEFAULT_DATA_FILE = "data/tickets.json"

VALID_CATEGORIES = {"network", "hardware", "software", "other"}
VALID_URGENCIES = {"low", "medium", "high"}
VALID_PRIORITIES = {"critical", "high", "medium", "low"}
VALID_STATUSES = {"open", "in_progress", "resolved"}
from campusflow.tickets import calculate_priority


def validate_ticket(ticket, index):
    """Validate one ticket without modifying it."""
    label = f"Ticket at position {index}"

    if not isinstance(ticket, dict):
        raise ValueError(f"{label} must be a JSON object.")

    required = {
        "id", "title", "category", "urgency",
        "affected_users", "priority", "status", "assigned_to",
    }
    missing = required - ticket.keys()
    if missing:
        raise ValueError(
            f"{label} is missing required fields: {', '.join(sorted(missing))}."
        )

    ticket_id = ticket["id"]
    if not isinstance(ticket_id, str) or not re.fullmatch(r"T\d{3,}", ticket_id):
        raise ValueError(f"{label} has an invalid ticket ID.")

    if not isinstance(ticket["title"], str) or not ticket["title"].strip():
        raise ValueError(f"{label} must have a non-empty title.")

    for field, allowed in (
        ("category", VALID_CATEGORIES),
        ("urgency", VALID_URGENCIES),
        ("priority", VALID_PRIORITIES),
        ("status", VALID_STATUSES),
    ):
        value = ticket[field]
        if not isinstance(value, str) or value.lower() not in allowed:
            raise ValueError(f"{label} has an invalid {field}.")

    users = ticket["affected_users"]
    if isinstance(users, bool) or not isinstance(users, int) or users <= 0:
        raise ValueError(f"{label} must have a positive integer affected_users.")

    if ticket["priority"] != calculate_priority(ticket["urgency"], users):
        raise ValueError(f"{label} has priority inconsistent with urgency and users.")
    if ticket["category"].lower() not in VALID_CATEGORIES:
        raise ValueError(f"{label} has noncanonical category.")
    if ticket["urgency"] not in VALID_URGENCIES or ticket["status"] not in VALID_STATUSES:
        raise ValueError(f"{label} has noncanonical urgency/status.")
    if ticket["status"] == "in_progress" and not ticket["assigned_to"]:
        raise ValueError(f"{label} is in progress without assignment.")
    notes = ticket.get("notes", [])  # Old records without notes remain supported.
    if not isinstance(notes, list):
        raise ValueError(f"{label} notes must be a list.")
    seen_notes = set()
    for note in notes:
        if not isinstance(note, dict) or not {"note_id", "author", "message"} <= note.keys():
            raise ValueError(f"{label} contains an invalid note.")
        nid = note["note_id"]
        if not isinstance(nid, str) or not re.fullmatch(r"N\d{3,}", nid) or nid in seen_notes:
            raise ValueError(f"{label} contains duplicate or invalid note ID.")
        seen_notes.add(nid)
        if not isinstance(note["author"], str) or not note["author"].strip():
            raise ValueError(f"{label} has an invalid note author.")
        if not isinstance(note["message"], str) or not 5 <= len(note["message"].strip()) <= 300:
            raise ValueError(f"{label} has an invalid note message.")

    assigned = ticket["assigned_to"]
    if assigned is not None and (
        not isinstance(assigned, str) or not assigned.strip()
    ):
        raise ValueError(f"{label} has an invalid assigned_to value.")


def save_tickets(tickets, filepath=DEFAULT_DATA_FILE):
    """Validate and atomically save tickets to JSON."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    validate_ticket_collection(tickets)

    directory = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(directory, exist_ok=True)
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name
            json.dump(tickets, temp_file, indent=2)
            temp_file.write("\n")

        os.replace(temp_path, filepath)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def validate_ticket_collection(tickets):
    """Validate all records and reject duplicate ticket IDs."""
    seen_ids = set()

    for index, ticket in enumerate(tickets, start=1):
        validate_ticket(ticket, index)
        ticket_id = ticket["id"]

        if ticket_id in seen_ids:
            raise ValueError(f"Duplicate ticket ID detected: {ticket_id}.")

        seen_ids.add(ticket_id)


def load_tickets(filepath=DEFAULT_DATA_FILE):
    """Load and validate tickets before returning them."""
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        raise ValueError(
            f"Corrupted or malformed JSON detected in '{filepath}'. "
            "Existing data was not overwritten."
        ) from err

    if not isinstance(data, list):
        raise ValueError(
            f"Invalid file format in '{filepath}': expected a list of tickets."
        )

    validate_ticket_collection(data)
    return data
