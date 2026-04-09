"""
Data Processor Module

Validates and enriches raw OHLCV DataFrames with additional columns used by
the strategy modules (ATR, candle body sizes, candle direction, etc.).
"""

import pandas as pd
import numpy as np
from typing import Optional


class DataProcessor:
    """Validates, cleans, and enriches OHLCV data for strategy use."""

    def __init__(self, data: pd.DataFrame):
        """
        Args:
            data: Raw OHLCV DataFrame (output of DataFetcher.fetch).
        """
        self.data = data.copy()
        self._validated = False

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """
        Check that required columns exist and have no NaN values.

        Returns:
            True if data is valid.

        Raises:
            ValueError: On missing columns or empty data.
        """
        required = {"open", "high", "low", "close"}
        missing = required - set(self.data.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        if self.data.empty:
            raise ValueError("DataFrame is empty.")
        # Drop rows with NaN in OHLC columns
        self.data.dropna(subset=list(required), inplace=True)
        if self.data.empty:
            raise ValueError("All rows contain NaN in OHLC columns.")
        self._validated = True
        return True

    # ------------------------------------------------------------------
    # Enrichment
    # ------------------------------------------------------------------

    def add_atr(self, period: int = 14) -> "DataProcessor":
        """
        Add an ATR (Average True Range) column to the DataFrame.

        Args:
            period: Lookback period for ATR calculation.
        """
        high = self.data["high"]
        low = self.data["low"]
        close = self.data["close"]

        prev_close = close.shift(1)
        tr = pd.concat(
            [
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        self.data["atr"] = tr.ewm(span=period, adjust=False).mean()
        return self

    def add_candle_direction(self) -> "DataProcessor":
        """
        Add a 'direction' column: +1 for bullish candle, -1 for bearish.
        """
        self.data["direction"] = np.where(
            self.data["close"] >= self.data["open"], 1, -1
        )
        return self

    def add_body_size(self) -> "DataProcessor":
        """Add a 'body_size' column with absolute close-open difference."""
        self.data["body_size"] = (
            self.data["close"] - self.data["open"]
        ).abs()
        return self

    def add_wick_sizes(self) -> "DataProcessor":
        """Add 'upper_wick' and 'lower_wick' columns."""
        self.data["upper_wick"] = self.data["high"] - self.data[["open", "close"]].max(axis=1)
        self.data["lower_wick"] = self.data[["open", "close"]].min(axis=1) - self.data["low"]
        return self

    def process(self, atr_period: int = 14) -> pd.DataFrame:
        """
        Run full processing pipeline: validate → ATR → direction → body.

        Args:
            atr_period: ATR lookback period.

        Returns:
            Enriched OHLCV DataFrame.
        """
        self.validate()
        self.add_atr(atr_period)
        self.add_candle_direction()
        self.add_body_size()
        self.add_wick_sizes()
        return self.data
