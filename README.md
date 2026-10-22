# AIxTech crypto intel v0.25: paper-only trading information system

Advanced research harness for automated cryptocurrency **information** and paper strategy evaluation.
Builds on [kkzee92/aixtech-crypto-intel-v024](https://github.com/kkzee92/aixtech-crypto-intel-v024), prior versions, and the [zeekiankok92/aixtech-agent-harness-demo](https://github.com/zeekiankok92/aixtech-agent-harness-demo) style.

It does not place live orders, does not store exchange secrets, and is not financial advice.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![version](https://img.shields.io/badge/version-0.25.0-blue)
![mode](https://img.shields.io/badge/execution-paper%20only-orange)
![Licence](https://img.shields.io/badge/licence-MIT-green)

## Enhancements in v0.25

- Refined multi-factor strategies for all 8 asset classes with MACD proxy, StochRSI, multi-TF consistency filters.
- Adaptive confidence/sizing with stronger correlation and anomaly overlays.
- Expanded cyber/data security: additional redaction patterns (Discord, Telegram token proxies), triple-hash lineage simulation, advanced isolation checks.
- Updated architecture emphasizing zero-trust and per-asset-class risk.

## What it does

- Eight asset classes with refined multi-factor research rules including MACD/StochRSI/Ichimoku/ADX/Bollinger/VWAP.
- Multi-scale regime + volatility tier + advanced anomaly scoring + correlation gates + multi-TF.
- Signals with adaptive filters, then multi-gate risk.
- Paper-only with class costs; enhanced hash-chained audit with advanced lineage.
- Synthetic candles only. No network by default.

| Asset class | Enhanced research rule (v0.25) | Risk cap | Cost |
|---|---|---|---|
| Major | Multi-EMA + Ichimoku + ADX + Bollinger + Supertrend + VWAP + MACD + StochRSI + volume-delta + multi-TF + no RSI div; stand aside stress/high-vol/anomaly | 8% | 8 bps |
| Large-cap alt | Volume-delta + Bollinger breakout + multi-TF + ADX + MACD | 4% | 14 bps |
| Stablecoin | Adaptive peg + multi-stat + VWAP alerts only | 0% | n/a |
| DeFi | Calm multi-scale + Ichimoku + Supertrend + Bollinger + low anomaly + ADX + StochRSI + multi-TF | 2% | 22 bps |
| Meme | Qualified burst with volume-delta, StochRSI, multi-TF, short horizon | 0.5% | 45 bps |
| L2 | Multi-period RS + relative volume-delta + corr vs benchmark + ADX + VWAP + MACD + multi-TF | 3% | 16 bps |
| RWA | Slow Ichimoku/Bollinger low-vol trend; adaptive gap halt + ADX + multi-TF | 2% | 12 bps |
| Perpetual | Funding carry with adaptive drift, Supertrend/Ichimoku, low anomaly, VWAP, multi-TF | 2% | 10 bps |

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
PYTHONPATH=src python -m crypto_intel
```

## Controls

Paper-only. No live credentials. Class caps, adaptive confidence and sizing, kill switch, drawdown, statistical anomaly + correlation gates, hash-chained audit with advanced lineage, expanded redaction, PDPA tripwire, gitleaks. Zero-trust research design.

## Honesty

No live exchange connector. Scores describe synthetic fixtures. Not investment, legal, or compliance advice. Research only.
