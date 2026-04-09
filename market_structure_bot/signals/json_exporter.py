"""
JSON Exporter Module

Exports trading signals to JSON files or stdout for consumption by
TradingView alerts, webhook receivers, or other downstream systems.
"""

import json
import os
from datetime import datetime, timezone
from typing import List, Optional


class JsonExporter:
    """Serializes and exports signal dicts to JSON."""

    def __init__(self, output_dir: str = "signals_output"):
        """
        Args:
            output_dir: Directory where JSON files are saved.
        """
        self.output_dir = output_dir

    @staticmethod
    def _enrich(signal: dict) -> dict:
        """Add a UTC timestamp and sanitise float precision."""
        enriched = signal.copy()
        enriched["generated_at"] = datetime.now(timezone.utc).isoformat()
        for key, val in enriched.items():
            if isinstance(val, float):
                enriched[key] = round(val, 5)
        return enriched

    def to_string(self, signals: List[dict], indent: int = 2) -> str:
        """Return signals serialised as a JSON string."""
        enriched = [self._enrich(s) for s in signals]
        return json.dumps(enriched, indent=indent)

    def to_stdout(self, signals: List[dict]):
        """Print signals as formatted JSON to stdout."""
        print(self.to_string(signals))

    def to_file(self, signals: List[dict], filename: Optional[str] = None) -> str:
        """
        Save signals to a JSON file.

        Args:
            signals: List of signal dicts.
            filename: Override default timestamped filename.

        Returns:
            Absolute path of the written file.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        if filename is None:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"signals_{ts}.json"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(self.to_string(signals))
        return filepath

    def to_tradingview_webhook(self, signal: dict) -> str:
        """
        Format a single signal as a TradingView-compatible JSON alert message.

        Args:
            signal: Single signal dict.

        Returns:
            JSON string suitable for a TradingView webhook payload.
        """
        payload = {
            "strategy": "MarketStructureBot",
            "pair": signal.get("pair"),
            "action": "buy" if signal.get("direction") == "LONG" else "sell",
            "price": signal.get("entry_price"),
            "sl": signal.get("stop_loss"),
            "tp": signal.get("take_profit"),
            "rr": signal.get("risk_reward_ratio"),
            "zone": signal.get("zone"),
            "priority": signal.get("entry_priority"),
        }
        return json.dumps(payload, indent=2)
