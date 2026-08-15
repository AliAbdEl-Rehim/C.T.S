# STRAT ULTRA PRO v3.2

TradingView Pine Script v6 indicator that prints **LONG** and **SHORT** entry signals from STRAT patterns, trap bars, liquidity sweeps, and EMA pullbacks.

Copy `STRAT_ULTRA_PRO.pine` into TradingView → Pine Editor → Add to chart.

## Why v3.2

v3.1 Precision stacked every filter as a hard AND (full EMA stack + 4H + fast MTF + OB/FVG/sweep + ADX + volume + FTC + RSI zone + confirmation). Almost no entries printed.

v3.2 uses a **score-first** model:

- Several independent entry engines can fire
- Confidence / confluence are thresholds, not a wall of vetoes
- Confirmation is off by default (signal prints on the closed bar)
- Trap bars no longer block a valid STRAT trigger on the same bar

## Signal Profile (first input)

| Profile | What you get |
|---|---|
| **More Signals** | Frequent LONG/SHORT, light filters |
| **Balanced** (default) | Regular signals with trend + quality score |
| **Precision** | Fewer, stricter setups |
| **Custom** | Uses the filter / MTF / SMC checkboxes as written |

Need more arrows: set **Signal Profile = More Signals**.  
Need fewer: **Precision**, or raise Minimum Confidence in Custom.

## What prints on the chart

- Green **LONG** / red **SHORT** arrow + label (or شراء / بيع if language = AR)
- Setup labels for STRAT 2-1-2, 3-2, RevStrat, etc.
- Optional EMA 21 / 50 / 200, order blocks, FVGs, swing points
- SL / TP1 / TP2 / TP3 lines while a trade is active
- Dashboard: trend, ADX/RSI, win rate, confidence, confluence, quality

## Alerts

Create a TradingView alert on this indicator:

- `ULTRA Long` / `ULTRA Short` — entries
- `ULTRA Any Entry` — either side
- `ULTRA Setup Long` / `ULTRA Setup Short` — pattern setups before the trigger

JSON and text alert payloads are supported.

## Suggested starting settings

1. Timeframe: 15m, 1H, or 4H
2. Signal Profile: **Balanced**
3. Entry Engines: **All Engines**
4. Require Next-Bar Confirmation: **off**
5. Turn **Show Blocked-Signal Reasons** on if you want to see why a bar was skipped
