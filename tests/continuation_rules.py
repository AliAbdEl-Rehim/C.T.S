"""Pure-Python mirror of the MktHandoff rise-continuation scoring rules.

These functions stay aligned with f_continuationScore, f_failureScore,
f_signalConfidence, f_liquidityArrives, f_liquidityLeaves, and the
confirmed-bar state machine in mkt_handoff.pine.
"""

from __future__ import annotations

from dataclasses import dataclass


def liquidity_arrives(role: str) -> bool:
    return role in {"ACTIVATION", "OVERLAP BUILD", "HANDOFF"} or role == "STRUCTURE PULLBACK"


def liquidity_leaves(role: str) -> bool:
    return role in {"DEACTIVATION", "OVERLAP RELEASE"}


def continuation_score(
    broke_and_held: bool,
    quality_bull: bool,
    trend_hold: bool,
    fast_hold: bool,
    rsi_supportive: bool,
    macd_supportive: bool,
    volume_supportive: bool,
    liquidity_arrives_flag: bool,
) -> int:
    score = 0
    if broke_and_held:
        score += 3
    if quality_bull:
        score += 2
    if trend_hold:
        score += 1
    if fast_hold:
        score += 1
    if rsi_supportive:
        score += 1
    if macd_supportive:
        score += 1
    if volume_supportive:
        score += 1
    if liquidity_arrives_flag:
        score += 2
    return score


def failure_score(
    failed_breakout: bool,
    lost_mid_trend: bool,
    lost_watch_low: bool,
    reject_wick: bool,
    bearish_candle: bool,
    macd_fading: bool,
    liquidity_leaves_flag: bool,
) -> int:
    score = 0
    if failed_breakout:
        score += 3
    if lost_mid_trend:
        score += 2
    if lost_watch_low:
        score += 3
    if reject_wick:
        score += 2
    if bearish_candle:
        score += 1
    if macd_fading:
        score += 1
    if liquidity_leaves_flag:
        score += 2
    return score


def signal_confidence(score: int) -> float:
    return min(50.0 + float(score) * 5.0, 95.0)


def prior_impulse_up(
    close_prev: float,
    swing_low_prev: float,
    close_lookback: float,
    atr_prev: float,
    impulse_atr_mult: float = 0.35,
    require_net_rise: bool = False,
) -> bool:
    atr_ok = atr_prev == atr_prev and swing_low_prev == swing_low_prev
    rise_ok = (close_prev - swing_low_prev) >= impulse_atr_mult * atr_prev
    net_ok = (not require_net_rise) or close_prev > close_lookback
    return atr_ok and rise_ok and net_ok


def volume_supportive(volume, volume_average, require: bool) -> bool:
    if not require:
        return True
    if volume is None or volume_average is None or volume_average <= 0:
        return True
    return volume > volume_average


def boundary_during_bar(state_at_open_minus, state_at_close_minus) -> bool:
    return state_at_open_minus != state_at_close_minus


def prior_trend_up(
    ema_fast_prev: float,
    ema_mid_prev: float,
    ema_slow_prev: float,
    close_prev: float,
    require_stack: bool = True,
) -> bool:
    stack_ok = (not require_stack) or (
        ema_fast_prev > ema_mid_prev and ema_mid_prev > ema_slow_prev
    )
    return stack_ok and close_prev > ema_mid_prev


def setup_ready(
    boundary_bar: bool,
    prior_trend: bool,
    prior_impulse: bool,
    role: str,
    structure_pullback: bool = False,
    already_watching: bool = False,
) -> bool:
    if not prior_trend or not prior_impulse:
        return False
    if boundary_bar and role != "INTERNAL BOUNDARY":
        return True
    return structure_pullback and not already_watching and not boundary_bar


def continue_raw(
    in_window: bool,
    continue_gate: bool,
    continue_score: int,
    fail_score: int,
    min_continue: int,
    broke_and_held: bool,
) -> bool:
    return (
        in_window
        and continue_gate
        and continue_score >= min_continue
        and continue_score > fail_score
        and broke_and_held
    )


def fail_raw(
    in_window: bool,
    fail_score: int,
    continue_score: int,
    min_fail: int,
    failed_breakout: bool,
    lost_watch_low: bool,
    lost_mid_trend: bool,
    bearish_candle: bool,
) -> bool:
    structural_fail = failed_breakout or lost_watch_low or (
        lost_mid_trend and bearish_candle
    )
    return (
        in_window
        and fail_score >= min_fail
        and fail_score > continue_score
        and structural_fail
    )


@dataclass
class WatchState:
    watching: bool = False
    watch_age: int = 0
    pending_continue: bool = False
    pending_fail: bool = False
    pending_age: int = 0
    last_kind: str = "NONE"


def step_confirmed(
    state: WatchState,
    *,
    setup: bool,
    continue_is_raw: bool,
    fail_is_raw: bool,
    two_bar: bool,
    hold_continue: bool,
    hold_fail: bool,
    confirm_window: int,
    expiry_fail: bool = True,
    saw_break_high: bool = False,
) -> str:
    """Advance one confirmed bar. Returns CONTINUE, FAIL, or NONE."""
    if setup:
        state.watching = True
        state.watch_age = 0
        state.pending_continue = False
        state.pending_fail = False
        state.pending_age = 0

    verdict = "NONE"
    if not state.watching:
        return verdict

    state.watch_age += 1

    if continue_is_raw and not state.pending_continue:
        if two_bar:
            state.pending_continue = True
            state.pending_fail = False
            state.pending_age = 0
        else:
            verdict = "CONTINUE"
    elif fail_is_raw and not state.pending_fail:
        if two_bar:
            state.pending_fail = True
            state.pending_continue = False
            state.pending_age = 0
        else:
            verdict = "FAIL"

    if state.pending_continue:
        state.pending_age += 1
        if state.pending_age >= 2:
            if hold_continue:
                verdict = "CONTINUE"
            state.pending_continue = False
            state.pending_age = 0
    elif state.pending_fail:
        state.pending_age += 1
        if state.pending_age >= 2:
            if hold_fail:
                verdict = "FAIL"
            state.pending_fail = False
            state.pending_age = 0

    if verdict != "NONE":
        state.watching = False
        state.pending_continue = False
        state.pending_fail = False
        state.last_kind = verdict
    elif state.watch_age > confirm_window and not state.pending_continue and not state.pending_fail:
        if expiry_fail and not saw_break_high:
            verdict = "FAIL"
            state.last_kind = "FAIL"
        state.watching = False

    return verdict
