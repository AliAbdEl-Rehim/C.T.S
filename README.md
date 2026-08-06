# C.T.S

## Sell Confluence Rules

`pine/Sell_Confluence_Rules.pine` — TradingView Pine v6 indicator.

Fires a **SELL** when any registered confluence rule is true within a lookback window.

### Sources
- **C1**: All-in-One PreBO (AdvDiv, Ichimoku B/HB/R1–R3/BO/BD, BSS Trend/Scalp/Breakout/PreBO/Early)
- **C2**: Buy/Sell Div Pro + EGX Boost (A++/A+/B, LIMIT, BURST, Early Buy/Sell, Trend/Scalp)

### Implemented rules
1–16, 19–23, 25, 27–32  
(Reserved for later: 17, 18, 24, 26)

### Usage
1. Open TradingView Pine Editor
2. Paste `pine/Sell_Confluence_Rules.pine`
3. Add to chart
4. Tune **Confluence Window** and enable/disable rules in settings
5. Create alert on `🔻 SELL Confluence`
