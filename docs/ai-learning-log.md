# CampusFlow — AI Learning Log

This document records the AI-assisted learning cycles and critical evaluations conducted during the sprint.


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


## Fellow: Engineer A — Onminyi Andrew Okala

### CampusFlow Next — AI-assisted learning record (draft; verify independently)

**Context:** The following entries distinguish discussion and assistant-run tests from experiments personally executed by Engineer A. Do not present an assistant-run test as your own terminal verification.

### Interaction #1 — Validate before mutation and note-state safety

**Problem:** Understand why note status, author and message must be checked before appending to a ticket.

**My initial understanding:** I answered that validation checks whether required fields are available. I still need to account for valid *values* and allowed ticket status, not merely presence.

**Prompt to AI:** "So as to check if the required fields are available" (my response to the assistant's question about why `add_note()` validates status before appending).

**Useful AI guidance:** A resolved ticket cannot accept notes until reopened. Validation must check the allowed status and content before changing the ticket, so rejection leaves the entire collection unchanged.

**My independent experiment/test:** **Pending personal run.** Run `python -m unittest tests.test_engineer_a_next -v` if the tests directory is importable, or `python -m unittest discover -s tests -p 'test_engineer_a_next.py' -v`. Inspect `test_note_ids_and_reopen` and `test_invalid_note_does_not_consume_id`.

**Verification source or result:** Automated test names are present in `tests/test_engineer_a_next.py`; personal terminal output **not yet supplied**. Record actual output after running.

**Decision:** Provisional acceptance of validate-before-mutate; finalize after independent test execution.

**Related file/commit:** `campusflow/notes.py`, `tests/test_engineer_a_next.py` (commit SHA pending).

**What I can now explain without AI:** I initially focused on required fields. I can explain that a note also needs a permitted ticket status and valid content; otherwise adding it would violate the workflow. (Review this wording and revise in your own voice.)

### Interaction #2 — Duplicate ticket IDs and JSON integrity

**Problem:** Understand why successfully decoded JSON can still be unsafe to load.

**My initial understanding:** I answered that duplicate IDs should not be accepted because they conflict with each other.

**Prompt to AI:** "it shouldn't because it will conflict each other" (my answer to whether two tickets with the same ID should be accepted).

**Useful AI guidance:** JSON decoding checks syntax, not uniqueness or consistency. Validate the full loaded collection before using it; reject duplicates without changing the current in-memory list.

**My independent experiment/test:** **Pending personal run.** Create a temporary JSON file containing two otherwise valid tickets with the same ID, call `load_tickets(path)`, and confirm `ValueError` occurs. Check that an existing `tickets` list remains unchanged. Do not overwrite a real data file.

**Verification source or result:** `campusflow/storage.py` contains load validation. Actual experiment output **pending**. Relevant existing tests include storage validation and `test_corrupt_load_does_not_change_memory`.

**Decision:** Provisional acceptance of full-collection validation; finalize after the duplicate-ID experiment.

**Related file/commit:** `campusflow/storage.py`, `tests/test_engineer_a_next.py`, `tests/test_storage_validation.py` (commit SHA pending).

**What I can now explain without AI:** Duplicate IDs make it ambiguous which ticket an operation refers to. Valid JSON syntax alone does not guarantee valid ticket records. (Revise after your experiment.)

### Interaction #3 — Numeric ID continuity for notes

**Problem:** Understand how to choose a new note ID without colliding with existing IDs.

**My initial understanding:** I answered that IDs N001 and N003 should lead to N004 by adding one to the last ID. More precisely, the implementation uses the **highest numeric ID**, not necessarily the last list entry.

**Prompt to AI:** "{"note_id": "N004"} because it will check the last enter ID and add 1 to it making the next ID." (my answer to the ID continuity question).

**Useful AI guidance:** Extract numeric portions of all existing note IDs and use maximum + 1; do not rely on list length or insertion order.

**My independent experiment/test:** **Pending personal run.** In a Python shell, call `next_note_id({"notes": [{"note_id": "N003"}, {"note_id": "N001"}]})` and predict `N004` before running it.

**Verification source or result:** `test_reload_preserves_notes_and_next_ids` covers note continuity after JSON reload. Personal execution and observed output **pending**.

**Decision:** Improve my earlier explanation from "last entered ID" to "highest numeric ID". This is a conceptual correction based on inspecting the implementation; independent verification is still pending.

**Related file/commit:** `campusflow/notes.py`, `tests/test_engineer_a_next.py` (commit SHA pending).

**What I can now explain without AI:** The next note ID should be one greater than the largest existing note number, even if notes are out of order. (Confirm with the experiment.)

**Submission reminder:** The CampusFlow Next guide requires at least two genuine, independently verified AI learning cycles per engineer. These draft records are not substitutes for personal experiments or exact historical prompts where no prompt was actually sent.
