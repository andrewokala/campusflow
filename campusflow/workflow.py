#now i will create a function that
def find_ticket(tickets, ticket_id):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    raise ValueError("Ticket not found: "+ ticket_id)



#now let me add another function called find_ticket

def assign_ticket(tickets, ticket_id, staff_name):
    ticket = find_ticket(tickets, ticket_id)

    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff_name can not be empty.")

    if ticket["status"].lower() == "resolved":
        raise ValueError("Reopen Ticket before modifying it.")

    ticket["assigned_to"] = staff_name.strip()

    return ticket


#====================================
# we have to create the validation status transtions
#=====================================

def change_status(tickets, ticket_id, new_status):
    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"].lower() == "resolved":
        raise ValueError("Reopen ticket before modifying it.")

    if not isinstance(new_status, str):
        raise ValueError("Status must be text.")
    status_target = new_status.strip().lower()

    if status_target == "in_progress":
        if ticket["status"].lower() != "open":
            raise ValueError("Ticket must be open before work begins.")

        if not ticket.get("assigned_to"):
            raise ValueError("Assign the ticket before starting the work.")

    elif status_target == "resolved":
        if ticket["status"].lower() != "in_progress":
            raise ValueError("Ticket must be in progress before resolution.")

    else:
        raise ValueError("Invalid status transition.")

    ticket["status"] = status_target

    return ticket

    #======================
    # now lets add the explicitly reopen a resovled ticket
    #=======================


def reopen_ticket(tickets, ticket_id):
    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"].lower() != "resolved":
        raise ValueError("Only Resolved Ticket can be reopened.")

    ticket["status"] = "open"

    return ticket


#===================
# now let me build the priority workflow queue 
#==================




def get_work_queue(tickets):
    """Return open tickets sorted by priority, then numeric ticket ID."""
    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    open_tickets = [
        ticket for ticket in tickets
        if ticket.get("status", "").lower() == "open"
    ]

    return sorted(
        open_tickets,
        key=lambda ticket: (
            priority_order.get(ticket.get("priority", "").lower(), 99),
            int(ticket["id"][1:]),
        ),
    )
