"""
Metrics Module

Calculates trading performance statistics from a list of completed trades.
"""

import pandas as pd
import numpy as np
from typing import List, Optional


class Metrics:
    """Computes win rate, profit factor, and drawdown from trade records."""

    def __init__(self, trades: List[dict]):
        """
        Args:
            trades: List of trade dicts produced by Backtester.run().
        """
        self.trades = [t for t in trades if t.get("outcome") != "OPEN"]
        self._df: Optional[pd.DataFrame] = None

    def _get_df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = pd.DataFrame(self.trades) if self.trades else pd.DataFrame()
        return self._df

    # ------------------------------------------------------------------
    # Individual metrics
    # ------------------------------------------------------------------

    def win_rate(self) -> float:
        """Return fraction of winning trades (0.0 – 1.0)."""
        df = self._get_df()
        if df.empty:
            return 0.0
        wins = (df["outcome"] == "WIN").sum()
        return round(wins / len(df), 4)

    def profit_factor(self) -> float:
        """Return gross profit / gross loss. Returns inf if no losses."""
        df = self._get_df()
        if df.empty:
            return 0.0
        gross_profit = df.loc[df["pnl"] > 0, "pnl"].sum()
        gross_loss = df.loc[df["pnl"] < 0, "pnl"].abs().sum()
        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0
        return round(gross_profit / gross_loss, 4)

    def max_drawdown(self) -> float:
        """Return maximum peak-to-trough drawdown in pips/price units."""
        df = self._get_df()
        if df.empty:
            return 0.0
        cumulative = df["pnl"].cumsum()
        rolling_max = cumulative.cummax()
        drawdown = rolling_max - cumulative
        return round(float(drawdown.max()), 5)

    def total_trades(self) -> int:
        """Return total number of completed trades."""
        return len(self.trades)

    def total_pnl(self) -> float:
        """Return sum of all trade PnL values."""
        df = self._get_df()
        if df.empty:
            return 0.0
        return round(float(df["pnl"].sum()), 5)

    def average_rr(self) -> float:
        """Return average realised Risk/Reward ratio of winning trades."""
        df = self._get_df()
        if df.empty:
            return 0.0
        wins = df[df["outcome"] == "WIN"]
        if wins.empty:
            return 0.0
        rr = (wins["reward"] / wins["risk"].replace(0, np.nan)).dropna()
        return round(float(rr.mean()), 4)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Return all metrics in a single dict."""
        return {
            "total_trades": self.total_trades(),
            "win_rate": self.win_rate(),
            "profit_factor": self.profit_factor(),
            "max_drawdown": self.max_drawdown(),
            "total_pnl": self.total_pnl(),
            "average_rr": self.average_rr(),
        }
