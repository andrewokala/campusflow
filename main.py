#!/usr/bin/env python3


import sys
from campusflow.storage import load_tickets, save_tickets, DEFAULT_DATA_FILE
from campusflow.tickets import create_ticket, ALLOWED_CATEGORIES, ALLOWED_URGENCIES
from campusflow.workflow import (
    find_ticket,
    assign_ticket,
    change_status,
    reopen_ticket,
    get_work_queue,
)
from campusflow.reports import format_report


def display_ticket_summary_row(ticket):
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
    print("\n--- Ticket Details ---")
    print(f"  ID:             {ticket.get('id')}")
    print(f"  Title:          {ticket.get('title')}")
    print(f"  Category:       {ticket.get('category')}")
    print(f"  Urgency:        {ticket.get('urgency')}")
    print(f"  Affected Users: {ticket.get('affected_users')}")
    print(f"  Priority:       {ticket.get('priority').upper()}")
    print(f"  Status:         {ticket.get('status')}")
    print(f"  Assigned To:    {ticket.get('assigned_to') or 'Unassigned'}")
    print("-----------------------\n")


def handle_create_ticket(tickets):
    print("\n--- Create New Ticket ---")
    title = input("Enter Title: ").strip()
    category = input(f"Enter Category ({', '.join(sorted(ALLOWED_CATEGORIES))}): ").strip()
    urgency = input(f"Enter Urgency ({', '.join(sorted(ALLOWED_URGENCIES))}): ").strip()
    users_raw = input("Enter Number of Affected Users: ").strip()

    try:
        affected_users = int(users_raw)
    except ValueError:
        print("\n❌ Error: Affected users must be a positive integer.\n")
        return

    try:
        ticket = create_ticket(tickets, title, category, urgency, affected_users)
        save_tickets(tickets)
        print(f"\n✅ Ticket created successfully! ID: {ticket['id']} [Priority: {ticket['priority'].upper()}]\n")
    except ValueError as err:
        print(f"\n❌ Validation Error: {err}\n")


def handle_list_tickets(tickets):
    print("\n--- All Tickets ---")
    if not tickets:
        print("No tickets found in the system.\n")
        return

    header = f"{'ID':<6} | {'PRIORITY':<8} | {'STATUS':<11} | {'CATEGORY':<9} | {'ASSIGNED TO':<14} | TITLE"
    print(header)
    print("-" * len(header) + "-" * 20)
    for ticket in tickets:
        print(display_ticket_summary_row(ticket))
    print(f"\nTotal: {len(tickets)} ticket(s)\n")


def handle_view_ticket(tickets):
    ticket_id = input("\nEnter Ticket ID to view (e.g., T001): ").strip()
    try:
        ticket = find_ticket(tickets, ticket_id)
        print_ticket_details(ticket)
    except ValueError as err:
        print(f"\n❌ Error: {err}\n")


def handle_assign_ticket(tickets):
    ticket_id = input("\nEnter Ticket ID to assign: ").strip()
    staff_name = input("Enter Staff Member Name: ").strip()

    try:
        ticket = assign_ticket(tickets, ticket_id, staff_name)
        save_tickets(tickets)
        print(f"\n✅ Ticket {ticket['id']} successfully assigned to '{ticket['assigned_to']}'.\n")
    except ValueError as err:
        print(f"\n❌ Error: {err}\n")


def handle_change_status(tickets):
    ticket_id = input("\nEnter Ticket ID: ").strip()
    new_status = input("Enter New Status (in_progress / resolved): ").strip()

    try:
        ticket = change_status(tickets, ticket_id, new_status)
        save_tickets(tickets)
        print(f"\n✅ Ticket {ticket['id']} status updated to '{ticket['status']}'.\n")
    except ValueError as err:
        print(f"\n❌ Transition Error: {err}\n")


def handle_reopen_ticket(tickets):
    ticket_id = input("\nEnter Ticket ID to reopen: ").strip()

    try:
        ticket = reopen_ticket(tickets, ticket_id)
        save_tickets(tickets)
        print(f"\n✅ Ticket {ticket['id']} reopened and set to status 'open'.\n")
    except ValueError as err:
        print(f"\n❌ Error: {err}\n")


def handle_work_queue(tickets):
    print("\n--- Priority Work Queue (Open / In-Progress) ---")
    queue = get_work_queue(tickets)
    if not queue:
        print("No unresolved tickets in the work queue.\n")
        return

    header = f"{'ID':<6} | {'PRIORITY':<8} | {'STATUS':<11} | {'CATEGORY':<9} | {'ASSIGNED TO':<14} | TITLE"
    print(header)
    print("-" * len(header) + "-" * 20)
    for ticket in queue:
        print(display_ticket_summary_row(ticket))
    print(f"\nActive Queue: {len(queue)} ticket(s) awaiting completion.\n")


def handle_reports(tickets):
    print("\n" + format_report(tickets) + "\n")


def handle_save(tickets):
    try:
        save_tickets(tickets)
        print(f"\n✅ Tickets saved to '{DEFAULT_DATA_FILE}'.\n")
    except Exception as err:
        print(f"\n❌ Save failed: {err}\n")


def main():
    print("=" * 44)
    print("    WELCOME TO CAMPUSFLOW HELPDESK CLI      ")
    print("=" * 44)

    try:
        tickets = load_tickets()
        print(f"Loaded {len(tickets)} existing ticket(s) from '{DEFAULT_DATA_FILE}'.\n")
    except ValueError as err:
        print(f"\n⚠️  {err}\n")
        sys.exit(1)

    while True:
        print("--- Menu Options ---")
        print("1. Create New Ticket (F1)")
        print("2. List All Tickets (F2)")
        print("3. View Ticket Details (F2)")
        print("4. Assign Ticket to Staff (F3)")
        print("5. Change Ticket Status (F4)")
        print("6. Reopen Resolved Ticket (F4)")
        print("7. View Priority Work Queue (F5)")
        print("8. View Summary Report (F6)")
        print("9. Save Tickets to Disk (F7)")
        print("0. Exit")

        try:
            choice = input("\nSelect an option [0-9]: ").strip()
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
        elif choice == "0":
            save_tickets(tickets)
            print("\nAll tickets saved. Exiting CampusFlow. Goodbye!")
            break
        else:
            print("\n❌ Invalid selection. Please choose an option from 0 to 9.\n")


if __name__ == "__main__":
    main()
