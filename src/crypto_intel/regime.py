"""Regime, volatility, and anomaly helpers (v0.25)."""

from __future__ import annotations

from enum import Enum
from statistics import fmean, pstdev

from crypto_intel.models import Candle

class Regime(str, Enum):
    TREND = "trend"
    RANGE = "range"
    STRESS = "stress"

class VolatilityTier(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

def classify(candles: list[Candle]) -> Regime:
    if len(candles) < 8:
        return Regime.RANGE
    closes = [c.close for c in candles]
    move = abs(closes[-1] / closes[-8] - 1.0)
    ranges = [(c.high - c.low) / c.close for c in candles[-8:] if c.close]
    avg_range = fmean(ranges) if ranges else 0.0
    if avg_range >= 0.035:
        return Regime.STRESS
    if move >= 0.025:
        return Regime.TREND
    return Regime.RANGE

def volatility_tier(candles: list[Candle]) -> VolatilityTier:
    ranges = [(c.high - c.low) / c.close for c in candles[-14:] if c.close]
    avg = fmean(ranges) if ranges else 0.0
    if avg < 0.015:
        return VolatilityTier.LOW
    if avg > 0.04:
        return VolatilityTier.HIGH
    return VolatilityTier.NORMAL

def anomaly_score(candles: list[Candle]) -> float:
    if len(candles) < 10:
        return 0.0
    closes = [c.close for c in candles[-20:]]
    rets = [closes[i] / closes[i-1] - 1.0 for i in range(1, len(closes))]
    if not rets:
        return 0.0
    std = pstdev(rets)
    extremes = sum(1 for r in rets if abs(r) > 3 * std)
    # Volume-price divergence proxy
    vols = [c.volume for c in candles[-10:]]
    price_up = closes[-1] > closes[-5]
    vol_down = fmean(vols[-5:]) < fmean(vols[:5]) if len(vols) >= 10 else False
    div = 0.3 if price_up and vol_down else 0.0
    # Multi-TF inconsistency proxy
    multi_tf_fail = 0.2 if len(candles) > 14 and not (closes[-1] > closes[-5] and closes[-1] > closes[-14]) else 0.0
    return min(1.0, extremes / max(len(rets), 1) * 2.5 + div + multi_tf_fail)
