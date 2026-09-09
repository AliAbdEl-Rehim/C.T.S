"""Unit tests for early BUY A++ gating (mirrors bsdiv_egx_boost.pine)."""

from __future__ import annotations

import math
import unittest


def logit(p: float) -> float:
    denom = 1.0 - p + 0.0001
    return math.log(p / denom)


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def bullish_score(
    *,
    f1: float,
    f2: float,
    f3: float,
    f4: float,
    f5: float,
    f6: float,
    f7: float,
    f8: float,
    f_egx1: float,
    f_egx2: float,
    f_egx3: float,
    egx_burst_weight: float = 1.5,
    egx_limit_weight: float = 1.3,
    egx_accum_weight: float = 1.2,
) -> float:
    ll = (
        1.3 * logit(clamp(f1, 0.1, 0.9))
        + 1.2 * logit(clamp(f2, 0.1, 0.9))
        + 1.0 * logit(clamp(f3, 0.1, 0.9))
        + 0.8 * logit(clamp(f4, 0.1, 0.9))
        + 1.1 * logit(clamp(f5, 0.1, 0.9))
        + 1.4 * logit(clamp(f6, 0.1, 0.9))
        + 0.9 * logit(clamp(f7, 0.1, 0.9))
        + 1.0 * logit(clamp(f8, 0.1, 0.9))
        + egx_burst_weight * logit(clamp(f_egx1, 0.1, 0.9))
        + egx_limit_weight * logit(clamp(f_egx2, 0.1, 0.9))
        + egx_accum_weight * logit(clamp(f_egx3, 0.1, 0.9))
    )
    prob = 1.0 / (1.0 + math.exp(-(-0.50 + ll)))
    return clamp(prob, 0.05, 0.95)


def early_stat_votes(
    *,
    forming_div: bool = False,
    forming_div_stored: bool = False,
    bullish_divergence: bool = False,
    accum_building: bool = False,
    is_accumulating: bool = False,
    volume_building: bool = False,
    compressed_coil: bool = False,
    rsi_turning_up: bool = False,
    rsi_not_ob: bool = True,
    rsi: float = 40.0,
    stoch_turning_up: bool = False,
    stoch_oversoldish: bool = False,
    spring_candle: bool = False,
    macd_hist_rising: bool = False,
    buyers_in_control: bool = False,
) -> int:
    return (
        (2 if (forming_div or forming_div_stored) else 0)
        + (2 if bullish_divergence else 0)
        + (2 if (accum_building or is_accumulating) else 0)
        + (1 if volume_building else 0)
        + (1 if compressed_coil else 0)
        + (1 if ((rsi_turning_up and rsi_not_ob) or rsi < 45) else 0)
        + (1 if (stoch_turning_up or stoch_oversoldish) else 0)
        + (2 if spring_candle else 0)
        + (1 if macd_hist_rising else 0)
        + (1 if buyers_in_control else 0)
    )


def get_buy_tier(
    score: float,
    *,
    use_predictive: bool = True,
    high_prob_cutoff: float = 0.70,
    med_prob_cutoff: float = 0.50,
    predictive_cutoff: float = 0.70,
    has_multiple_conf: bool,
    has_stoch_conf: bool,
    has_vol_conf: bool,
    is_strong_bullish: bool,
    near_limit_up: bool,
    is_accumulating: bool,
    accum_ratio: float,
    is_pre_burst: bool,
    rsi_turning_up: bool,
    bullish_divergence: bool,
    forming_div: bool = False,
    early_stat_ready: bool = False,
    block_on_burst: bool = True,
    block_on_limit: bool = True,
    require_accum: bool = True,
    predictive_accum_min: float = 1.10,
) -> str:
    high_score = score >= high_prob_cutoff
    med_score = score >= med_prob_cutoff
    has_burst = is_strong_bullish
    has_limit = near_limit_up
    has_accum = is_accumulating
    classic_app = score >= 0.85 and has_multiple_conf and has_burst and (has_limit or has_accum)

    late_chase = (block_on_burst and is_strong_bullish) or (block_on_limit and near_limit_up)
    accum_ok = (not require_accum) or has_accum or accum_ratio >= predictive_accum_min
    live_div = bullish_divergence or forming_div
    setup_ok = is_pre_burst or early_stat_ready or (
        has_multiple_conf and (has_stoch_conf or has_vol_conf or rsi_turning_up)
    )
    score_ok = score >= predictive_cutoff or (early_stat_ready and score >= med_prob_cutoff)
    predictive_app = (
        use_predictive
        and (not late_chase)
        and score_ok
        and accum_ok
        and setup_ok
        and live_div
    )

    if predictive_app:
        return "A++"
    if (not use_predictive or not block_on_burst) and classic_app:
        return "A++"
    if high_score and has_multiple_conf and (has_stoch_conf or has_vol_conf or has_burst or is_pre_burst or early_stat_ready):
        return "A+"
    if high_score and (has_multiple_conf or has_stoch_conf or has_vol_conf or has_burst or is_pre_burst or early_stat_ready or live_div):
        return "A"
    if med_score:
        return "B"
    return "C"


class EarlyAPlusPlusTests(unittest.TestCase):
    def test_forming_div_and_early_votes_fire_a_plus_plus_without_full_rsi_pivot(self):
        """The late path waited for completed RSI/OBV HL. Early path uses forming divergence."""
        votes = early_stat_votes(
            forming_div=True,
            accum_building=True,
            volume_building=True,
            compressed_coil=True,
            spring_candle=True,
            macd_hist_rising=True,
            rsi=38.0,
        )
        self.assertGreaterEqual(votes, 5)
        score = bullish_score(
            f1=0.72,  # forming div, not completed RSI HL
            f2=0.70,
            f3=0.50,
            f4=0.58,
            f5=0.50,
            f6=0.72,
            f7=0.72,
            f8=0.55,
            f_egx1=0.76,
            f_egx2=0.25,
            f_egx3=0.68,
        )
        self.assertGreaterEqual(score, 0.50)
        tier = get_buy_tier(
            score,
            has_multiple_conf=False,
            has_stoch_conf=False,
            has_vol_conf=False,
            is_strong_bullish=False,
            near_limit_up=False,
            is_accumulating=False,
            accum_ratio=1.20,
            is_pre_burst=False,
            rsi_turning_up=False,
            bullish_divergence=False,
            forming_div=True,
            early_stat_ready=True,
        )
        self.assertEqual(tier, "A++")

    def test_full_divergence_still_fires_before_burst(self):
        score = 0.86
        tier = get_buy_tier(
            score,
            has_multiple_conf=True,
            has_stoch_conf=True,
            has_vol_conf=False,
            is_strong_bullish=False,
            near_limit_up=False,
            is_accumulating=True,
            accum_ratio=1.6,
            is_pre_burst=True,
            rsi_turning_up=True,
            bullish_divergence=True,
        )
        self.assertEqual(tier, "A++")

    def test_burst_and_limit_are_late_and_blocked(self):
        score = 0.93
        tier = get_buy_tier(
            score,
            has_multiple_conf=True,
            has_stoch_conf=True,
            has_vol_conf=True,
            is_strong_bullish=True,
            near_limit_up=True,
            is_accumulating=True,
            accum_ratio=2.0,
            is_pre_burst=False,
            rsi_turning_up=True,
            bullish_divergence=True,
            forming_div=True,
            early_stat_ready=True,
        )
        self.assertNotEqual(tier, "A++")
        self.assertIn(tier, {"A+", "A"})

    def test_classic_mode_still_allows_late_burst_a_plus_plus(self):
        score = 0.90
        tier = get_buy_tier(
            score,
            use_predictive=False,
            has_multiple_conf=True,
            has_stoch_conf=True,
            has_vol_conf=True,
            is_strong_bullish=True,
            near_limit_up=True,
            is_accumulating=True,
            accum_ratio=2.0,
            is_pre_burst=False,
            rsi_turning_up=True,
            bullish_divergence=True,
        )
        self.assertEqual(tier, "A++")

    def test_no_divergence_and_no_forming_cannot_be_a_plus_plus(self):
        tier = get_buy_tier(
            0.90,
            has_multiple_conf=True,
            has_stoch_conf=True,
            has_vol_conf=True,
            is_strong_bullish=False,
            near_limit_up=False,
            is_accumulating=True,
            accum_ratio=1.8,
            is_pre_burst=True,
            rsi_turning_up=True,
            bullish_divergence=False,
            forming_div=False,
            early_stat_ready=True,
        )
        self.assertNotEqual(tier, "A++")

    def test_spring_candle_is_not_a_green_burst(self):
        """Hammer/spring (close can still be red) counts 2 early votes; burst candle does not."""
        votes = early_stat_votes(spring_candle=True, forming_div=True, accum_building=True)
        self.assertGreaterEqual(votes, 5)
        self.assertEqual(early_stat_votes(spring_candle=False, forming_div=True, accum_building=True), votes - 2)

    def test_forming_div_boosts_score_vs_no_div(self):
        with_form = bullish_score(
            f1=0.72, f2=0.70, f3=0.25, f4=0.58, f5=0.50, f6=0.72, f7=0.72, f8=0.55,
            f_egx1=0.76, f_egx2=0.25, f_egx3=0.68,
        )
        without = bullish_score(
            f1=0.25, f2=0.25, f3=0.25, f4=0.40, f5=0.50, f6=0.50, f7=0.50, f8=0.20,
            f_egx1=0.25, f_egx2=0.25, f_egx3=0.25,
        )
        self.assertGreater(with_form, without)


if __name__ == "__main__":
    unittest.main()
