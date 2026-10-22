"""Asset-class strategy research rules (v0.25).

Refined multi-factor heuristics with MACD proxy, StochRSI, multi-TF consistency, Bollinger/VWAP/Ichimoku/ADX for all classes. Paper research only.
Not forecasts.
"""

from __future__ import annotations

from statistics import fmean

from crypto_intel.models import AssetClass, Candle, Side, Signal
from crypto_intel.regime import Regime, VolatilityTier, anomaly_score, classify, volatility_tier

def _ema(values: list[float], span: int) -> float:
    alpha = 2.0 / (span + 1)
    value = values[0]
    for point in values[1:]:
        value = alpha * point + (1 - alpha) * value
    return value

def _macd_proxy(closes: list[float]) -> float:
    """Simple MACD histogram proxy."""
    if len(closes) < 26:
        return 0.0
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    return ema12 - ema26

def _stoch_rsi(closes: list[float], period: int = 14) -> float:
    """Stochastic RSI proxy (0-100)."""
    if len(closes) < period + 1:
        return 50.0
    rsi_vals = [_rsi(closes[-i-period:-i] if i > 0 else closes[-period:]) for i in range(period)]
    min_rsi = min(rsi_vals)
    max_rsi = max(rsi_vals)
    current_rsi = _rsi(closes)
    if max_rsi == min_rsi:
        return 50.0
    return 100 * (current_rsi - min_rsi) / (max_rsi - min_rsi)

def _bollinger(closes: list[float], span: int = 20, mult: float = 2.0) -> tuple[float, float, float]:
    mid = _ema(closes[-span:], span) if len(closes) >= span else _ema(closes, len(closes))
    std = (sum((x - mid)**2 for x in closes[-span:]) / max(span, 1))**0.5 if len(closes) >= span else 0.0
    return mid, mid + mult * std, mid - mult * std

def _vwap_proxy(candles: list[Candle], span: int = 14) -> float:
    window = candles[-span:]
    typical = [(c.high + c.low + c.close) / 3 for c in window]
    vols = [c.volume for c in window]
    return sum(t * v for t, v in zip(typical, vols)) / max(sum(vols), 1)

def _supertrend_proxy(candles: list[Candle], period: int = 10, mult: float = 3.0) -> bool:
    if len(candles) < period + 1:
        return True
    closes = [c.close for c in candles]
    atr = fmean([(c.high - c.low) for c in candles[-period:]])
    upper = _ema(closes, period) + mult * atr
    return closes[-1] > upper * 0.995

def _ichimoku_proxy(candles: list[Candle]) -> bool:
    if len(candles) < 26:
        return True
    closes = [c.close for c in candles]
    tenkan = (_ema(closes[-9:], 9) + fmean(closes[-9:])) / 2
    kijun = (_ema(closes[-26:], 26) + fmean(closes[-26:])) / 2
    return closes[-1] > max(tenkan, kijun)

def _adx_proxy(candles: list[Candle], period: int = 14) -> float:
    if len(candles) < period + 1:
        return 0.5
    ranges = [c.high - c.low for c in candles[-period:]]
    avg_range = fmean(ranges)
    moves = abs(candles[-1].close - candles[-period].close)
    return min(1.0, avg_range / max(moves, 0.001) * 0.1)

def _rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    gains = losses = 0.0
    for i in range(1, period + 1):
        diff = closes[-i] - closes[-i-1]
        if diff > 0:
            gains += diff
        else:
            losses -= diff
    rs = gains / max(losses, 0.001)
    return 100 - (100 / (1 + rs))

def _rsi_divergence(candles: list[Candle]) -> bool:
    if len(candles) < 20:
        return False
    closes = [c.close for c in candles]
    rsi_now = _rsi(closes)
    rsi_prev = _rsi(closes[:-5])
    price_higher = closes[-1] > closes[-6]
    return price_higher and rsi_now < rsi_prev - 5

def _volume_delta(candles: list[Candle], span: int = 5) -> float:
    window = candles[-span:]
    up_vol = sum(c.volume for c in window if c.close > c.open)
    down_vol = sum(c.volume for c in window if c.close < c.open)
    return (up_vol - down_vol) / max(up_vol + down_vol, 1)

def _multi_tf_momentum(candles: list[Candle]) -> bool:
    """Simple multi-TF consistency: short and medium positive."""
    if len(candles) < 20:
        return True
    closes = [c.close for c in candles]
    short = closes[-1] > closes[-5]
    medium = closes[-1] > closes[-14]
    return short and medium

def _correlation_proxy(candles: list[Candle], benchmark: list[Candle] | None) -> float:
    if not benchmark or len(candles) < 10 or len(benchmark) < 10:
        return 0.5
    c_rets = [candles[i].close / candles[i-1].close - 1 for i in range(1, min(10, len(candles)))]
    b_rets = [benchmark[i].close / benchmark[i-1].close - 1 for i in range(1, min(10, len(benchmark)))]
    if len(c_rets) != len(b_rets):
        return 0.5
    mean_c = fmean(c_rets)
    mean_b = fmean(b_rets)
    cov = fmean([(c - mean_c) * (b - mean_b) for c, b in zip(c_rets, b_rets)])
    return max(0.0, min(1.0, cov * 10 + 0.5))

def _base(candles: list[Candle], side: Side, confidence: float, reason: str, size: float, bars: int) -> Signal:
    last = candles[-1]
    regime = classify(candles)
    vol = volatility_tier(candles)
    anom = anomaly_score(candles)
    corr_factor = 0.65 if _correlation_proxy(candles, None) > 0.8 else 1.0
    adj_conf = confidence * (0.7 if anom > 0.6 else 1.0) * corr_factor
    adj_size = size * (0.35 if anom > 0.65 or vol is VolatilityTier.HIGH else 1.0)
    return Signal(
        symbol=last.symbol,
        asset_class=last.asset_class,
        side=side,
        confidence=round(max(0.0, min(adj_conf, 1.0)), 4),
        reason=f"{reason}; regime={regime.value}; vol={vol.value}; anom={anom:.2f}",
        stop_distance_pct=round(max(0.01, anom * 0.05), 4),
        size_fraction=round(max(0.0, adj_size), 4),
        horizon_bars=bars,
    )

def signal_for(candles: list[Candle], benchmark: list[Candle] | None = None) -> Signal:
    if len(candles) < 8:
        raise ValueError("need at least 8 candles")
    asset_class = candles[-1].asset_class
    closes = [c.close for c in candles]
    regime = classify(candles)
    vol = volatility_tier(candles)
    corr = _correlation_proxy(candles, benchmark)
    if asset_class is AssetClass.MAJOR:
        return _major(candles, closes, regime, vol, corr)
    if asset_class is AssetClass.LARGE_CAP_ALT:
        return _large_cap(candles, closes, regime, vol)
    if asset_class is AssetClass.STABLECOIN:
        return _stable(candles)
    if asset_class is AssetClass.DEFI:
        return _defi(candles, closes, regime, vol)
    if asset_class is AssetClass.MEME:
        return _meme(candles, closes, regime)
    if asset_class is AssetClass.L2:
        return _l2(candles, closes, regime, corr)
    if asset_class is AssetClass.RWA:
        return _rwa(candles, closes, regime, vol)
    if asset_class is AssetClass.PERPETUAL:
        return _perp(candles, closes, regime)
    return _base(candles, Side.FLAT, 0.4, f"{asset_class.value}: no specific rule", 0.0, 1)

def _major(candles: list[Candle], closes: list[float], regime: Regime, vol: VolatilityTier, corr: float) -> Signal:
    if regime is Regime.STRESS or anomaly_score(candles) > 0.65 or _rsi_divergence(candles) or not _multi_tf_momentum(candles):
        return _base(candles, Side.FLAT, 0.4, "major stress, high anomaly, RSI div or multi-TF fail: stand aside", 0.0, 1)
    st_up = _supertrend_proxy(candles)
    ichi = _ichimoku_proxy(candles)
    adx = _adx_proxy(candles)
    b_mid, _, _ = _bollinger(closes)
    vwap = _vwap_proxy(candles)
    vd = _volume_delta(candles)
    macd = _macd_proxy(closes)
    stoch = _stoch_rsi(closes)
    if st_up and ichi and adx > 0.4 and closes[-1] > b_mid and closes[-1] > vwap and vd > 0.1 and macd > 0 and stoch < 80 and corr < 0.75:
        return _base(candles, Side.LONG, 0.92, "major multi-factor: Ichimoku+ADX+Bollinger+VWAP+Supertrend+MACD+StochRSI+volume-delta+multi-TF, low corr", 0.07, 20)
    return _base(candles, Side.FLAT, 0.35, "major: no multi-factor edge", 0.0, 1)

def _large_cap(candles: list[Candle], closes: list[float], regime: Regime, vol: VolatilityTier) -> Signal:
    if regime is Regime.STRESS or anomaly_score(candles) > 0.6 or not _multi_tf_momentum(candles):
        return _base(candles, Side.FLAT, 0.35, "large-cap: stress, anomaly or multi-TF fail", 0.0, 1)
    _, b_upper, _ = _bollinger(closes)
    adx = _adx_proxy(candles)
    vd = _volume_delta(candles)
    macd = _macd_proxy(closes)
    if closes[-1] > b_upper and vd > 0.15 and adx > 0.35 and macd > 0:
        return _base(candles, Side.LONG, 0.78, "large-cap Bollinger breakout + volume-delta + ADX + MACD + multi-TF", 0.04, 12)
    return _base(candles, Side.FLAT, 0.4, "large-cap: no breakout", 0.0, 1)

def _stable(candles: list[Candle]) -> Signal:
    deviation = abs(candles[-1].close - 1.0)
    vwap = _vwap_proxy(candles)
    vwap_dev = abs(candles[-1].close - vwap)
    if deviation >= 0.005 or vwap_dev > 0.003:
        return _base(candles, Side.ALERT, 0.96, f"stablecoin depeg or VWAP dev: {deviation:.4f}", 0.0, 1)
    return _base(candles, Side.FLAT, 0.88, "stablecoin inside band", 0.0, 1)

def _defi(candles: list[Candle], closes: list[float], regime: Regime, vol: VolatilityTier) -> Signal:
    if regime is Regime.STRESS or vol is VolatilityTier.HIGH or anomaly_score(candles) > 0.55 or not _multi_tf_momentum(candles):
        return _base(candles, Side.FLAT, 0.3, "DeFi: stress/high-vol/anomaly/multi-TF fail", 0.0, 1)
    ichi = _ichimoku_proxy(candles)
    st_up = _supertrend_proxy(candles)
    b_mid, _, _ = _bollinger(closes)
    adx = _adx_proxy(candles)
    stoch = _stoch_rsi(closes)
    if ichi and st_up and closes[-1] > b_mid and adx > 0.3 and stoch < 75:
        return _base(candles, Side.LONG, 0.68, "DeFi calm trend with Ichimoku/Supertrend/Bollinger/ADX/StochRSI/multi-TF", 0.02, 15)
    return _base(candles, Side.FLAT, 0.4, "DeFi: no calm trend", 0.0, 1)

def _meme(candles: list[Candle], closes: list[float], regime: Regime) -> Signal:
    if regime is Regime.STRESS or anomaly_score(candles) > 0.7 or _rsi(closes) > 75 or _stoch_rsi(closes) > 85:
        return _base(candles, Side.FLAT, 0.25, "meme: extreme or stress", 0.0, 1)
    vd = _volume_delta(candles)
    if vd > 0.3 and _rsi(closes) < 70 and _multi_tf_momentum(candles):
        return _base(candles, Side.LONG, 0.58, "meme qualified volume-delta burst + multi-TF", 0.005, 3)
    return _base(candles, Side.FLAT, 0.3, "meme: no burst", 0.0, 1)

def _l2(candles: list[Candle], closes: list[float], regime: Regime, corr: float) -> Signal:
    if regime is Regime.STRESS or corr > 0.85 or not _multi_tf_momentum(candles):
        return _base(candles, Side.FLAT, 0.35, "L2: stress, high corr or multi-TF fail", 0.0, 1)
    adx = _adx_proxy(candles)
    vd = _volume_delta(candles)
    vwap = _vwap_proxy(candles)
    macd = _macd_proxy(closes)
    if adx > 0.35 and vd > 0.1 and closes[-1] > vwap and macd > 0:
        return _base(candles, Side.LONG, 0.72, "L2 relative strength + ADX + volume-delta + VWAP + MACD + multi-TF", 0.03, 16)
    return _base(candles, Side.FLAT, 0.4, "L2: no RS", 0.0, 1)

def _rwa(candles: list[Candle], closes: list[float], regime: Regime, vol: VolatilityTier) -> Signal:
    if regime is Regime.STRESS or vol is not VolatilityTier.LOW or anomaly_score(candles) > 0.5 or not _multi_tf_momentum(candles):
        return _base(candles, Side.FLAT, 0.3, "RWA: not low-vol calm or multi-TF fail", 0.0, 1)
    ichi = _ichimoku_proxy(candles)
    b_mid, _, _ = _bollinger(closes)
    adx = _adx_proxy(candles)
    if ichi and closes[-1] > b_mid and adx > 0.25:
        return _base(candles, Side.LONG, 0.62, "RWA slow Ichimoku/Bollinger trend + ADX + multi-TF", 0.02, 30)
    return _base(candles, Side.FLAT, 0.35, "RWA: no slow trend", 0.0, 1)

def _perp(candles: list[Candle], closes: list[float], regime: Regime) -> Signal:
    if regime is Regime.STRESS or anomaly_score(candles) > 0.6 or not _multi_tf_momentum(candles):
        return _base(candles, Side.FLAT, 0.3, "perp: stress/anomaly/multi-TF fail", 0.0, 1)
    funding = candles[-1].funding_rate
    ichi = _ichimoku_proxy(candles)
    st_up = _supertrend_proxy(candles)
    vwap = _vwap_proxy(candles)
    if funding < -0.0001 and ichi and st_up and closes[-1] > vwap:
        return _base(candles, Side.LONG, 0.70, "perp negative funding carry with alignment + multi-TF", 0.02, 10)
    return _base(candles, Side.FLAT, 0.4, "perp: no carry edge", 0.0, 1)
