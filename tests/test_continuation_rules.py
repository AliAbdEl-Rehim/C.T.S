import unittest

from continuation_rules import (
    WatchState,
    continuation_score,
    continue_raw,
    fail_raw,
    failure_score,
    liquidity_arrives,
    liquidity_leaves,
    prior_impulse_up,
    prior_trend_up,
    setup_ready,
    signal_confidence,
    step_confirmed,
)


class ScoringTests(unittest.TestCase):
    def test_full_continuation_confluence_meets_default_threshold(self):
        score = continuation_score(True, True, True, True, True, True, True, True)
        self.assertEqual(score, 12)
        self.assertGreaterEqual(score, 7)
        self.assertEqual(signal_confidence(score), 95.0)

    def test_weak_continuation_without_break_is_rejected(self):
        score = continuation_score(False, True, True, True, False, False, False, True)
        self.assertEqual(score, 5)
        self.assertFalse(
            continue_raw(True, True, score, 0, 7, broke_and_held=False)
        )

    def test_failed_breakout_meets_default_fail_threshold(self):
        score = failure_score(True, True, False, True, True, True, False)
        self.assertEqual(score, 9)
        self.assertTrue(
            fail_raw(True, score, 3, 6, True, False, True, True)
        )

    def test_expiry_without_structure_does_not_force_fail(self):
        score = failure_score(False, False, False, False, False, False, False)
        self.assertEqual(score, 0)
        self.assertFalse(
            fail_raw(True, score, 0, 6, False, False, False, False)
        )

    def test_confidence_is_capped(self):
        self.assertEqual(signal_confidence(4), 70.0)
        self.assertEqual(signal_confidence(20), 95.0)


class SetupFilterTests(unittest.TestCase):
    def test_internal_boundary_never_starts_a_watch(self):
        self.assertFalse(setup_ready(True, True, True, "INTERNAL BOUNDARY"))

    def test_setup_requires_prior_rise_and_trend(self):
        self.assertTrue(setup_ready(True, True, True, "HANDOFF"))
        self.assertFalse(setup_ready(True, False, True, "HANDOFF"))
        self.assertFalse(setup_ready(True, True, False, "ACTIVATION"))
        self.assertFalse(setup_ready(False, True, True, "OVERLAP BUILD"))

    def test_impulse_needs_atr_expansion_from_swing_low(self):
        self.assertTrue(prior_impulse_up(110, 100, 104, 5.0, 0.80))
        self.assertFalse(prior_impulse_up(101, 100, 104, 5.0, 0.80))
        self.assertFalse(prior_impulse_up(110, 100, 112, 5.0, 0.80))

    def test_trend_stack_can_be_required(self):
        self.assertTrue(prior_trend_up(12, 11, 10, 13, True))
        self.assertFalse(prior_trend_up(10, 11, 12, 13, True))
        self.assertTrue(prior_trend_up(10, 11, 12, 13, False))

    def test_liquidity_roles(self):
        for role in ("ACTIVATION", "OVERLAP BUILD", "HANDOFF"):
            self.assertTrue(liquidity_arrives(role))
            self.assertFalse(liquidity_leaves(role))
        for role in ("DEACTIVATION", "OVERLAP RELEASE"):
            self.assertTrue(liquidity_leaves(role))
            self.assertFalse(liquidity_arrives(role))


class StateMachineTests(unittest.TestCase):
    def test_two_bar_continuation_requires_hold(self):
        state = WatchState()
        first = step_confirmed(
            state,
            setup=True,
            continue_is_raw=True,
            fail_is_raw=False,
            two_bar=True,
            hold_continue=True,
            hold_fail=False,
            confirm_window=8,
        )
        self.assertEqual(first, "NONE")
        self.assertTrue(state.pending_continue)

        second = step_confirmed(
            state,
            setup=False,
            continue_is_raw=True,
            fail_is_raw=False,
            two_bar=True,
            hold_continue=True,
            hold_fail=False,
            confirm_window=8,
        )
        self.assertEqual(second, "CONTINUE")
        self.assertFalse(state.watching)

    def test_two_bar_continuation_cancels_if_second_bar_gives_it_back(self):
        state = WatchState()
        step_confirmed(
            state,
            setup=True,
            continue_is_raw=True,
            fail_is_raw=False,
            two_bar=True,
            hold_continue=True,
            hold_fail=False,
            confirm_window=8,
        )
        second = step_confirmed(
            state,
            setup=False,
            continue_is_raw=False,
            fail_is_raw=False,
            two_bar=True,
            hold_continue=False,
            hold_fail=False,
            confirm_window=8,
        )
        self.assertEqual(second, "NONE")
        self.assertFalse(state.pending_continue)

    def test_single_bar_failure_can_print_immediately(self):
        state = WatchState()
        verdict = step_confirmed(
            state,
            setup=True,
            continue_is_raw=False,
            fail_is_raw=True,
            two_bar=False,
            hold_continue=False,
            hold_fail=True,
            confirm_window=8,
        )
        self.assertEqual(verdict, "FAIL")
        self.assertEqual(state.last_kind, "FAIL")

    def test_window_expiry_stays_silent(self):
        state = WatchState()
        verdicts = []
        for age in range(10):
            verdicts.append(
                step_confirmed(
                    state,
                    setup=age == 0,
                    continue_is_raw=False,
                    fail_is_raw=False,
                    two_bar=True,
                    hold_continue=False,
                    hold_fail=False,
                    confirm_window=8,
                )
            )
        self.assertEqual(set(verdicts), {"NONE"})
        self.assertFalse(state.watching)

    def test_continue_gate_blocks_when_liquidity_leaves(self):
        score = continuation_score(True, True, True, True, True, True, True, False)
        self.assertFalse(
            continue_raw(
                True,
                continue_gate=False,
                continue_score=score,
                fail_score=0,
                min_continue=7,
                broke_and_held=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
