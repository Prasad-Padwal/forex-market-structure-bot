"""Forex Market Structure Trading Bot package."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("forex-market-structure-bot")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = ["__version__"]
