"""
Backtester Module

Tests the market structure strategy on historical OHLCV data by:
  1. Scanning every bar for 2CR + CHoH confirmations.
  2. Opening a simulated trade at the signal bar's close.
  3. Tracking each trade to its SL or TP outcome.
  4. Recording the trade journal for metrics calculation.
"""

import pandas as pd
import numpy as np
from typing import List, Optional

from ..strategy.market_structure import MarketStructure
from ..strategy.two_cr import TwoCR
from ..strategy.choch import CHoH
from ..strategy.levels import Levels
from ..strategy.signals import SignalEngine


class Backtester:
    """
    Runs a vectorised-style backtest of the market structure strategy.

    Each trade is tracked bar-by-bar once opened until SL or TP is hit.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        pair: str = "EURUSD",
        timeframe: str = "4H",
        rr_target: float = 2.0,
        sl_atr_mult: float = 1.5,
    ):
        """
        Args:
            data: Processed OHLCV DataFrame (must have 'atr' column).
            pair: Currency pair label for signal tagging.
            timeframe: Timeframe label for signal tagging.
            rr_target: Take-profit expressed as a multiple of the risk.
            sl_atr_mult: Stop-loss distance = ATR × sl_atr_mult.
        """
        self.data = data.reset_index(drop=True)
        self.pair = pair
        self.timeframe = timeframe
        self.rr_target = rr_target
        self.sl_atr_mult = sl_atr_mult
        self.trades: List[dict] = []

    # ------------------------------------------------------------------
    # Trade simulation helpers
    # ------------------------------------------------------------------

    def _simulate_trade(
        self,
        entry_idx: int,
        direction: str,
        entry: float,
        sl: float,
        tp: float,
    ) -> dict:
        """
        Walk forward from *entry_idx* until SL or TP is hit.

        Returns:
            Trade result dict.
        """
        for i in range(entry_idx + 1, len(self.data)):
            high = float(self.data["high"].iloc[i])
            low = float(self.data["low"].iloc[i])

            if direction == "SHORT":
                if low <= tp:
                    return self._trade_record(entry_idx, i, direction, entry, sl, tp, "WIN")
                if high >= sl:
                    return self._trade_record(entry_idx, i, direction, entry, sl, tp, "LOSS")
            else:  # LONG
                if high >= tp:
                    return self._trade_record(entry_idx, i, direction, entry, sl, tp, "WIN")
                if low <= sl:
                    return self._trade_record(entry_idx, i, direction, entry, sl, tp, "LOSS")

        # Trade never resolved – mark as open/expired
        return self._trade_record(entry_idx, len(self.data) - 1, direction, entry, sl, tp, "OPEN")

    @staticmethod
    def _trade_record(
        open_idx: int,
        close_idx: int,
        direction: str,
        entry: float,
        sl: float,
        tp: float,
        outcome: str,
    ) -> dict:
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        pnl = reward if outcome == "WIN" else (-risk if outcome == "LOSS" else 0.0)
        return {
            "open_idx": open_idx,
            "close_idx": close_idx,
            "direction": direction,
            "entry": entry,
            "stop_loss": sl,
            "take_profit": tp,
            "outcome": outcome,
            "pnl": pnl,
            "risk": risk,
            "reward": reward,
        }

    # ------------------------------------------------------------------
    # Main run
    # ------------------------------------------------------------------

    def run(self, swing_lookback: int = 5) -> List[dict]:
        """
        Execute the backtest over the full dataset.

        Args:
            swing_lookback: Bars each side to confirm swing points.

        Returns:
            List of trade result dicts (also stored in self.trades).
        """
        self.trades = []
        two_cr = TwoCR(self.data)
        ms = MarketStructure(self.data, swing_lookback)
        ms.find_peaks()
        ms.find_valleys()
        support_levels = ms.find_support_levels()
        resistance_levels = ms.find_resistance_levels()
        choch_engine = CHoH(self.data)
        levels_engine = Levels(self.data)

        # Require 'atr' column
        if "atr" not in self.data.columns:
            raise ValueError("Data must have an 'atr' column. Run DataProcessor first.")

        # Start at swing_lookback+2 to ensure:
        #   - swing_lookback bars of history for MarketStructure
        #   - +2 so the 2CR check can access candle[i-1] safely
        for i in range(swing_lookback + 2, len(self.data) - 1):
            atr = float(self.data["atr"].iloc[i])
            if atr == 0 or np.isnan(atr):
                continue

            # Check 2CR signal
            cr_result = two_cr.confirm_2cr(i)
            if not cr_result["confirmed"]:
                continue

            direction_label = cr_result["direction"]  # 'bullish' | 'bearish'
            trade_dir = "LONG" if direction_label == "bullish" else "SHORT"

            # Check CHoH confirmation
            choch_found = False
            if trade_dir == "LONG":
                for res in resistance_levels:
                    if choch_engine.is_bullish_choch(res, i):
                        choch_found = True
                        break
            else:
                for sup in support_levels:
                    if choch_engine.is_bearish_choch(sup, i):
                        choch_found = True
                        break

            if not choch_found:
                continue

            # Calculate levels and enter at A+/QML if available
            all_lvls = levels_engine.get_all_levels(support_levels, direction_label)
            entry_zone = all_lvls.get("aplus_qml") or all_lvls.get("sbr")
            if entry_zone is None:
                continue

            entry = entry_zone["price"]
            sl_dist = atr * self.sl_atr_mult

            if trade_dir == "SHORT":
                sl = entry + sl_dist
                tp = entry - sl_dist * self.rr_target
            else:
                sl = entry - sl_dist
                tp = entry + sl_dist * self.rr_target

            trade = self._simulate_trade(i, trade_dir, entry, sl, tp)
            self.trades.append(trade)

        return self.trades

    def get_trades_df(self) -> pd.DataFrame:
        """Return the trade journal as a DataFrame."""
        if not self.trades:
            return pd.DataFrame()
        return pd.DataFrame(self.trades)
