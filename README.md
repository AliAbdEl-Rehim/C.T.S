# STRAT indicators (Pine v6)

TradingView overlays. Copy a `.pine` file into TradingView → Pine Editor → **Save** → Add to chart.

| File | Version | Use when |
|---|---|---|
| **`STRAT_PRO.pine`** | **3.1.0 Signal First** | **Use this.** Visible BUY / SELL arrows from STRAT + trap + sweep + continuation |
| `STRAT_Trap_VWAP_Engine.pine` | 2.1.0 IQ | Same signal-first fix on the v1.9 / Smart Mix core |
| `statistical_model.pine` | snippet | Historical pattern-matching section only (not a full indicator) |

## Why v3.0.1 / v2.0 printed nothing

The compile-clean scripts still hid arrows behind a **managed single trade** plus a wall of filters:

1. No arrow unless `Trade Engine` was on **and** the book was flat
2. No `plotshape` BUY/SELL — only easy-to-miss labels, capped by FIFO
3. PVTE default ON + Neutral = **Block** (most bars are Neutral)
4. Confidence floor 60 / 52 while a naked STRAT/trap often scored ~30
5. `Require Structure Alignment` ON while the market had no BOS yet
6. In “Both” mode a trap bar took the slot, then failed filters, and **swallowed** a valid STRAT trigger

v3.1.0 / v2.1.0 fix that the same way STRAT ULTRA v3.2 did: **signal first, trade optional**.

## STRAT PRO v3.1.0 — copy this file

Defaults are built to **print arrows**:

- Signal Profile = **More Signals** (floor 28)
- BUY / SELL `plotshape` on every engine fire
- Arrows print even if Trade Engine is off, and they keep printing while a trade is already open
- PVTE filter **OFF** (bands still draw); Neutral = **Allow** if you turn it on
- Structure alignment **OFF**
- Trap and trigger are scored independently; a passing STRAT trigger is not swallowed
- Extra engines: liquidity sweep reclaim, 2U / 2D continuation (EMA / RSI / structure agreement)
- 2-bar cooldown only — not a stack of AND-vetoes

| Profile | What you get |
|---|---|
| **More Signals** (default) | Frequent BUY/SELL, light gates |
| **Balanced** | Score ≥ 32 (the numeric input), uses the filter checkboxes |
| **Strict** | Score ≥ 50 + structure + PVTE |

Fewer arrows → **Strict**. Still quiet after Save? Turn **Show BUY / SELL Arrows** on and leave profile on More Signals.

SMC (BOS/CHoCH/FVG/OB), RSI divergence, killzones, SL/TP manager, and the v3.0.1 compiler fixes are unchanged.

## STRAT Trap IQ v2.1.0

Same signal-first behaviour on the IQ core. Default profile is **More Signals**. Smart Mix still scores trap + trigger + sweep reclaim + EMA pullback; trigger wins a tie so a trap cannot eat a valid break.

Turn **Smart Confluence Engine** OFF to recover the v1.9 path — triggers still print arrows even while a trade is open.

## Suggested starting settings (PRO)

1. Timeframe: 15m, 1H, or 4H
2. Signal Profile: **More Signals**
3. Entry Mode: **Both**
4. Show BUY / SELL Arrows: **ON**
5. Trade Engine: ON if you want SL/TP lines; OFF if you only want arrows
6. After you see prints, move to **Balanced** if you want fewer, cleaner ones

## Chart

- Green **BUY** / red **SELL** labels on the bar (plus pattern + score text)
- STRAT 1 / 2 / 3 bar numbers, EMA 21 / 50 / 200, PVTE bands, anchored VWAP
- Order-block and FVG boxes, optional BOS/CHoCH
- SL / TP1 / TP2 / TP3 lines only while a managed trade is active
- Dashboard: last BUY/SELL, score, structure, PVTE, trade, stats

## Alerts

Create a TradingView alert on the indicator with condition **Any alert() function call**, or use:

- `STRAT PRO: BUY` / `STRAT PRO: SELL` / `STRAT PRO: BUY or SELL`
- `STRAT PRO: Trade Opened` / `TP Hit` / `Trade Closed`
- Setup / Triggered Bull/Bear/Any

IQ uses the `STRAT: BUY` / `STRAT: SELL` names.

## Honesty notes

- All signals fire on **bar close** (no intrabar repaint on the signal layer)
- FTC alignment uses the **forming** higher-TF bar and can change until that HTF bar closes
- Stats / pattern memory reset on chart reload
- Win = TP1 touched (optimistic same-bar TP-priority model)
- This is a signal engine, not a broker. Size risk yourself.

Pine cannot be compiled in this environment. After paste: Pine Editor → Save. If TradingView still shows an old version, remove the indicator from the chart and add it again so the new defaults load.
