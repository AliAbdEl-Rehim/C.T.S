# STRAT Trap & VWAP Engine IQ v2.0

TradingView **Pine Script v6** overlay. Copy `STRAT_Trap_VWAP_Engine.pine` into TradingView → Pine Editor → Add to chart.

نسخة أذكى من محرك STRAT Trap: إشارات شراء/بيع تُفتح فقط عندما يتفق أكثر من محرك (STRAT + نظام + زخم + سيولة)، مع الإبقاء على منطق v1.9 عند إيقاف المحرك الذكي.

## What v2.0 adds

The v1.9 STRAT FSM, trap bars, PVTE regime, anchored VWAP, FTC strip, risk engine, and alerts are intact. Intelligence sits **on top** as a score-first gate — not a wall of AND-vetoes (that pattern killed entries in earlier Ultra builds).

| Layer | Role |
|---|---|
| **STRAT patterns** | 2-1-2, 3-2, 2-2 Rev/Cont, RevStrat, optional extended 2-2-2 / RJ / 3 RevStrat |
| **Trap bars** | Failed 2U (red) → SHORT, failed 2D (green) → LONG |
| **Smart Mix engines** | Trap + STRAT trigger + liquidity-sweep reclaim + EMA-21 pullback. Highest score wins; trap wins a tie |
| **12-factor score** | PVTE, EMA 21/50/200, MACD, RSI, Supertrend, ADX/DMI, Stochastic, Volume/OBV, FTC, session VWAP, SMC (OB/FVG/sweep/structure), pattern memory |
| **Grade** | A+ ≥80 · A ≥70 · B ≥60 · C ≥52 · D below. Labels show `LONG · 2-1-2 · 74% A` |
| **PVTE** | Still the hard regime filter by default (longs in BULL, shorts in BEAR) |
| **Risk** | Volatility-adaptive SL/TP, BE after TP1, chandelier trail after TP1 |

Turn **Smart Confluence Engine** OFF to recover the exact v1.9.0 entry path.

## Signal Profile (first thing to change)

| Profile | What you get |
|---|---|
| **More Signals** | Frequent arrows, light gates (confidence ≥ 40, confluence ≥ 1) |
| **Balanced** (default) | Soft EMA trend + score ≥ 52 + confluence ≥ 2. Regular, higher-quality prints |
| **Precision** | Full EMA stack, ADX, volume, FTC ≥ 2, chop block, location (OB/FVG/sweep), score ≥ 68 |
| **Custom** | Uses the numeric thresholds and filter checkboxes as written |

Need more arrows → **More Signals**. Need fewer, cleaner ones → **Precision**.

## Suggested starting settings

1. Timeframe: 15m, 1H, or 4H
2. Signal Profile: **Balanced**
3. Entry Mode: **Smart Mix**
4. Smart Confluence Engine: **ON**
5. PVTE Regime Filter: **ON**
6. Turn **Show Blocked-Signal Reasons** on if a chart looks quiet — gray `× Trend` / `× Conf 48` labels tell you why a bar was skipped

## Chart

- Green **LONG** / red **SHORT** (or شراء / بيع) with optional confidence grade. Gold label = A+ (≥80)
- STRAT 1 / 2 / 3 bar numbers, optional setup ▲/▼ labels
- EMA 21 / 50 / 200, Supertrend, session VWAP, PVTE bands, anchored VWAP
- Order-block and FVG boxes, optional swing SH/SL
- SL / TP1 / TP2 / TP3 lines while a trade is active (trail/BE annotated)
- Dashboard: Market, Intelligence (grade/confluence/RSI/MACD/ADX/VWAP/last gate), Trade, Stats

## Alerts

Create a TradingView alert on this indicator with condition **Any alert() function call**, or use the fixed dropdown:

- `STRAT: LONG` / `STRAT: SHORT` / `STRAT: Trade Opened`
- `STRAT: Setup Bull/Bear/Any`
- `STRAT: Triggered Bull/Bear/Any`
- `STRAT: TP Hit` / `STRAT: Trade Closed`

JSON payloads keep `ind: STRAT` for existing bots and add `conf`, `confl`, `grade`. Extra actions: `sweep_long`, `sweep_short`, `pull_long`, `pull_short`.

## Honesty notes (same as v1.9)

- All entries fire on **bar close** (no intrabar repaint on the trade layer)
- FTC alignment uses the **forming** higher-TF bar by design and can change until that HTF bar closes
- Stats / pattern memory reset on chart reload
- Win = TP1 touched (optimistic same-bar TP-priority model)
- This is a signal engine, not a broker. Size risk yourself.
