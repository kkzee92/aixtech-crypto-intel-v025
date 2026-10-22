# Asset-class strategy notes (v0.25)

Research heuristics with MACD proxy, StochRSI, multi-TF consistency, Ichimoku, ADX, RSI divergence, Bollinger/VWAP for all classes. Not forecasts.

Regime: trend / range / stress. Volatility tier: low/normal/high. Anomaly score includes kurtosis, volume-price divergence. Correlation proxy and multi-TF for portfolio gates.

## Major

Hypothesis: Liquid majors trend with multi-factor alignment outside stress/high anomaly/RSI divergence/multi-TF fail, low correlation.
Entry: Ichimoku up, ADX > 0.4, Supertrend up, price above Bollinger mid and VWAP, positive MACD, StochRSI < 80, positive volume-delta, multi-TF consistent, no RSI div, corr < 0.75.
Invalidation: Stress, high anomaly, RSI divergence, multi-TF fail, or Supertrend flip.
Horizon: 20 bars. Cap 8%. Cost 8 bps.

## Large-cap alt

Hypothesis: Breakouts need volume-delta confirmation, multi-TF, ADX, MACD outside stress.
Entry: Close above Bollinger upper, volume-delta > threshold, multi-TF positive, ADX support, MACD > 0.
Cap 4%. Cost 14 bps.

## Stablecoin

Hypothesis: Statistical multi-metric peg deviation (z, consecutive, skew, kurtosis, VWAP).
Alerts only. Size zero.

## DeFi

Hypothesis: Trend only in calm non-stress with Ichimoku, Supertrend, Bollinger, ADX, StochRSI, multi-TF, low anomaly.
Cap 2%. Cost 22 bps.

## Meme

Hypothesis: Qualified bursts with volume-delta consistency, StochRSI filter, multi-TF, RSI not extreme.
Hard 3-bar horizon. Cap 0.5%. Cost 45 bps.

## L2

Hypothesis: Multi-period relative strength with volume-delta, ADX, VWAP, MACD, correlation vs non-stress benchmark, multi-TF.
Cap 3%. Cost 16 bps.

## RWA

Hypothesis: Slow Ichimoku/Bollinger trend; halt on adaptive gap or stress; ADX and multi-TF confirmation.
Cap 2%. Cost 12 bps.

## Perpetual

Hypothesis: Negative funding with contained drift, Supertrend/Ichimoku alignment, low anomaly, VWAP, multi-TF.
Cap 2%. Cost 10 bps.

Out of scope: live orders, trade keys, future return claims.
