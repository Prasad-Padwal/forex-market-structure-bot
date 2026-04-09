"""
Zone Markers Module

Adds coloured rectangular zone overlays to an existing matplotlib Axes for
SBR, A+/QML, and DT/DB price zones.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Optional


# Colour palette for the three zones
_ZONE_COLORS = {
    "sbr": ("#FFA500", "SBR"),          # orange
    "aplus_qml": ("#00FF7F", "A+/QML"), # spring green
    "dt_db": ("#FF4500", "DT/DB"),      # red-orange
}


class ZoneMarkers:
    """Draws price zone overlays on a matplotlib Axes."""

    def __init__(self, ax: plt.Axes, num_bars: int):
        """
        Args:
            ax: Matplotlib Axes to draw on.
            num_bars: Total number of bars in the chart (used for zone width).
        """
        self.ax = ax
        self.num_bars = num_bars

    def add_zone(
        self,
        zone: dict,
        zone_type: str = "sbr",
        alpha: float = 0.25,
        x_start: Optional[int] = None,
        x_end: Optional[int] = None,
    ):
        """
        Draw a horizontal shaded rectangle for a price zone.

        Args:
            zone: Zone dict with keys 'price', 'upper', 'lower'.
            zone_type: One of 'sbr', 'aplus_qml', 'dt_db'.
            alpha: Fill opacity.
            x_start: Left edge bar index (default 0).
            x_end: Right edge bar index (default num_bars).
        """
        color, label = _ZONE_COLORS.get(zone_type, ("#AAAAAA", zone_type))
        x0 = x_start if x_start is not None else 0
        x1 = x_end if x_end is not None else self.num_bars
        width = x1 - x0
        height = zone["upper"] - zone["lower"]

        rect = mpatches.FancyBboxPatch(
            (x0, zone["lower"]),
            width,
            height,
            boxstyle="square,pad=0",
            facecolor=color,
            edgecolor=color,
            alpha=alpha,
            label=f"{label} zone",
        )
        self.ax.add_patch(rect)
        # Draw a thin centre line
        self.ax.axhline(
            zone["price"],
            color=color,
            linestyle="-",
            linewidth=1.2,
            alpha=0.9,
        )

    def add_all_zones(self, levels: dict, alpha: float = 0.25):
        """
        Draw all available level zones from a levels dict.

        Args:
            levels: Output of ``Levels.get_all_levels()``.
            alpha: Fill opacity.
        """
        for zone_type, zone_data in levels.items():
            if zone_data is not None:
                self.add_zone(zone_data, zone_type=zone_type, alpha=alpha)
