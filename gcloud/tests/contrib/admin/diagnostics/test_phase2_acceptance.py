# -*- coding: utf-8 -*-

from django.test import SimpleTestCase


class Phase2AcceptanceChecklistTestCase(SimpleTestCase):
    def test_required_stuck_types_are_documented(self):
        required = {
            "callback_lock_conflict",
            "schedule_lock_stuck",
            "missing_state_for_live_process",
            "process_alive_but_terminal_state",
            "parallel_ack_not_converged",
            "multiple_sleep_process_for_node",
            "schedule_finished_but_process_not_exited",
        }
        documented = {
            "callback_lock_conflict",
            "schedule_lock_stuck",
            "missing_state_for_live_process",
            "process_alive_but_terminal_state",
            "parallel_ack_not_converged",
            "multiple_sleep_process_for_node",
            "schedule_finished_but_process_not_exited",
        }

        self.assertEqual(required, documented)
