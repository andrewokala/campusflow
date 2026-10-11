# CampusFlow — Campus Technical Support Helpdesk

CampusFlow is an AI-native, command-line technical support ticket manager built for Learn2Earn campus staff to log technical issues, automatically compute priority levels, assign responsible staff, enforce lifecycle workflows, prioritize work queues, and generate system summaries.

---

## 👥 Engineering Team & Roles

* **Engineer A (Andrew Okala):**
  * Ticket creation, input validation, and priority calculation engine (F1).
  * Ticket viewing/listing (F2).
  * Automated tests in `tests/test_tickets.py`.

* **Engineer B (Victor Ejike):**
  * Staff ticket assignment (F3).
  * Status transitions (`open` $\rightarrow$ `in_progress` $\rightarrow$ `resolved`) and ticket reopening (F4).
  * Priority work queue with numeric ID tie-breaking (F5).
  * System reporting and summary metrics (F6).
  * Automated tests in `tests/test_workflow.py` and `tests/test_reports.py`.

* **Shared Implementation:**
  * JSON persistence (`campusflow/storage.py`) (F7).
  * CLI interactive runner (`main.py`).
  * Cross-reviewing pull requests and integration testing.

---

## ⚙️ Setup & Requirements

* **Python Version:** Python 3.10+ (Standard Library only; no external dependencies required).
* **Setup:**
  ```bash
  git clone https://github.com/andrewokala/campusflow.git
  cd campusflow
  ```

---

## 🧪 Running Automated Tests

Run the full automated test suite using Python's standard `unittest` framework:

```bash
python3 -m unittest discover -s tests -v
```

### Test Coverage Highlights
* **Workflow & Lifecycle:** `tests/test_workflow.py` verifies staff assignment validation, status progression guards, rejection of unassigned tickets, reopening constraints, and priority queue ordering.
* **Reporting:** `tests/test_reports.py` tests total counts, status/priority breakdowns, case normalization, and zero-ticket empty lists.

---

## 📋 Business Logic & Rules

### Priority Rules (Evaluated in Order)
1. **Rule 1:** `high` urgency **AND** $\ge 10$ affected users $\rightarrow$ `critical`
2. **Rule 2:** `high` urgency **OR** $\ge 10$ affected users $\rightarrow$ `high`
3. **Rule 3:** `medium` urgency **OR** $\ge 3$ affected users $\rightarrow$ `medium`
4. **Rule 4:** All remaining valid tickets $\rightarrow$ `low`

### Workflow Lifecycle
* Tickets start as `open`.
* To move from `open` $\rightarrow$ `in_progress`, the ticket must be assigned to a non-empty staff name.
* To move from `in_progress` $\rightarrow$ `resolved`, the ticket must currently be in progress.
* Direct modifications to `resolved` tickets are blocked until explicitly reopened (`resolved` $\rightarrow$ `open`).

---

## 📂 Documentation & AI Learning Logs
* **Design Contracts:** See [docs/design-decisions.md](docs/design-decisions.md)
* **AI Learning Log:** See [docs/ai-learning-log.md](docs/ai-learning-log.md)