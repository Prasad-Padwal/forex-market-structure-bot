"""
Example: Run a Backtest

Runs a historical backtest of the market structure strategy on EURUSD 4H
data and prints performance metrics.

Run::

    python examples/example_backtest.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_structure_bot.data.data_fetcher import DataFetcher
from market_structure_bot.data.data_processor import DataProcessor
from market_structure_bot.backtest.backtester import Backtester
from market_structure_bot.backtest.metrics import Metrics


PAIR = "EURUSD"
TIMEFRAME = "4H"
PERIOD = "2y"
RR_TARGET = 2.0


def run_backtest(pair: str = PAIR, timeframe: str = TIMEFRAME):
    print(f"\nBacktest: {pair} {timeframe}  (period={PERIOD})")
    print("=" * 50)

    # 1. Fetch data
    fetcher = DataFetcher(pair, timeframe)
    try:
        raw = fetcher.fetch(PERIOD)
    except ValueError as e:
        print(f"[ERROR] Could not fetch data: {e}")
        return

    # 2. Process
    processor = DataProcessor(raw)
    data = processor.process()

    print(f"  Loaded {len(data)} bars.")

    # 3. Backtest
    backtester = Backtester(data, pair, timeframe, rr_target=RR_TARGET)
    trades = backtester.run()

    if not trades:
        print("  No trades generated.")
        return

    # 4. Metrics
    metrics = Metrics(trades)
    summary = metrics.summary()

    print(f"\n  Results for {pair} {timeframe}:")
    print(f"  {'─'*40}")
    for key, val in summary.items():
        if isinstance(val, float):
            print(f"  {key:<25}: {val:.4f}")
        else:
            print(f"  {key:<25}: {val}")

    # 5. Show sample trades
    trades_df = backtester.get_trades_df()
    print(f"\n  Sample trades (first 5):")
    print(trades_df.head().to_string(index=False))


if __name__ == "__main__":
    run_backtest()
