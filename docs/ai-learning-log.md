# CampusFlow — AI Learning Log

This document records the AI-assisted learning cycles and critical evaluations conducted during the sprint.

---

## Fellow: Victor Ejike (Engineer B — Workflow, Lifecycle, Queue, & Reports)

### Interaction #1 — Multi-key Sorting & Priority Tie-Breaking in Python
* **Problem:** In Feature F5 (`get_work_queue`), tickets must be sorted by custom priority hierarchy (`critical` $\rightarrow$ `high` $\rightarrow$ `medium` $\rightarrow$ `low`), and ties must be broken by earlier numeric ID (e.g., `T002` before `T010`, rather than alphabetical string sorting where `"T010"` might precede `"T02"`).
* **My initial understanding:** I knew Python's `list.sort()` accepts a `key` parameter, but I wasn't certain how to combine a non-alphabetical priority dictionary with numeric tie-breaking without writing multiple nested sort passes.
* **Prompt to AI:** *"How does Python sort using a tuple key when I have a custom priority mapping and want to break ties using numeric IDs?"*
* **Useful AI guidance:** Python compares tuples element-by-element (`(key1, key2)`). If `key1` matches, Python naturally falls back to comparing `key2`. A dictionary mapping priorities to rank integers (`{"critical": 0, "high": 1, ...}`) combined with `int(ticket["id"][1:])` produces clean, stable ordering in a single pass.
* **My independent experiment/test:** In an interactive Python session, I tested sorting sample records with identical priorities:
  ```python
  priority_order = {"high": 1}
  items = [
      {"id": "T010", "priority": "high"},
      {"id": "T002", "priority": "high"},
  ]
  items.sort(
      key=lambda x: (priority_order[x["priority"]], int(x["id"][1:]))
  )
  print([x["id"] for x in items])  # Output: ['T002', 'T010']
```
* **Verification source or result:** Added `test_queue_priority_and_ticket_id_order` and `test_queue_does_not_reorder_original_list` in `tests/test_workflow.py`. Both assertions passed.
* **Decision:** Accepted and implemented the tuple-key sorting pattern in `campusflow/workflow.py`.
* **Related file/commit:** `campusflow/workflow.py` (`get_work_queue`), `tests/test_workflow.py`.
* **What I can now explain without AI:** How Python tuple comparisons work for multi-criteria sorting and how to extract integer values from formatted string identifiers for numeric ordering.

---

### Interaction #2 — Structuring Report Aggregations and Empty-State Handling
* **Problem:** In Feature F6 (`campusflow/reports.py`), the system must summarize ticket totals and breakdowns by status and priority, and must handle zero tickets (`[]`) gracefully without crashing or throwing missing key errors.
* **My initial understanding:** I initially thought of looping over tickets and building a dictionary on the fly, but that could result in missing status/priority keys when ticket counts are zero.
* **Prompt to AI:** *"What is the best way to structure ticket summary aggregation in Python to ensure predictable schema keys and safe handling when the list is empty?"*
* **Useful AI guidance:** Pre-initialize the result dictionary with default counters set to zero for all expected statuses and priorities (`open`, `in_progress`, `resolved` and `critical`, `high`, `medium`, `low`). This guarantees consistent dictionary keys even when `tickets` is empty.
* **My independent experiment/test:** Created `generate_ticket_summary([])` with pre-defined keys and asserted that all counts equal 0:
  ```python
  summary = generate_ticket_summary([])
  assert summary["total"] == 0
  assert summary["by_status"]["open"] == 0
```
* **Verification source or result:** Added `test_empty_ticket_list` and `test_summary_with_tickets` in `tests/test_reports.py`. All tests passed.
* **Decision:** Accepted and implemented the pre-initialized dictionary pattern, and added case normalization (`.lower()`) so variations like `"OPEN"` or `"Critical"` increment the correct buckets.
* **Related file/commit:** `campusflow/reports.py`, `tests/test_reports.py`.
* **What I can now explain without AI:** How pre-defining schema dictionaries prevents missing-key errors and simplifies consumer code (like CLI renderers) when processing empty collections.

---

### Interaction #3 — State Machine Invariants & Catching Flawed AI Logic (CRITICAL EVALUATION)
* **Problem:** In Feature F4 (`change_status` and `reopen_ticket`), we need to strictly enforce lifecycle transitions (`open` $\rightarrow$ `in_progress` $\rightarrow$ `resolved`), reject unassigned tickets from entering `in_progress`, and prevent direct modification of resolved tickets without reopening.
* **My initial understanding:** The function must verify that preconditions are satisfied before changing state.
* **Prompt to AI:** *"Help draft validation logic for change_status and reopen_ticket in Python with error checks for unassigned tickets and resolved tickets."*
* **AI guidance received (Flawed Draft):** The generated code draft contained multiple critical defects:
  1. **Inverted conditional:** It checked `if ticket["status"] == "open": raise ValueError(...)` instead of `!= "open"`, meaning open tickets were blocked from progressing!
  2. **Key casing typo:** It accessed `ticket["Assigned_to"]` (uppercase `A`), which caused runtime `KeyError` exceptions when checking dictionary keys.
  3. **Callable name confusion:** In `reopen_ticket`, it wrote `ticket = ticket_id(tickets, ticket_id)`, attempting to call the string variable `ticket_id` as a function!
  4. **Case sensitivity:** In `assign_ticket`, it compared against `"Resolved"` with uppercase `R`, failing to catch `"resolved"` tickets.
* **My independent experiment/test:** Rather than blindly trusting the draft, I ran the automated test suite:
  ```bash
  python3 -m unittest discover -s tests -v
```
  The test runner immediately caught the defects:
  ```
  ERROR: test_assigned_ticket_can_progress (ValueError: Ticket must be open before works begins.)
  ERROR: test_cannot_reopen_open_ticket (TypeError: 'str' object is not callable)
  ERROR: test_reopen_resolved_ticket (TypeError: 'str' object is not callable)
  FAIL: test_reject_assignment_to_resolved_ticket (AssertionError: ValueError not raised)
  ```
* **Verification source or result:** Traced each failure through the unittest stack traces, inspected the logic, corrected the inverted conditional to `ticket["status"].lower() != "open"`, changed `ticket["Assigned_to"]` to `not ticket.get("assigned_to")`, and corrected the function call to `find_ticket(tickets, ticket_id)`. Re-ran the test suite and confirmed 19/19 tests passed.
* **Decision:** **REJECTED and CORRECTED the AI suggestions.**
* **Related file/commit:** `campusflow/workflow.py`, `tests/test_workflow.py`.
* **What I can now explain without AI:** How to design invariant checks in state machine transitions, the necessity of case normalization when inspecting dictionary values, and why rigorous unit tests are non-negotiable when evaluating AI-generated code.
