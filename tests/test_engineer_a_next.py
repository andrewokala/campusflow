"""Engineer A regression and safety tests for CampusFlow Next."""
import copy
import json
import os
import tempfile
import unittest
from campusflow.tickets import create_ticket
from campusflow.notes import add_note, next_note_id
from campusflow.workflow import assign_ticket, change_status, reopen_ticket
from campusflow.storage import load_tickets, save_tickets


class TestEngineerANext(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, 'Wi-Fi down', 'Network', 'high', 12)

    def test_new_ticket_has_empty_notes(self):
        self.assertEqual(self.tickets[0]['notes'], [])

    def test_unassigned_cannot_start_and_state_unchanged(self):
        before = copy.deepcopy(self.tickets)
        with self.assertRaises(ValueError):
            change_status(self.tickets, 'T001', 'in_progress')
        self.assertEqual(self.tickets, before)

    def test_resolved_assignment_rejected_without_mutation(self):
        assign_ticket(self.tickets, 'T001', 'Ada')
        change_status(self.tickets, 'T001', 'in_progress')
        change_status(self.tickets, 'T001', 'resolved')
        before = copy.deepcopy(self.tickets)
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, 'T001', 'Grace')
        self.assertEqual(self.tickets, before)

    def test_invalid_users_do_not_mutate(self):
        for bad in (0, -1, 1.2, True, '2'):
            before = copy.deepcopy(self.tickets)
            with self.assertRaises(ValueError):
                create_ticket(self.tickets, 'Problem', 'Other', 'low', bad)
            self.assertEqual(self.tickets, before)

    def test_note_ids_and_reopen(self):
        self.assertEqual(add_note(self.tickets, 'T001', 'Ada', 'Checking router')['note_id'], 'N001')
        assign_ticket(self.tickets, 'T001', 'Ada')
        change_status(self.tickets, 'T001', 'in_progress')
        change_status(self.tickets, 'T001', 'resolved')
        before = copy.deepcopy(self.tickets)
        with self.assertRaises(ValueError):
            add_note(self.tickets, 'T001', 'Ada', 'Checking again')
        self.assertEqual(self.tickets, before)
        reopen_ticket(self.tickets, 'T001')
        self.assertEqual(add_note(self.tickets, 'T001', 'Ada', 'Checking again')['note_id'], 'N002')

    def test_invalid_note_does_not_consume_id(self):
        for bad in ('abc', ' ', 'x' * 301):
            before = copy.deepcopy(self.tickets)
            with self.assertRaises(ValueError):
                add_note(self.tickets, 'T001', 'Ada', bad)
            self.assertEqual(self.tickets, before)
        self.assertEqual(next_note_id(self.tickets[0]), 'N001')

    def test_reload_preserves_notes_and_next_ids(self):
        add_note(self.tickets, 'T001', 'Ada', 'Checking router')
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'tickets.json')
            save_tickets(self.tickets, path)
            loaded = load_tickets(path)
        self.assertEqual(loaded[0]['notes'][0]['note_id'], 'N001')
        self.assertEqual(add_note(loaded, 'T001', 'Ada', 'Testing cables')['note_id'], 'N002')
        self.assertEqual(create_ticket(loaded, 'Laptop issue', 'Hardware', 'low', 1)['id'], 'T002')

    def test_duplicate_note_ids_rejected(self):
        note = add_note(self.tickets, 'T001', 'Ada', 'Checking router')
        self.tickets[0]['notes'].append(copy.deepcopy(note))
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                save_tickets(self.tickets, os.path.join(d, 'tickets.json'))

    def test_corrupt_load_does_not_change_memory(self):
        before = copy.deepcopy(self.tickets)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'tickets.json')
            with open(path, 'w') as f:
                f.write('{broken')
            with self.assertRaises(ValueError):
                load_tickets(path)
        self.assertEqual(self.tickets, before)

    def test_inconsistent_priority_rejected(self):
        self.tickets[0]['priority'] = 'low'
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                save_tickets(self.tickets, os.path.join(d, 'tickets.json'))
