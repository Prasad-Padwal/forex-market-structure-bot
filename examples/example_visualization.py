"""
Example: Chart Visualization with Market Structure Zones

Plots a candlestick chart for EURUSD 4H with SBR, A+/QML, and DT/DB
zones overlaid.

Run::

    python examples/example_visualization.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend; change to "TkAgg" for GUI

from market_structure_bot.data.data_fetcher import DataFetcher
from market_structure_bot.data.data_processor import DataProcessor
from market_structure_bot.strategy.market_structure import MarketStructure
from market_structure_bot.strategy.levels import Levels
from market_structure_bot.visualization.chart_plotter import ChartPlotter
from market_structure_bot.visualization.zone_markers import ZoneMarkers


PAIR = "EURUSD"
TIMEFRAME = "4H"
PERIOD = "6mo"
OUTPUT_FILE = "eurusd_4h_zones.png"


def visualize(pair: str = PAIR, timeframe: str = TIMEFRAME):
    print(f"\nVisualising {pair} {timeframe} …")

    # 1. Fetch & process
    fetcher = DataFetcher(pair, timeframe)
    try:
        raw = fetcher.fetch(PERIOD)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    processor = DataProcessor(raw)
    data = processor.process()

    print(f"  {len(data)} bars loaded.")

    # 2. Market structure
    ms = MarketStructure(data, swing_lookback=5)
    structure = ms.identify_structure()
    print(f"  Trend: {structure['trend']}")
    print(f"  Support levels:    {[round(x, 5) for x in structure['support_levels'][:5]]}")
    print(f"  Resistance levels: {[round(x, 5) for x in structure['resistance_levels'][:5]]}")

    # 3. Calculate zones
    direction = "bearish" if structure["trend"] in ("bearish", "sideways") else "bullish"
    levels_engine = Levels(data)
    all_levels = levels_engine.get_all_levels(structure["support_levels"], direction)

    for zone_name, zone_data in all_levels.items():
        if zone_data:
            print(f"  {zone_name:<12}: {zone_data['price']:.5f}  "
                  f"[{zone_data['lower']:.5f} – {zone_data['upper']:.5f}]")

    # 4. Plot
    plotter = ChartPlotter(data, pair, timeframe)
    plotter.plot_base_chart()
    plotter.add_support_resistance(
        structure["support_levels"][:10],
        structure["resistance_levels"][:10],
    )

    zone_markers = ZoneMarkers(plotter.ax, len(data))
    zone_markers.add_all_zones(all_levels)

    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    plotter.save(output_path)
    print(f"\n  Chart saved → {output_path}")


if __name__ == "__main__":
    visualize()
