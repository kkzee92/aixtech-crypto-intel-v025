"""Simple entrypoint demo for paper-only crypto intel v0.25."""

from crypto_intel.strategies import signal_for
from crypto_intel.models import Candle, AssetClass

def demo():
    # Synthetic candles for major
    candles = [
        Candle("BTC", AssetClass.MAJOR, 60000, 60500, 59800, 60200, 1000),
        Candle("BTC", AssetClass.MAJOR, 60200, 60800, 60100, 60600, 1200),
        # ... more would be generated in real fixtures
    ]
    # Pad for demo
    base = candles[-1]
    for i in range(30):
        candles.append(Candle("BTC", AssetClass.MAJOR, base.close, base.close*1.01, base.close*0.99, base.close*1.002, 1100, 0.0))
        base = candles[-1]
    sig = signal_for(candles)
    print(f"Demo signal: {sig.side.value} conf={sig.confidence} size={sig.size_fraction} reason={sig.reason[:80]}...")

if __name__ == "__main__":
    demo()
