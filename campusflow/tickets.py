"""
Ticket creation, input validation, and priority calculation module for CampusFlow.
"""

ALLOWED_CATEGORIES = {"Network", "Hardware", "Software", "Other"}
ALLOWED_URGENCIES = {"low", "medium", "high"}


def calculate_priority(urgency, affected_users):
    """
    Calculate ticket priority based on sprint rules evaluated in strict order:
    RULE 1: high urgency AND >= 10 affected users -> critical
    RULE 2: high urgency OR  >= 10 affected users -> high
    RULE 3: medium urgency OR >= 3 affected users  -> medium
    RULE 4: all remaining valid tickets            -> low
    """
    if not isinstance(urgency, str) or urgency.strip().lower() not in ALLOWED_URGENCIES:
        raise ValueError(f"Urgency must be one of {sorted(ALLOWED_URGENCIES)}.")

    if not isinstance(affected_users, int) or isinstance(affected_users, bool) or affected_users <= 0:
        raise ValueError("affected_users must be a positive integer greater than zero.")

    urgency_norm = urgency.strip().lower()

    if urgency_norm == "high" and affected_users >= 10:
        return "critical"
    if urgency_norm == "high" or affected_users >= 10:
        return "high"
    if urgency_norm == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def generate_ticket_id(tickets):
    """
    Generate the next unique ticket ID (T001, T002, ...) based on existing tickets.
    Ensures IDs remain unique even after data reload.
    """
    max_num = 0
    for ticket in tickets:
        tid = ticket.get("id", "")
        digits = "".join(ch for ch in tid if ch.isdigit())
        if digits:
            num = int(digits)
            if num > max_num:
                max_num = num

    return f"T{max_num + 1:03d}"


def normalize_category(category):
    """
    Normalize category with case-insensitivity against ALLOWED_CATEGORIES.
    """
    if not isinstance(category, str) or not category.strip():
        raise ValueError(f"Category must be one of {sorted(ALLOWED_CATEGORIES)}.")

    for allowed in ALLOWED_CATEGORIES:
        if category.strip().lower() == allowed.lower():
            return allowed

    raise ValueError(f"Invalid category '{category}'. Allowed categories: {sorted(ALLOWED_CATEGORIES)}.")


def normalize_urgency(urgency):
    """
    Normalize urgency level with case-insensitivity.
    """
    if not isinstance(urgency, str) or not urgency.strip():
        raise ValueError(f"Urgency must be one of {sorted(ALLOWED_URGENCIES)}.")

    urgency_lower = urgency.strip().lower()
    if urgency_lower in ALLOWED_URGENCIES:
        return urgency_lower

    raise ValueError(f"Invalid urgency '{urgency}'. Allowed urgency: {sorted(ALLOWED_URGENCIES)}.")


def create_ticket(tickets, title, category, urgency, affected_users):
    """
    Validate inputs, calculate priority, assign a unique ID, and store the ticket record.
    """
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Title must not be blank.")

    norm_category = normalize_category(category)
    norm_urgency = normalize_urgency(urgency)

    if not isinstance(affected_users, int) or isinstance(affected_users, bool) or affected_users <= 0:
        raise ValueError("affected_users must be a positive integer greater than zero.")

    priority = calculate_priority(norm_urgency, affected_users)
    ticket_id = generate_ticket_id(tickets)

    ticket = {
        "id": ticket_id,
        "title": title.strip(),
        "category": norm_category,
        "urgency": norm_urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
    }

    tickets.append(ticket)
    return ticket
