CATEGORIES = {"network": "Network", "hardware": "Hardware", "software": "Software", "other": "Other"}
URGENCIES = {"low", "medium", "high"}


def validate_ticket(title, category, urgency, affected_users):

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Title must not be blank")
    if not isinstance(category, str) or category.strip().lower() not in CATEGORIES:
        raise ValueError("Category must be Network, Hardware, Software, or Other")
    if not isinstance(urgency, str) or urgency.strip().lower() not in URGENCIES:
        raise ValueError("Urgency must be low, medium, or high")
    if type(affected_users) is not int or affected_users <= 0:
        raise ValueError("Affected users must be a positive integer")
    return title.strip(), CATEGORIES[category.strip().lower()], urgency.strip().lower(), affected_users


def calculate_priority(urgency, affected_users):
    
    if not isinstance(urgency, str) or urgency.strip().lower() not in URGENCIES:
        raise ValueError("Urgency must be low, medium, or high")
    if type(affected_users) is not int or affected_users <= 0:
        raise ValueError("Affected users must be a positive integer")
    urgency = urgency.strip().lower()
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def generate_ticket_id(tickets):
  
    max_number = 0
    for ticket in tickets:
        ticket_id = ticket["id"]
        if not isinstance(ticket_id, str) or len(ticket_id) < 2 or ticket_id[0] != "T" or not ticket_id[1:].isascii() or not ticket_id[1:].isdigit():
            raise ValueError(f"Invalid stored ticket ID: {ticket_id!r}")
        max_number = max(max_number, int(ticket_id[1:]))
    return f"T{max_number + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
  
    title, category, urgency, affected_users = validate_ticket(title, category, urgency, affected_users)
    ticket_id = generate_ticket_id(tickets)
    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
    }
    tickets.append(ticket)
    return ticket


def get_ticket(tickets, ticket_id):
  
    if not isinstance(ticket_id, str):
        raise KeyError("Ticket ID must be text")
    normalized_id = ticket_id.strip().upper()
    for ticket in tickets:
        if ticket["id"] == normalized_id:
            return ticket
    raise KeyError(f"Unknown ticket ID: {normalized_id}")