"""
Signal Engine Module

Generates structured trading signals from market structure analysis.

Signal structure::

    {
        "pair": "EURUSD",
        "timeframe": "4H",
        "direction": "SHORT|LONG",
        "entry_price": 1.0820,
        "stop_loss": 1.0835,
        "take_profit": 1.0790,
        "risk_reward_ratio": 2.0,
        "zone": "aplus_qml|sbr|dt_db",
        "entry_priority": 1
    }
"""

import pandas as pd
from typing import Optional

PRIORITY_MAP = {"aplus_qml": 1, "sbr": 2, "dt_db": 3}


class SignalEngine:
    """Generates, validates, and packages trading signals."""

    def __init__(self, pair: str = "EURUSD", timeframe: str = "4H"):
        self.pair = pair
        self.timeframe = timeframe

    # ------------------------------------------------------------------
    # Risk / Reward
    # ------------------------------------------------------------------

    def calculate_risk_reward(
        self, entry: float, stop_loss: float, take_profit: float
    ) -> float:
        """
        Calculate the Risk/Reward ratio.

        Args:
            entry: Entry price.
            stop_loss: Stop-loss price.
            take_profit: Take-profit price.

        Returns:
            R/R ratio (positive float). Returns 0.0 on invalid input.
        """
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        if risk == 0:
            return 0.0
        return round(reward / risk, 2)

    # ------------------------------------------------------------------
    # Signal generation
    # ------------------------------------------------------------------

    def generate_signal(
        self,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        zone: str = "sbr",
        levels: Optional[dict] = None,
    ) -> dict:
        """
        Create a structured trading signal.

        Args:
            direction: 'LONG' or 'SHORT'.
            entry_price: Proposed entry price.
            stop_loss: Stop-loss price.
            take_profit: Take-profit price.
            zone: Which level zone the entry is in ('sbr', 'aplus_qml', 'dt_db').
            levels: Optional full levels dict for enrichment.

        Returns:
            Signal dict ready for export or further processing.
        """
        rr = self.calculate_risk_reward(entry_price, stop_loss, take_profit)
        priority = PRIORITY_MAP.get(zone, 3)

        signal = {
            "pair": self.pair,
            "timeframe": self.timeframe,
            "direction": direction.upper(),
            "entry_price": round(entry_price, 5),
            "stop_loss": round(stop_loss, 5),
            "take_profit": round(take_profit, 5),
            "risk_reward_ratio": rr,
            "zone": zone,
            "entry_priority": priority,
        }

        if levels:
            signal["levels"] = levels

        return signal

    def generate_signals_from_levels(
        self,
        levels: dict,
        direction: str,
        atr: float,
        rr_target: float = 2.0,
    ) -> list:
        """
        Auto-generate signals for each available level zone.

        Args:
            levels: Output of ``Levels.get_all_levels()``.
            direction: 'LONG' or 'SHORT'.
            atr: Average True Range used to set SL distance.
            rr_target: Desired minimum Risk/Reward ratio.

        Returns:
            List of signal dicts sorted by entry_priority.
        """
        signals = []
        sl_distance = atr * 1.5

        for zone_name, zone_data in levels.items():
            if zone_data is None:
                continue
            entry = zone_data["price"]

            if direction.upper() == "SHORT":
                stop_loss = entry + sl_distance
                take_profit = entry - sl_distance * rr_target
            else:
                stop_loss = entry - sl_distance
                take_profit = entry + sl_distance * rr_target

            sig = self.generate_signal(
                direction=direction,
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit=take_profit,
                zone=zone_name,
            )
            signals.append(sig)

        return sorted(signals, key=lambda s: s["entry_priority"])
