"""
Market Structure Module

Detects peaks, valleys, support and resistance levels in forex price data.
"""

import numpy as np
import pandas as pd
from typing import List, Optional, Tuple


class MarketStructure:
    """Detects and tracks forex market structure including peaks, valleys,
    support and resistance levels."""

    def __init__(self, data: pd.DataFrame, swing_lookback: int = 5):
        """
        Args:
            data: OHLCV DataFrame with columns [open, high, low, close, volume].
            swing_lookback: Number of bars on each side to confirm a swing point.
        """
        self.data = data.copy()
        self.swing_lookback = swing_lookback
        self._peaks: List[int] = []
        self._valleys: List[int] = []
        self._support_levels: List[float] = []
        self._resistance_levels: List[float] = []

    # ------------------------------------------------------------------
    # Peak / Valley detection
    # ------------------------------------------------------------------

    def find_peaks(self) -> List[int]:
        """Return bar indices that are local highs (swing highs)."""
        highs = self.data["high"].values
        lb = self.swing_lookback
        peaks = []
        for i in range(lb, len(highs) - lb):
            window = highs[i - lb : i + lb + 1]
            if highs[i] == max(window):
                peaks.append(i)
        self._peaks = peaks
        return peaks

    def find_valleys(self) -> List[int]:
        """Return bar indices that are local lows (swing lows)."""
        lows = self.data["low"].values
        lb = self.swing_lookback
        valleys = []
        for i in range(lb, len(lows) - lb):
            window = lows[i - lb : i + lb + 1]
            if lows[i] == min(window):
                valleys.append(i)
        self._valleys = valleys
        return valleys

    # ------------------------------------------------------------------
    # Support / Resistance
    # ------------------------------------------------------------------

    def find_support_levels(self) -> List[float]:
        """Return price levels acting as support (swing lows)."""
        if not self._valleys:
            self.find_valleys()
        levels = [float(self.data["low"].iloc[i]) for i in self._valleys]
        self._support_levels = levels
        return levels

    def find_resistance_levels(self) -> List[float]:
        """Return price levels acting as resistance (swing highs)."""
        if not self._peaks:
            self.find_peaks()
        levels = [float(self.data["high"].iloc[i]) for i in self._peaks]
        self._resistance_levels = levels
        return levels

    # ------------------------------------------------------------------
    # Trend
    # ------------------------------------------------------------------

    def detect_trend(self) -> str:
        """Detect overall trend: 'bullish', 'bearish', or 'sideways'."""
        if not self._peaks or not self._valleys:
            self.find_peaks()
            self.find_valleys()

        if len(self._peaks) < 2 or len(self._valleys) < 2:
            return "sideways"

        last_two_peaks = [self.data["high"].iloc[i] for i in self._peaks[-2:]]
        last_two_valleys = [self.data["low"].iloc[i] for i in self._valleys[-2:]]

        hh = last_two_peaks[1] > last_two_peaks[0]
        hl = last_two_valleys[1] > last_two_valleys[0]
        lh = last_two_peaks[1] < last_two_peaks[0]
        ll = last_two_valleys[1] < last_two_valleys[0]

        if hh and hl:
            return "bullish"
        if lh and ll:
            return "bearish"
        return "sideways"

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def identify_structure(self) -> dict:
        """Run full market structure analysis and return a summary dict."""
        trend = self.detect_trend()
        support = self.find_support_levels()
        resistance = self.find_resistance_levels()
        return {
            "trend": trend,
            "support_levels": support,
            "resistance_levels": resistance,
            "peaks": self._peaks,
            "valleys": self._valleys,
        }
