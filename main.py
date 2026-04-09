"""
Forex Market Structure Bot – Main Entry Point

Usage::

    python main.py --pair EURUSD --timeframe 4H --action scan
    python main.py --pair GBPUSD --timeframe 1D --action backtest
    python main.py --pair USDJPY --timeframe 4H --action visualize
    python main.py --action scan --pairs EURUSD GBPUSD USDJPY

Actions:
    scan        Fetch latest data and print any detected signals.
    backtest    Run a historical backtest and print performance metrics.
    visualize   Plot a candlestick chart with market structure zones.
"""

import argparse
import logging
import sys

from market_structure_bot.config.settings import default_settings as cfg
from market_structure_bot.data.data_fetcher import DataFetcher
from market_structure_bot.data.data_processor import DataProcessor
from market_structure_bot.signals.signal_generator import SignalGenerator
from market_structure_bot.signals.json_exporter import JsonExporter
from market_structure_bot.backtest.backtester import Backtester
from market_structure_bot.backtest.metrics import Metrics
from market_structure_bot.strategy.market_structure import MarketStructure
from market_structure_bot.strategy.levels import Levels
from market_structure_bot.visualization.chart_plotter import ChartPlotter
from market_structure_bot.visualization.zone_markers import ZoneMarkers


logging.basicConfig(
    level=getattr(logging, cfg.log_level, logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Action handlers
# ------------------------------------------------------------------

def action_scan(pair: str, timeframe: str, period: str = "1y"):
    log.info("Scanning %s %s …", pair, timeframe)
    fetcher = DataFetcher(pair, timeframe)
    raw = fetcher.fetch(period)
    processor = DataProcessor(raw)
    data = processor.process(cfg.atr_period)

    generator = SignalGenerator(pair, timeframe, cfg.default_rr_target, cfg.swing_lookback)
    signals = generator.generate(data)

    if signals:
        log.info("Found %d signal(s):", len(signals))
        exporter = JsonExporter(cfg.signals_output_dir)
        exporter.to_stdout(signals)
    else:
        log.info("No signals detected for %s %s.", pair, timeframe)


def action_backtest(pair: str, timeframe: str, period: str = "2y"):
    log.info("Backtesting %s %s …", pair, timeframe)
    fetcher = DataFetcher(pair, timeframe)
    raw = fetcher.fetch(period)
    processor = DataProcessor(raw)
    data = processor.process(cfg.atr_period)

    backtester = Backtester(data, pair, timeframe, cfg.default_rr_target, cfg.sl_atr_multiplier)
    trades = backtester.run(cfg.swing_lookback)

    metrics = Metrics(trades)
    summary = metrics.summary()

    print(f"\n{'='*50}")
    print(f"  Backtest Results  –  {pair} {timeframe}")
    print(f"{'='*50}")
    for k, v in summary.items():
        print(f"  {k:<22}: {v}")
    print(f"{'='*50}\n")


def action_visualize(pair: str, timeframe: str, period: str = "6mo", save_path: str = None):
    log.info("Visualizing %s %s …", pair, timeframe)
    fetcher = DataFetcher(pair, timeframe)
    raw = fetcher.fetch(period)
    processor = DataProcessor(raw)
    data = processor.process(cfg.atr_period)

    ms = MarketStructure(data, cfg.swing_lookback)
    structure = ms.identify_structure()

    levels_engine = Levels(data, cfg.zone_pct)
    direction = "bearish" if structure["trend"] in ("bearish", "sideways") else "bullish"
    all_levels = levels_engine.get_all_levels(structure["support_levels"], direction)

    plotter = ChartPlotter(data, pair, timeframe)
    plotter.plot_base_chart()
    plotter.add_support_resistance(
        structure["support_levels"], structure["resistance_levels"]
    )

    zone_markers = ZoneMarkers(plotter.ax, len(data))
    zone_markers.add_all_zones(all_levels)

    if save_path:
        plotter.save(save_path)
        log.info("Chart saved to %s", save_path)
    else:
        plotter.show()


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Forex Market Structure Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--pair", default="EURUSD", help="Single forex pair (default: EURUSD)")
    parser.add_argument(
        "--pairs",
        nargs="+",
        help="Multiple forex pairs to scan (overrides --pair)",
    )
    parser.add_argument(
        "--timeframe",
        default="4H",
        choices=["1H", "4H", "1D", "1W"],
        help="Chart timeframe (default: 4H)",
    )
    parser.add_argument(
        "--action",
        default="scan",
        choices=["scan", "backtest", "visualize"],
        help="Action to perform (default: scan)",
    )
    parser.add_argument("--period", default=None, help="Data period (e.g. '1y', '2y', '6mo')")
    parser.add_argument("--save", default=None, help="Save chart to this file path (visualize only)")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    pairs = args.pairs or [args.pair]
    action = args.action

    default_periods = {"scan": "1y", "backtest": "2y", "visualize": "6mo"}
    period = args.period or default_periods[action]

    for pair in pairs:
        try:
            if action == "scan":
                action_scan(pair, args.timeframe, period)
            elif action == "backtest":
                action_backtest(pair, args.timeframe, period)
            elif action == "visualize":
                action_visualize(pair, args.timeframe, period, args.save)
        except Exception as exc:
            log.error("Error processing %s: %s", pair, exc)

    sys.exit(0)


if __name__ == "__main__":
    main()
