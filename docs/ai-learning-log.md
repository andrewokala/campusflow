## Fellow: Onminyi Andrew Okala 
### Interaction #1 — Input validation and safe mutation
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




## Fellow: Onminyi Andrew Okala
### Interaction #2 — Understanding `and` and `or` in python priority calculation


Problem: I neede to understand how Python's logical operators (`and` and `or`) works whan checking through multiple conditions, in regards to ticket priority in CampusFlow.


My initial understanding: I understood that `and` requires both conditions to be true, while `or` requires at least on condition to be true. However, I needed to understand why order of conditions matters when applying it to multiple priority rules.


Prompt to AI: Explain how Python's `and` and `or` works when evaluating multiple conditions. Use a small example related to CampusFlow. explain why order of `if` statements matters when multiple conditions sould be true.


Useful AI guidance: It explained that: `and` evaluates to true when both conditions a true, `or` evaluates to true when at least on condition is true, Python evaluates `if` and `elif` conditions in order, whan a matching branch executes, subsequent `elif` branches are skipped, a function stops executing when it encounters `return`.


My independent experiment/test: I created a file called `logic_experiment` and ran:


age = 20
has_id = True

if age >= 18 and has_id:
    print("Access granted")
else:
    print("Access denied")

temperature = 35
is_sunny = False

if temperature >= 30 or is_sunny:
    print("Hot or sunny weather")
else:
    print("Normal weather")


Verification source or result:


`Access granted`
`Hot or sunny weather`


Decision: I accepted the explanation of logical operators because it is consistent with the Python's documented behaviour.


Related file/commit: `campusflow/tickets.py` and `tests/test_tickets.py` related function is `calculate_priority()`


What I can now explain without AI: The `and` operator checks whether two conditions are both true, while `or` checks whether at least one condition is true.




## Fellow: Onminyi Andrew Okala
### Interaction #1 — Evaluating AI Guidance Input Validation


Problem: I needed to understand how Python validates integer values and why `isinstance()` might not be sufficient when validating the number of affected users in CampusFlow.


My initial understanding: I understood that `isinstance()` checks whether a value belongs to a particular data type.

Prompt to AI: Explain the difference between `isinstance(value, int)` and `type(value) is int` in Python, Use small unrelated example involving input validation. explain whether booleans can pass integer validation and how I can independently verify the behaviour.


Useful AI guidance: AI explained that Python's `bool` type inherits from `int`, therefore `isinstance(True, int)` returns `True`, However: `type(True) is int` returns `False` This distinction matters because CampusFlow requires a positive integer representating the number of affected users. Although `True` behaves like integer `1` in some Python operations, it should not represent one affected user.


My independent experiment/test: I created a file called `validation_experiment.py` and Ran:


values = [10, 0, -5, 2.5, "10", True, False]


for value in values:
    print(
        repr(value),
        isinstance(value, int),
        type(value) is int
    )


Verification source or result: 


10 True True
0 True True
-5 True True
2.5 False False
'10' False False
True True False
False True False


Decision: using only `isinstance(affected_users, int)` is insufficient for CampusFlow because it accepts boolean values. I therefore prefer `type(affected_users) is in` combined with `affected_users > 0`. This approach rejects booleans, zero, negative numbers, decimals, and strings.


Related file/commit: `campusflow/tickets.py` and `tests/test_tickets.py` related function is `validate_ticket()`


What I can now explain without AI: In Python, boolean values are subclassess of integers. This means `isinstance(True, int)` returns `True`, even though `True` is a boolean.
