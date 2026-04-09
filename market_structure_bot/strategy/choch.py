"""
CHoH (Change of Character) Module

Detects market-character changes that signal a potential trend reversal.

Bearish CHoH : last two candles close *below* a key support level.
Bullish CHoH : last two candles close *above* a key resistance level.
"""

import pandas as pd
from typing import Optional


class CHoH:
    """Detects Change of Character (CHoH) reversal signals."""

    def __init__(self, data: pd.DataFrame):
        """
        Args:
            data: OHLCV DataFrame with columns [open, high, low, close, volume].
        """
        self.data = data.reset_index(drop=True)

    # ------------------------------------------------------------------
    # Pattern detection
    # ------------------------------------------------------------------

    def is_bearish_choch(
        self, support: float, idx: Optional[int] = None
    ) -> bool:
        """
        Return True when the last two candles both close below *support*.

        Args:
            support: The key support price level to test against.
            idx: Bar index to check (default: last bar).
        """
        if idx is None:
            idx = len(self.data) - 1
        if idx < 1:
            return False

        c1 = float(self.data["close"].iloc[idx - 1])
        c2 = float(self.data["close"].iloc[idx])
        return c1 < support and c2 < support

    def is_bullish_choch(
        self, resistance: float, idx: Optional[int] = None
    ) -> bool:
        """
        Return True when the last two candles both close above *resistance*.

        Args:
            resistance: The key resistance price level to test against.
            idx: Bar index to check (default: last bar).
        """
        if idx is None:
            idx = len(self.data) - 1
        if idx < 1:
            return False

        c1 = float(self.data["close"].iloc[idx - 1])
        c2 = float(self.data["close"].iloc[idx])
        return c1 > resistance and c2 > resistance

    def detect_choch(
        self,
        support: Optional[float] = None,
        resistance: Optional[float] = None,
        idx: Optional[int] = None,
    ) -> dict:
        """
        Detect CHoH against provided support/resistance levels.

        Returns:
            dict with keys:
                - detected (bool)
                - direction ('bullish' | 'bearish' | None)
                - level (float | None) – the level that was broken
                - idx (int)
        """
        if idx is None:
            idx = len(self.data) - 1

        if resistance is not None and self.is_bullish_choch(resistance, idx):
            return {
                "detected": True,
                "direction": "bullish",
                "level": resistance,
                "idx": idx,
            }

        if support is not None and self.is_bearish_choch(support, idx):
            return {
                "detected": True,
                "direction": "bearish",
                "level": support,
                "idx": idx,
            }

        return {"detected": False, "direction": None, "level": None, "idx": idx}

    def scan_all(
        self,
        support_levels: Optional[list] = None,
        resistance_levels: Optional[list] = None,
    ) -> list:
        """
        Scan full dataset for CHoH signals against all provided levels.

        Args:
            support_levels: List of support price levels.
            resistance_levels: List of resistance price levels.

        Returns:
            List of detected CHoH signal dicts.
        """
        support_levels = support_levels or []
        resistance_levels = resistance_levels or []
        signals = []

        for i in range(1, len(self.data)):
            for sup in support_levels:
                result = self.detect_choch(support=sup, idx=i)
                if result["detected"]:
                    signals.append(result)
                    break
            for res in resistance_levels:
                result = self.detect_choch(resistance=res, idx=i)
                if result["detected"]:
                    signals.append(result)
                    break
        return signals
