# CampusFlow — Architecture & Design Decisions

This document records the architectural agreements and function contracts between Engineer A and Engineer B for the CampusFlow project.

---

## 1. Division of Responsibilities

* **Engineer A:**
  * Feature F1 (Ticket Creation & Validation)
  * Feature F1 Priority Calculation Engine (`calculate_priority`)
  * Feature F2 (Ticket Listing & Viewing)
  * Automated tests in `tests/test_tickets.py`
* **Engineer B:**
  * Feature F3 (Ticket Assignment — `assign_ticket`)
  * Feature F4 (Status Transitions & Reopening — `change_status`, `reopen_ticket`)
  * Feature F5 (Work Queue Prioritization — `get_work_queue`)
  * Feature F6 (System Reporting — `generate_ticket_summary`, `format_report`)
  * Automated tests in `tests/test_workflow.py` and `tests/test_reports.py`
* **Shared / Integrated:**
  * Feature F7 (JSON Storage & Persistence — `storage.py`)
  * CLI Interface (`main.py`)
  * Data contracts, code reviews, and PR approvals

---

## 2. Core Function Contracts & Data Structure

### 2.1 Ticket Data Structure
Each ticket is represented as a Python dictionary with normalized lowercase field values:
```python
{
    "id": "T001",                   # String: 'T' followed by 3+ digits (e.g., 'T001')
    "title": "Campus Wi-Fi is down", # Non-empty string
    "category": "Network",           # "Network" | "Hardware" | "Software" | "Other"
    "urgency": "high",              # "low" | "medium" | "high" (normalized lowercase)
    "affected_users": 15,           # Positive integer (> 0)
    "priority": "critical",         # "critical" | "high" | "medium" | "low"
    "status": "open",               # "open" | "in_progress" | "resolved"
    "assigned_to": None             # None or non-empty string (staff name)
}
```

### 2.2 In-Memory State & Storage
* The ticket collection is stored in-memory as a Python `list` of ticket dictionaries.
* Functions receive the `tickets` list as an argument and either modify the dictionary in-place or return a newly filtered/sorted list.
* The collection is persisted to disk using `campusflow.storage.save_tickets(tickets, filepath)` and loaded via `load_tickets(filepath)`.

### 2.3 Error Handling & Exceptions
* Business logic functions signal invalid inputs, illegal state transitions, or missing tickets by raising `ValueError` with descriptive messages.
* The CLI layer (`main.py`) wraps calls in `try ... except ValueError as err:` blocks and displays user-friendly errors without crashing the application.
* Interactive input (`input()`) is strictly confined to the CLI layer (`main.py`). All business logic in `campusflow/` consists of pure, deterministic functions that can be tested in `unittest` without mock CLI prompts.

---

## 3. Engineer B Function Specifications

### `find_ticket(tickets, ticket_id) -> dict`
* **Input:** `tickets: list[dict]`, `ticket_id: str`
* **Behavior:** Searches `tickets` for matching `id`.
* **Errors:** Raises `ValueError("Ticket not found: <id>")` if not present.

### `assign_ticket(tickets, ticket_id, staff_name) -> dict`
* **Input:** `tickets: list[dict]`, `ticket_id: str`, `staff_name: str`
* **Behavior:** Strips whitespace and assigns `ticket["assigned_to"] = staff_name.strip()`.
* **Errors:**
  * Raises `ValueError` if `staff_name` is empty or whitespace.
  * Raises `ValueError` if ticket status is `"resolved"`.
  * Raises `ValueError` if `ticket_id` is unknown (via `find_ticket`).

### `change_status(tickets, ticket_id, new_status) -> dict`
* **Input:** `tickets: list[dict]`, `ticket_id: str`, `new_status: str`
* **Lifecycle Rules:**
  * `open` $\rightarrow$ `in_progress`: Ticket must currently be `"open"` and `assigned_to` must not be None or blank.
  * `in_progress` $\rightarrow$ `resolved`: Ticket must currently be `"in_progress"`.
  * Modifying an already resolved ticket directly is rejected; must be reopened first.
  * Any other transition raises `ValueError`.

### `reopen_ticket(tickets, ticket_id) -> dict`
* **Input:** `tickets: list[dict]`, `ticket_id: str`
* **Behavior:** Sets `ticket["status"] = "open"`.
* **Errors:** Raises `ValueError` if ticket status is not currently `"resolved"`.

### `get_work_queue(tickets) -> list[dict]`
* **Input:** `tickets: list[dict]`
* **Behavior:** Returns a *new* list containing only tickets with status `"open"` or `"in_progress"`.
* **Ordering:**
  1. Priority order: `critical` (0) $\rightarrow$ `high` (1) $\rightarrow$ `medium` (2) $\rightarrow$ `low` (3).
  2. Tie-breaking: Earlier numeric ID (e.g., `T002` before `T010`).
* **Side-effects:** Does not mutate the original `tickets` list order.

### `generate_ticket_summary(tickets) -> dict`
* **Input:** `tickets: list[dict]`
* **Behavior:** Aggregates totals:
  * `total`: Count of all tickets.
  * `by_status`: Counts for `"open"`, `"in_progress"`, and `"resolved"`.
  * `by_priority`: Counts for `"critical"`, `"high"`, `"medium"`, and `"low"`.
* **Edge Cases:** Safely handles empty ticket lists (`[]`), returning 0 for all counts.

### `format_report(summary_or_tickets) -> str`
* **Input:** `summary: dict` or `tickets: list[dict]`
* **Behavior:** Returns a formatted human-readable string suitable for CLI display.
