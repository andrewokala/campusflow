
#!/usr/bin/env python3
"""CampusFlow Helpdesk CLI."""

import sys

from campusflow.storage import (
    DEFAULT_DATA_FILE,
    load_tickets,
    save_tickets,
)
from campusflow.tickets import (
    create_ticket,
    ALLOWED_CATEGORIES,
    ALLOWED_URGENCIES,
)
from campusflow.workflow import (
    find_ticket,
    assign_ticket,
    change_status,
    reopen_ticket,
    get_work_queue,
)
from campusflow.reports import format_report
from campusflow.search import search_tickets
from campusflow.notes import add_note, get_notes


def display_ticket_summary_row(ticket):
    """Format one ticket for a table."""
    assigned = ticket.get("assigned_to") or "Unassigned"

    return (
        f"{ticket.get('id', ''):<6} | "
        f"{ticket.get('priority', '').upper():<8} | "
        f"{ticket.get('status', ''):<11} | "
        f"{ticket.get('category', ''):<9} | "
        f"{assigned:<14} | "
        f"{ticket.get('title', '')}"
    )


def print_ticket_details(ticket):
    """Display the details of one ticket."""
    print("\n--- Ticket Details ---")
    print(f"  ID:             {ticket.get('id')}")
    print(f"  Title:          {ticket.get('title')}")
    print(f"  Category:       {ticket.get('category')}")
    print(f"  Urgency:        {ticket.get('urgency')}")
    print(f"  Affected Users: {ticket.get('affected_users')}")
    print(f"  Priority:       {ticket.get('priority', '').upper()}")
    print(f"  Status:         {ticket.get('status')}")
    print(f"  Assigned To:    {ticket.get('assigned_to') or 'Unassigned'}")
    print("-----------------------\n")


def handle_create_ticket(tickets):
    """Collect input and create a ticket."""
    print("\n--- Create New Ticket ---")

    title = input("Enter Title: ").strip()
    category = input(
        f"Enter Category ({', '.join(sorted(ALLOWED_CATEGORIES))}): "
    ).strip()
    urgency = input(
        f"Enter Urgency ({', '.join(sorted(ALLOWED_URGENCIES))}): "
    ).strip()
    users_raw = input("Enter Number of Affected Users: ").strip()

    try:
        affected_users = int(users_raw)
        ticket = create_ticket(
            tickets, title, category, urgency, affected_users
        )
        save_tickets(tickets)

        print(
            f"\nTicket created successfully! ID: {ticket['id']} "
            f"[Priority: {ticket['priority'].upper()}]\n"
        )
    except ValueError as err:
        print(f"\nValidation Error: {err}\n")


def handle_list_tickets(tickets):
    """Display all tickets."""
    print("\n--- All Tickets ---")

    if not tickets:
        print("No tickets found in the system.\n")
        return

    header = (
        f"{'ID':<6} | {'PRIORITY':<8} | {'STATUS':<11} | "
        f"{'CATEGORY':<9} | {'ASSIGNED TO':<14} | TITLE"
    )
    print(header)
    print("-" * (len(header) + 20))

    for ticket in tickets:
        print(display_ticket_summary_row(ticket))

    print(f"\nTotal: {len(tickets)} ticket(s)\n")


def handle_view_ticket(tickets):
    """Display one ticket by ID."""
    ticket_id = input("\nEnter Ticket ID to view (e.g., T001): ").strip()

    try:
        ticket = find_ticket(tickets, ticket_id)
        print_ticket_details(ticket)
    except ValueError as err:
        print(f"\nError: {err}\n")


def handle_assign_ticket(tickets):
    """Assign a ticket to a staff member."""
    ticket_id = input("\nEnter Ticket ID to assign: ").strip()
    staff_name = input("Enter Staff Member Name: ").strip()

    try:
        assign_ticket(tickets, ticket_id, staff_name)
        save_tickets(tickets)

        print(f"\nTicket {ticket_id} assigned successfully.\n")
    except ValueError as err:
        print(f"\nError: {err}\n")


def handle_change_status(tickets):
    """Change a ticket's status."""
    ticket_id = input("\nEnter Ticket ID: ").strip()
    new_status = input(
        "Enter New Status (in_progress / resolved): "
    ).strip()

    try:
        ticket = change_status(tickets, ticket_id, new_status)
        save_tickets(tickets)

        print(
            f"\nTicket {ticket['id']} status updated to "
            f"'{ticket['status']}'.\n"
        )
    except ValueError as err:
        print(f"\nTransition Error: {err}\n")


def handle_reopen_ticket(tickets):
    """Reopen a resolved ticket."""
    ticket_id = input("\nEnter Ticket ID to reopen: ").strip()

    try:
        ticket = reopen_ticket(tickets, ticket_id)
        save_tickets(tickets)

        print(
            f"\nTicket {ticket['id']} reopened successfully. "
            "Status: open.\n"
        )
    except ValueError as err:
        print(f"\nError: {err}\n")


def handle_work_queue(tickets):
    """Display open tickets in priority order."""
    print("\n--- Priority Work Queue (Open Tickets Only) ---")

    queue = get_work_queue(tickets)

    if not queue:
        print("No open tickets in the work queue.\n")
        return

    header = (
        f"{'ID':<6} | {'PRIORITY':<8} | {'STATUS':<11} | "
        f"{'CATEGORY':<9} | {'ASSIGNED TO':<14} | TITLE"
    )
    print(header)
    print("-" * (len(header) + 20))

    for ticket in queue:
        print(display_ticket_summary_row(ticket))

    print(f"\nOpen Queue: {len(queue)} ticket(s).\n")


def handle_search_tickets(tickets):
    """Search using any combination of filters."""
    print("\n--- Search Tickets ---")
    print("Leave a filter blank to skip it.")

    ticket_id = input("Ticket ID: ").strip() or None
    title = input("Title contains: ").strip() or None
    category = input("Category: ").strip() or None
    urgency = input("Urgency: ").strip() or None
    priority = input("Priority: ").strip() or None
    status = input("Status: ").strip() or None
    assigned_to = input("Assigned staff: ").strip() or None

    results = search_tickets(
        tickets,
        ticket_id=ticket_id,
        title=title,
        category=category,
        urgency=urgency,
        priority=priority,
        status=status,
        assigned_to=assigned_to,
    )

    print(f"\nFound {len(results)} matching ticket(s).")

    if results:
        for ticket in results:
            print(display_ticket_summary_row(ticket))

    print()


def handle_ticket_notes(tickets):
    """Add or view timestamped follow-up notes."""
    ticket_id = input("\nEnter Ticket ID: ").strip()

    try:
        find_ticket(tickets, ticket_id)
    except ValueError as err:
        print(f"\nError: {err}\n")
        return

    print("\n1. Add a follow-up note")
    print("2. View existing notes")
    action = input("Choose an option: ").strip()

    if action == "1":
        author = input("Your name: ").strip()
        message = input("Note: ").strip()

        try:
            note = add_note(tickets, ticket_id, author, message)
            save_tickets(tickets)
            print(f"\nNote {note['note_id']} added.\n")
        except ValueError as err:
            print(f"\nError: {err}\n")

    elif action == "2":
        notes = get_notes(tickets, ticket_id)

        if not notes:
            print("\nNo follow-up notes for this ticket.\n")
            return

        print(f"\n--- Notes for {ticket_id} ---")

        for note in notes:
            print(
                f"[{note['note_id']}] "
                f"{note.get('author', 'Unknown author')}: "
                f"{note['message']}"
            )

        print()

    else:
        print("\nInvalid notes option.\n")


def handle_reports(tickets):
    """Display ticket summary reports."""
    print("\n" + format_report(tickets) + "\n")


def handle_save(tickets):
    """Save tickets to disk."""
    try:
        save_tickets(tickets)
        print(f"\nTickets saved to '{DEFAULT_DATA_FILE}'.\n")
    except (ValueError, OSError, TypeError) as err:
        print(f"\nSave failed: {err}\n")


def main():
    """Run the CampusFlow menu."""
    print("=" * 44)
    print("    WELCOME TO CAMPUSFLOW HELPDESK CLI")
    print("=" * 44)

    try:
        tickets = load_tickets()
        print(
            f"Loaded {len(tickets)} existing ticket(s) "
            f"from '{DEFAULT_DATA_FILE}'.\n"
        )
    except (ValueError, OSError) as err:
        print(f"\nUnable to load tickets: {err}\n")
        sys.exit(1)

    while True:
        print("--- Menu Options ---")
        print("1. Create New Ticket")
        print("2. List All Tickets")
        print("3. View Ticket Details")
        print("4. Assign Ticket to Staff")
        print("5. Change Ticket Status")
        print("6. Reopen Resolved Ticket")
        print("7. View Priority Work Queue")
        print("8. View Summary Report")
        print("9. Save Tickets to Disk")
        print("10. Search Tickets")
        print("11. Add / View Ticket Notes")
        print("0. Exit")

        try:
            choice = input("\nSelect an option [0-11]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting CampusFlow. Goodbye!")
            break

        if choice == "1":
            handle_create_ticket(tickets)
        elif choice == "2":
            handle_list_tickets(tickets)
        elif choice == "3":
            handle_view_ticket(tickets)
        elif choice == "4":
            handle_assign_ticket(tickets)
        elif choice == "5":
            handle_change_status(tickets)
        elif choice == "6":
            handle_reopen_ticket(tickets)
        elif choice == "7":
            handle_work_queue(tickets)
        elif choice == "8":
            handle_reports(tickets)
        elif choice == "9":
            handle_save(tickets)
        elif choice == "10":
            handle_search_tickets(tickets)
        elif choice == "11":
            handle_ticket_notes(tickets)
        elif choice == "0":
            try:
                save_tickets(tickets)
                print("\nAll tickets saved. Exiting CampusFlow. Goodbye!")
                break
            except (ValueError, OSError, TypeError) as err:
                print(f"\nCould not save tickets: {err}")
        else:
            print("\nInvalid selection. Choose an option from 0 to 11.\n")


if __name__ == "__main__":
    main()
