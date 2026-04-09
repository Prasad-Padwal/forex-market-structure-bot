"""
Levels Module

Calculates the three key entry zones used in the market structure strategy:

  1. SBR  – Support Becomes Resistance (or RBS: Resistance Becomes Support).
  2. A+/QML – Quasi Modal Level: midpoint between SBR and DT/DB (best entry).
  3. DT/DB  – Double Top / Double Bottom: the extreme swing high or low.

Each level is returned with a surrounding zone (±zone_pct % of candle body).
"""

import pandas as pd
import numpy as np
from typing import Optional


class Levels:
    """Calculates SBR, A+/QML, and DT/DB price levels with entry zones."""

    DEFAULT_ZONE_PCT = 0.015  # 1.5 % of candle body size

    def __init__(self, data: pd.DataFrame, zone_pct: float = DEFAULT_ZONE_PCT):
        """
        Args:
            data: OHLCV DataFrame with columns [open, high, low, close, volume].
            zone_pct: Fraction of average candle body used for zone width.
        """
        self.data = data.reset_index(drop=True)
        self.zone_pct = zone_pct

    # ------------------------------------------------------------------
    # Zone helper
    # ------------------------------------------------------------------

    def _make_zone(self, price: float) -> dict:
        """Return a price zone dict centred on *price*."""
        body_sizes = abs(self.data["close"] - self.data["open"])
        avg_body = float(body_sizes.mean()) if len(body_sizes) else price * 0.001
        half = max(avg_body * self.zone_pct, price * 0.0005)
        return {"price": price, "upper": price + half, "lower": price - half}

    # ------------------------------------------------------------------
    # Level calculations
    # ------------------------------------------------------------------

    def calculate_sbr(
        self,
        support_levels: Optional[list] = None,
        direction: str = "bearish",
    ) -> Optional[dict]:
        """
        Calculate the SBR (Support Becomes Resistance) level.

        For a bearish setup the most recent swing low that has been broken
        is used as resistance.  For a bullish setup the most recent broken
        swing high acts as support.

        Args:
            support_levels: Pre-calculated support price levels.
            direction: 'bearish' or 'bullish'.

        Returns:
            Zone dict or None if insufficient data.
        """
        if not support_levels:
            return None

        close = self.data["close"].iloc[-1]
        if direction == "bearish":
            # Find the highest support level that price is now trading below
            candidates = [s for s in support_levels if close < s]
            if not candidates:
                candidates = support_levels
            price = min(candidates)
        else:
            candidates = [s for s in support_levels if close > s]
            if not candidates:
                candidates = support_levels
            price = max(candidates)

        return self._make_zone(price)

    def calculate_dt_db(self, direction: str = "bearish") -> dict:
        """
        Calculate the Double-Top (bearish) or Double-Bottom (bullish) level.

        For bearish: the highest high in the dataset.
        For bullish: the lowest low in the dataset.

        Args:
            direction: 'bearish' or 'bullish'.

        Returns:
            Zone dict.
        """
        if direction == "bearish":
            price = float(self.data["high"].max())
        else:
            price = float(self.data["low"].min())
        return self._make_zone(price)

    def calculate_aplus_qml(
        self,
        sbr_level: Optional[float] = None,
        dt_db_level: Optional[float] = None,
        support_levels: Optional[list] = None,
        direction: str = "bearish",
    ) -> Optional[dict]:
        """
        Calculate the A+/QML (Quasi Modal Level) – the midpoint between
        the SBR level and the DT/DB extreme, which represents the best
        risk-reward entry point.

        Args:
            sbr_level: Pre-calculated SBR price. Auto-calculated if None.
            dt_db_level: Pre-calculated DT/DB price. Auto-calculated if None.
            support_levels: Used when auto-calculating SBR.
            direction: 'bearish' or 'bullish'.

        Returns:
            Zone dict or None if SBR cannot be determined.
        """
        if sbr_level is None:
            sbr = self.calculate_sbr(support_levels, direction)
            if sbr is None:
                return None
            sbr_level = sbr["price"]

        if dt_db_level is None:
            dt_db = self.calculate_dt_db(direction)
            dt_db_level = dt_db["price"]

        price = (sbr_level + dt_db_level) / 2.0
        return self._make_zone(price)

    # ------------------------------------------------------------------
    # All levels at once
    # ------------------------------------------------------------------

    def get_all_levels(
        self,
        support_levels: Optional[list] = None,
        direction: str = "bearish",
    ) -> dict:
        """
        Return all three levels (SBR, A+/QML, DT/DB) with their zones.

        Args:
            support_levels: Pre-calculated support price levels.
            direction: 'bearish' or 'bullish'.

        Returns:
            dict with keys 'sbr', 'aplus_qml', 'dt_db', each a zone dict
            (or None when a level cannot be calculated).
        """
        sbr = self.calculate_sbr(support_levels, direction)
        dt_db = self.calculate_dt_db(direction)
        aplus_qml = self.calculate_aplus_qml(
            sbr_level=sbr["price"] if sbr else None,
            dt_db_level=dt_db["price"],
            direction=direction,
        )
        return {"sbr": sbr, "aplus_qml": aplus_qml, "dt_db": dt_db}
