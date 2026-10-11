"""
Persistence module for CampusFlow helpdesk tickets.
Handles saving to JSON and loading from JSON with robust error handling for missing
or malformed files.
"""

import json
import os

DEFAULT_DATA_FILE = "data/tickets.json"


def save_tickets(tickets, filepath=DEFAULT_DATA_FILE):
    """
    Save the list of tickets to a JSON file.
    Ensures parent directories exist.
    """
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2)


def load_tickets(filepath=DEFAULT_DATA_FILE):
    """
    Load tickets from a JSON file.
    - Missing file allows a fresh start (returns empty list []).
    - Malformed JSON raises ValueError with a clear message to prevent data loss.
    """
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        raise ValueError(
            f"Corrupted or malformed JSON detected in '{filepath}': {err}. "
            "Data was not overwritten to prevent data loss."
        ) from err

    if not isinstance(data, list):
        raise ValueError(
            f"Invalid file format in '{filepath}': expected a list of tickets, got {type(data).__name__}."
        )

    return data
