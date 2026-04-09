"""
Data Fetcher Module

Fetches OHLCV forex data from Yahoo Finance using yfinance.

Supported pairs  : EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, NZDUSD, USDCAD
Supported periods: 1mo, 3mo, 6mo, 1y, 2y, 5y
Supported intervals (timeframes):
    '1h'  → 1-hour bars   (max 730 days of history from yfinance)
    '4h'  → 4-hour bars
    '1d'  → Daily bars
    '1wk' → Weekly bars
"""

import pandas as pd
import yfinance as yf
from typing import Optional


# yfinance uses "=X" suffix for forex pairs
_PAIR_MAP = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "USDCHF": "USDCHF=X",
    "AUDUSD": "AUDUSD=X",
    "NZDUSD": "NZDUSD=X",
    "USDCAD": "USDCAD=X",
    "EURGBP": "EURGBP=X",
    "EURJPY": "EURJPY=X",
}

# Map human-friendly timeframe strings to yfinance interval codes
_INTERVAL_MAP = {
    "1H": "1h",
    "4H": "4h",
    "1D": "1d",
    "1W": "1wk",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
    "1w": "1wk",
    "1wk": "1wk",
}


class DataFetcher:
    """Fetches and caches OHLCV data from Yahoo Finance."""

    def __init__(self, pair: str = "EURUSD", timeframe: str = "4H"):
        """
        Args:
            pair: Forex pair symbol, e.g. 'EURUSD'.
            timeframe: Timeframe string, e.g. '1H', '4H', '1D', '1W'.
        """
        self.pair = pair.upper()
        self.timeframe = timeframe.upper()
        self._ticker = _PAIR_MAP.get(self.pair, f"{self.pair}=X")
        self._interval = _INTERVAL_MAP.get(self.timeframe, "4h")
        self._cache: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------------
    # Fetch
    # ------------------------------------------------------------------

    def fetch(self, period: str = "1y") -> pd.DataFrame:
        """
        Download OHLCV data for the configured pair and timeframe.

        Args:
            period: yfinance period string ('1mo', '3mo', '6mo', '1y', '2y').

        Returns:
            DataFrame with lowercase columns: open, high, low, close, volume.
            Index is a DatetimeIndex.

        Raises:
            ValueError: If the download returns empty data.
        """
        raw = yf.download(
            self._ticker,
            period=period,
            interval=self._interval,
            auto_adjust=True,
            progress=False,
        )

        if raw.empty:
            raise ValueError(
                f"No data returned for {self.pair} ({self._ticker}) "
                f"interval={self._interval} period={period}."
            )

        # Normalise column names (yfinance may return str or tuple columns)
        normalised = []
        for c in raw.columns:
            if isinstance(c, str):
                normalised.append(c.lower())
            elif isinstance(c, (tuple, list)) and len(c) > 0 and isinstance(c[0], str):
                normalised.append(c[0].lower())
            else:
                normalised.append(str(c).lower())
        raw.columns = normalised  # type: ignore[assignment]
        # Ensure required columns exist
        for col in ("open", "high", "low", "close"):
            if col not in raw.columns:
                raise ValueError(f"Missing expected column '{col}' in downloaded data.")

        if "volume" not in raw.columns:
            raw["volume"] = 0

        self._cache = raw[["open", "high", "low", "close", "volume"]].copy()
        return self._cache

    def fetch_custom(
        self, start: str, end: str
    ) -> pd.DataFrame:
        """
        Download data for a specific date range.

        Args:
            start: Start date string 'YYYY-MM-DD'.
            end: End date string 'YYYY-MM-DD'.

        Returns:
            OHLCV DataFrame.
        """
        raw = yf.download(
            self._ticker,
            start=start,
            end=end,
            interval=self._interval,
            auto_adjust=True,
            progress=False,
        )
        if raw.empty:
            raise ValueError(
                f"No data returned for {self.pair} from {start} to {end}."
            )
        norm2 = []
        for c in raw.columns:
            if isinstance(c, str):
                norm2.append(c.lower())
            elif isinstance(c, (tuple, list)) and len(c) > 0 and isinstance(c[0], str):
                norm2.append(c[0].lower())
            else:
                norm2.append(str(c).lower())
        raw.columns = norm2  # type: ignore[assignment]
        for col in ("open", "high", "low", "close"):
            if col not in raw.columns:
                raise ValueError(f"Missing column '{col}'.")
        if "volume" not in raw.columns:
            raw["volume"] = 0
        self._cache = raw[["open", "high", "low", "close", "volume"]].copy()
        return self._cache

    @property
    def cached_data(self) -> Optional[pd.DataFrame]:
        """Return the last fetched DataFrame, or None."""
        return self._cache

    @staticmethod
    def supported_pairs() -> list:
        """Return list of supported forex pairs."""
        return list(_PAIR_MAP.keys())

    @staticmethod
    def supported_timeframes() -> list:
        """Return list of supported timeframe strings."""
        return ["1H", "4H", "1D", "1W"]
