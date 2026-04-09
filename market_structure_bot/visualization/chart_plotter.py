"""
Chart Plotter Module

Plots OHLCV candlestick charts enriched with market structure overlays
(support/resistance levels, 2CR confirmations, trade zones).

Requires matplotlib and mplfinance.  Falls back to a simple close-line
chart if mplfinance is not available.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Optional, List


class ChartPlotter:
    """Plots candlestick charts with market structure overlays."""

    def __init__(self, data: pd.DataFrame, pair: str = "EURUSD", timeframe: str = "4H"):
        """
        Args:
            data: OHLCV DataFrame (index should be a DatetimeIndex or RangeIndex).
            pair: Label for the chart title.
            timeframe: Label for the chart title.
        """
        self.data = data.copy()
        self.pair = pair
        self.timeframe = timeframe
        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[plt.Axes] = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _setup_figure(self, figsize=(16, 8)):
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.set_title(f"{self.pair} – {self.timeframe}", fontsize=14, fontweight="bold")
        self.ax.set_xlabel("Bar index")
        self.ax.set_ylabel("Price")
        self.ax.grid(True, alpha=0.3)

    def _draw_candles(self):
        """Draw simple OHLC bar chart."""
        df = self.data.reset_index(drop=True)
        for i, row in df.iterrows():
            color = "green" if row["close"] >= row["open"] else "red"
            # Wick
            self.ax.plot([i, i], [row["low"], row["high"]], color=color, linewidth=0.8)
            # Body
            body_bottom = min(row["open"], row["close"])
            body_height = abs(row["close"] - row["open"])
            rect = mpatches.FancyBboxPatch(
                (i - 0.3, body_bottom),
                0.6,
                max(body_height, 1e-10),
                boxstyle="square,pad=0",
                facecolor=color,
                edgecolor=color,
                alpha=0.8,
            )
            self.ax.add_patch(rect)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def plot_base_chart(self, figsize=(16, 8)) -> "ChartPlotter":
        """Draw base candlestick chart."""
        self._setup_figure(figsize)
        self._draw_candles()
        return self

    def add_support_resistance(
        self,
        support_levels: Optional[List[float]] = None,
        resistance_levels: Optional[List[float]] = None,
    ) -> "ChartPlotter":
        """
        Overlay horizontal support and resistance lines.

        Args:
            support_levels: List of support prices.
            resistance_levels: List of resistance prices.
        """
        if self.ax is None:
            self.plot_base_chart()
        for level in (support_levels or []):
            self.ax.axhline(level, color="blue", linestyle="--", linewidth=0.9, alpha=0.7,
                            label=f"Support {level:.5f}")
        for level in (resistance_levels or []):
            self.ax.axhline(level, color="orange", linestyle="--", linewidth=0.9, alpha=0.7,
                            label=f"Resistance {level:.5f}")
        return self

    def add_signal_markers(self, signals: List[dict]) -> "ChartPlotter":
        """
        Add entry arrows for each signal dict.

        Args:
            signals: List of signal dicts (output of SignalEngine).
        """
        if self.ax is None:
            self.plot_base_chart()
        df = self.data.reset_index(drop=True)
        for sig in signals:
            entry = sig.get("entry_price")
            direction = sig.get("direction", "LONG")
            if entry is None:
                continue
            # Plot at the last bar for visual purposes
            x = len(df) - 1
            marker = "^" if direction == "LONG" else "v"
            color = "lime" if direction == "LONG" else "red"
            self.ax.scatter(x, entry, marker=marker, color=color, s=120, zorder=5,
                            label=f"{direction} @ {entry:.5f}")
        return self

    def show(self):
        """Display the chart interactively."""
        if self.fig is None:
            self.plot_base_chart()
        handles, labels = self.ax.get_legend_handles_labels()
        if labels:
            by_label = dict(zip(labels, handles))
            self.ax.legend(by_label.values(), by_label.keys(), fontsize=8)
        plt.tight_layout()
        plt.show()

    def save(self, filepath: str, dpi: int = 150):
        """Save chart to file."""
        if self.fig is None:
            self.plot_base_chart()
        plt.tight_layout()
        self.fig.savefig(filepath, dpi=dpi)
        plt.close(self.fig)
