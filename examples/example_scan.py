"""
Example: Real-time Signal Scanning

Scans EURUSD and GBPUSD on the 4H timeframe for market structure signals
and prints any found signals as formatted JSON.

Run::

    python examples/example_scan.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_structure_bot.data.data_fetcher import DataFetcher
from market_structure_bot.data.data_processor import DataProcessor
from market_structure_bot.signals.signal_generator import SignalGenerator
from market_structure_bot.signals.json_exporter import JsonExporter


PAIRS = ["EURUSD", "GBPUSD", "USDJPY"]
TIMEFRAME = "4H"
PERIOD = "1y"


def scan_pair(pair: str, timeframe: str = TIMEFRAME):
    print(f"\n{'─'*50}")
    print(f"  Scanning {pair} – {timeframe}")
    print(f"{'─'*50}")

    fetcher = DataFetcher(pair, timeframe)
    try:
        raw = fetcher.fetch(PERIOD)
    except ValueError as e:
        print(f"  [SKIP] {e}")
        return

    processor = DataProcessor(raw)
    data = processor.process()

    generator = SignalGenerator(pair, timeframe)
    signals = generator.generate(data)

    if signals:
        count = len(signals)
        print(f"  Found {count} signal(s):")
        exporter = JsonExporter()
        exporter.to_stdout(signals)
    else:
        print("  No signals at this time.")


if __name__ == "__main__":
    print("Forex Market Structure Bot – Signal Scanner")
    print("=" * 50)
    for pair in PAIRS:
        scan_pair(pair)
    print("\nScan complete.")
