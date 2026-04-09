"""
Signal Generator Module

Orchestrates the full signal generation pipeline:
  1. Fetch & process data.
  2. Detect market structure.
  3. Identify 2CR + CHoH confirmations.
  4. Calculate level zones.
  5. Produce structured signal dicts.
"""

import pandas as pd
from typing import List, Optional

from ..strategy.market_structure import MarketStructure
from ..strategy.two_cr import TwoCR
from ..strategy.choch import CHoH
from ..strategy.levels import Levels
from ..strategy.signals import SignalEngine


class SignalGenerator:
    """Orchestrates full signal generation for a given pair and timeframe."""

    def __init__(
        self,
        pair: str = "EURUSD",
        timeframe: str = "4H",
        rr_target: float = 2.0,
        swing_lookback: int = 5,
    ):
        """
        Args:
            pair: Currency pair.
            timeframe: Chart timeframe.
            rr_target: Target Risk/Reward ratio for TP placement.
            swing_lookback: Bars each side to confirm swing points.
        """
        self.pair = pair
        self.timeframe = timeframe
        self.rr_target = rr_target
        self.swing_lookback = swing_lookback

    def generate(self, data: pd.DataFrame) -> List[dict]:
        """
        Run full signal detection pipeline on *data*.

        Args:
            data: Processed OHLCV DataFrame (with 'atr' column).

        Returns:
            List of signal dicts sorted by entry_priority.
        """
        data = data.reset_index(drop=True)

        # 1. Market structure
        ms = MarketStructure(data, self.swing_lookback)
        structure = ms.identify_structure()
        support_levels = structure["support_levels"]
        resistance_levels = structure["resistance_levels"]
        trend = structure["trend"]

        # 2. Determine direction from trend
        if trend == "bullish":
            direction = "LONG"
            choch_direction = "bullish"
        elif trend == "bearish":
            direction = "SHORT"
            choch_direction = "bearish"
        else:
            return []  # No clear trend → no signal

        # 3. Check 2CR on last bar
        two_cr = TwoCR(data)
        cr_result = two_cr.confirm_2cr()
        if not cr_result["confirmed"]:
            return []

        # Direction must agree with trend
        if cr_result["direction"] != choch_direction:
            return []

        # 4. CHoH confirmation
        choch_engine = CHoH(data)
        choch_found = False
        if direction == "LONG":
            for res in resistance_levels:
                if choch_engine.is_bullish_choch(res):
                    choch_found = True
                    break
        else:
            for sup in support_levels:
                if choch_engine.is_bearish_choch(sup):
                    choch_found = True
                    break

        if not choch_found:
            return []

        # 5. Levels
        levels_engine = Levels(data)
        all_levels = levels_engine.get_all_levels(support_levels, choch_direction)

        # 6. ATR for SL sizing
        atr = float(data["atr"].iloc[-1]) if "atr" in data.columns else 0.001

        # 7. Generate signals
        engine = SignalEngine(self.pair, self.timeframe)
        return engine.generate_signals_from_levels(all_levels, direction, atr, self.rr_target)
