"""
Settings / Configuration Module

Central configuration for the Forex Market Structure Bot.
All parameters can be overridden via environment variables.
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Settings:
    """Bot configuration dataclass with environment-variable overrides."""

    # ------------------------------------------------------------------
    # Trading pairs
    # ------------------------------------------------------------------
    pairs: List[str] = field(
        default_factory=lambda: [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "USDCHF",
            "AUDUSD",
            "NZDUSD",
            "USDCAD",
        ]
    )

    # ------------------------------------------------------------------
    # Timeframes
    # ------------------------------------------------------------------
    timeframes: List[str] = field(
        default_factory=lambda: ["1H", "4H", "1D", "1W"]
    )

    # ------------------------------------------------------------------
    # Risk management
    # ------------------------------------------------------------------
    default_rr_target: float = 2.0
    sl_atr_multiplier: float = 1.5
    max_risk_per_trade_pct: float = 1.0   # % of account balance
    max_open_trades: int = 5

    # ------------------------------------------------------------------
    # Strategy
    # ------------------------------------------------------------------
    swing_lookback: int = 5
    zone_pct: float = 0.015              # 1.5 % zone width
    atr_period: int = 14
    min_rr_to_publish: float = 1.5

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    default_period: str = "1y"
    data_cache_dir: str = "data_cache"

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    signals_output_dir: str = "signals_output"
    charts_output_dir: str = "charts_output"

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    log_level: str = "INFO"

    def __post_init__(self):
        """Apply environment-variable overrides after dataclass init."""
        if os.getenv("BOT_LOG_LEVEL"):
            self.log_level = os.environ["BOT_LOG_LEVEL"]
        if os.getenv("BOT_RR_TARGET"):
            self.default_rr_target = float(os.environ["BOT_RR_TARGET"])
        if os.getenv("BOT_MAX_RISK_PCT"):
            self.max_risk_per_trade_pct = float(os.environ["BOT_MAX_RISK_PCT"])
        if os.getenv("BOT_SIGNALS_DIR"):
            self.signals_output_dir = os.environ["BOT_SIGNALS_DIR"]


# Module-level default instance
default_settings = Settings()
