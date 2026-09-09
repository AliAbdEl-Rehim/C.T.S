"""Unit tests for predictive BUY A++ gating (mirrors bsdiv_egx_boost.pine)."""

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


def get_buy_tier(
    score: float,
    *,
    use_predictive: bool = True,
    high_prob_cutoff: float = 0.70,
    med_prob_cutoff: float = 0.50,
    predictive_cutoff: float = 0.75,
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
    block_on_burst: bool = True,
    block_on_limit: bool = True,
    require_accum: bool = True,
    predictive_accum_min: float = 1.15,
) -> str:
    high_score = score >= high_prob_cutoff
    med_score = score >= med_prob_cutoff
    has_burst = is_strong_bullish
    has_limit = near_limit_up
    has_accum = is_accumulating
    classic_app = score >= 0.85 and has_multiple_conf and has_burst and (has_limit or has_accum)

    late_chase = (block_on_burst and is_strong_bullish) or (block_on_limit and near_limit_up)
    accum_ok = (not require_accum) or has_accum or accum_ratio >= predictive_accum_min
    pre_quality = has_multiple_conf and accum_ok and (
        has_stoch_conf or has_vol_conf or is_pre_burst or rsi_turning_up
    )
    predictive_app = (
        use_predictive
        and (not late_chase)
        and score >= predictive_cutoff
        and pre_quality
        and bullish_divergence
    )

    if predictive_app:
        return "A++"
    if (not use_predictive or not block_on_burst) and classic_app:
        return "A++"
    if high_score and has_multiple_conf and (has_stoch_conf or has_vol_conf or has_burst or is_pre_burst):
        return "A+"
    if high_score and (has_multiple_conf or has_stoch_conf or has_vol_conf or has_burst or is_pre_burst):
        return "A"
    if med_score:
        return "B"
    return "C"


class PredictiveAPlusPlusTests(unittest.TestCase):
    def test_pre_burst_divergence_reaches_score_cutoff_without_explosion(self):
        score = bullish_score(
            f1=0.85,  # price LL + RSI HL
            f2=0.80,  # price LL + OBV HL
            f3=0.75,  # stoch oversold + divergence
            f4=0.58,  # volume building
            f5=0.50,  # sideways
            f6=0.85,  # RSI+OBV aligned
            f7=0.72,  # compressed coil
            f8=0.80,  # 3+ confirms
            f_egx1=0.82,  # pre-burst, not full burst
            f_egx2=0.25,  # not near limit
            f_egx3=0.68,  # accumulation building
        )
        self.assertGreaterEqual(score, 0.75)
        self.assertLess(score, 0.99)

    def test_predictive_a_plus_plus_fires_before_burst(self):
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

    def test_no_divergence_cannot_be_a_plus_plus(self):
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
        )
        self.assertNotEqual(tier, "A++")

    def test_score_below_cutoff_is_not_a_plus_plus(self):
        tier = get_buy_tier(
            0.70,
            has_multiple_conf=True,
            has_stoch_conf=True,
            has_vol_conf=True,
            is_strong_bullish=False,
            near_limit_up=False,
            is_accumulating=True,
            accum_ratio=1.8,
            is_pre_burst=True,
            rsi_turning_up=True,
            bullish_divergence=True,
        )
        self.assertNotEqual(tier, "A++")
        self.assertEqual(tier, "A+")

    def test_building_accum_below_full_threshold_still_qualifies(self):
        tier = get_buy_tier(
            0.80,
            has_multiple_conf=True,
            has_stoch_conf=False,
            has_vol_conf=False,
            is_strong_bullish=False,
            near_limit_up=False,
            is_accumulating=False,
            accum_ratio=1.20,
            is_pre_burst=True,
            rsi_turning_up=True,
            bullish_divergence=True,
        )
        self.assertEqual(tier, "A++")


if __name__ == "__main__":
    unittest.main()
