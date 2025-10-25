"""
Configuration module for paths, constants, and environment settings.

Defines project-wide constants including instrument universe, data paths,
and default parameters for the CDX overlay strategy.
"""

from pathlib import Path
from typing import Final

# Project root and data directories
PROJECT_ROOT: Final[Path] = Path(__file__).parent.parent.parent
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
REGISTRY_PATH: Final[Path] = DATA_DIR / "registry.json"
LOGS_DIR: Final[Path] = PROJECT_ROOT / "logs"

# Instrument universe for CDX overlay strategy
CDX_INSTRUMENTS: Final[dict[str, list[str]]] = {
    "IG": ["5Y", "10Y"],  # Investment Grade
    "HY": ["5Y"],  # High Yield
    "XO": ["5Y"],  # Crossover
}

# ETF proxies for signal generation (not direct trading)
ETF_TICKERS: Final[list[str]] = ["HYG", "LQD"]

# Market data identifiers
MARKET_DATA_TICKERS: Final[dict[str, str]] = {
    "VIX": "^VIX",
    "SPX": "^GSPC",
}

# Default signal parameters
DEFAULT_SIGNAL_PARAMS: Final[dict[str, int | float]] = {
    "momentum_window": 5,
    "volatility_window": 20,
    "z_score_window": 60,
    "basis_threshold": 0.5,
}

# Data versioning
DATA_VERSION: Final[str] = "0.1.0"


def ensure_directories() -> None:
    """
    Create required directories if they don't exist.

    Creates data, logs, and other necessary directories for the project.
    Safe to call multiple times.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "raw").mkdir(exist_ok=True)
    (DATA_DIR / "processed").mkdir(exist_ok=True)


# Initialize directories on module import
ensure_directories()
