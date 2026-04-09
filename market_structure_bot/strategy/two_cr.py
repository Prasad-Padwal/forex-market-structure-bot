"""
2CR (Two Candle Retracement) Module

Detects bullish and bearish two-candle retracement setups.

Bullish 2CR : two consecutive red (bearish) candles pulling back within an
              uptrend – expects price to continue higher after the pullback.
Bearish 2CR : two consecutive green (bullish) candles pulling back within a
              downtrend – expects price to continue lower after the pullback.
"""

import pandas as pd
from typing import Optional


class TwoCR:
    """Identifies 2-Candle Retracement (2CR) confirmation patterns."""

    def __init__(self, data: pd.DataFrame):
        """
        Args:
            data: OHLCV DataFrame with columns [open, high, low, close, volume].
        """
        self.data = data.reset_index(drop=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_red(self, idx: int) -> bool:
        """Return True if candle at *idx* is bearish (close < open)."""
        return float(self.data["close"].iloc[idx]) < float(self.data["open"].iloc[idx])

    def _is_green(self, idx: int) -> bool:
        """Return True if candle at *idx* is bullish (close >= open)."""
        return float(self.data["close"].iloc[idx]) >= float(self.data["open"].iloc[idx])

    # ------------------------------------------------------------------
    # Pattern detection
    # ------------------------------------------------------------------

    def is_bullish_2cr(self, idx: Optional[int] = None) -> bool:
        """
        Detect a bullish 2CR pattern ending at *idx* (default: last bar).

        Conditions:
        - Candle[idx-1] and Candle[idx] are both red (bearish).
        - close[idx] < close[idx-1]  → closes are descending (deeper pullback).
        """
        if idx is None:
            idx = len(self.data) - 1
        if idx < 1:
            return False

        c1, c2 = idx - 1, idx
        return (
            self._is_red(c1)
            and self._is_red(c2)
            and float(self.data["close"].iloc[c2]) < float(self.data["close"].iloc[c1])
        )

    def is_bearish_2cr(self, idx: Optional[int] = None) -> bool:
        """
        Detect a bearish 2CR pattern ending at *idx* (default: last bar).

        Conditions:
        - Candle[idx-1] and Candle[idx] are both green (bullish).
        - close[idx] > close[idx-1]  → closes are ascending (deeper pullback up).
        """
        if idx is None:
            idx = len(self.data) - 1
        if idx < 1:
            return False

        c1, c2 = idx - 1, idx
        return (
            self._is_green(c1)
            and self._is_green(c2)
            and float(self.data["close"].iloc[c2]) > float(self.data["close"].iloc[c1])
        )

    def confirm_2cr(self, idx: Optional[int] = None) -> dict:
        """
        Return 2CR confirmation status at *idx*.

        Returns:
            dict with keys:
                - confirmed (bool)
                - direction ('bullish' | 'bearish' | None)
                - idx (int)
        """
        if idx is None:
            idx = len(self.data) - 1

        if self.is_bullish_2cr(idx):
            return {"confirmed": True, "direction": "bullish", "idx": idx}
        if self.is_bearish_2cr(idx):
            return {"confirmed": True, "direction": "bearish", "idx": idx}
        return {"confirmed": False, "direction": None, "idx": idx}

    def scan_all(self) -> list:
        """Scan entire dataset and return list of confirmed 2CR signals."""
        signals = []
        for i in range(1, len(self.data)):
            result = self.confirm_2cr(i)
            if result["confirmed"]:
                signals.append(result)
        return signals
