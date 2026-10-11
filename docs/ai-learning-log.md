## Fellow: <your name>
### Interaction #1 — <concept/topic>
Problem: Understanding how to reject invalid inputs withour corrupting stored tickets.


My initial understanding: Using a function to validate the modified ticket collection


Prompt to AI: How do i reject invalid inputs without breaking initial data collection


Useful AI guidance: Validate all inputs before modifying the ticket collection.


My independent experiment/test: Run the `test_tickets` test.


Verification source or result: test_blank_title_rejected (test_tickets.TicketTests.test_blank_title_rejected) ... ok
test_boolean_is_not_valid_count (test_tickets.TicketTests.test_boolean_is_not_valid_count) ... ok
test_creation_defaults_and_normalization (test_tickets.TicketTests.test_creation_defaults_and_normalization) ... ok
test_critical_priority (test_tickets.TicketTests.test_critical_priority) ... ok
test_high_priority (test_tickets.TicketTests.test_high_priority) ... ok
test_invalid_category_rejected (test_tickets.TicketTests.test_invalid_category_rejected) ... ok
test_lookup_case_insensitive (test_tickets.TicketTests.test_lookup_case_insensitive) ... ok
test_lookup_unknown_id (test_tickets.TicketTests.test_lookup_unknown_id) ... ok
test_low_priority (test_tickets.TicketTests.test_low_priority) ... ok
test_medium_priority (test_tickets.TicketTests.test_medium_priority) ... ok
test_sequential_ids_after_reload_shape (test_tickets.TicketTests.test_sequential_ids_after_reload_shape) ... ok
test_zero_users_does_not_mutate (test_tickets.TicketTests.test_zero_users_does_not_mutate) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.001s

OK


Decision: Accepted


Related file/commit: `tests/test_ticket.py`


What I can now explain without AI: Rejecting invalid input is not enough if the function has already modified the application state.
