# Models Layer

## Overview

The models layer implements signal generation and strategy logic for the systematic CDX overlay pilot. It follows a **functional design** with pure, composable signal functions.

## Naming Convention

**IMPORTANT:** Signal names must be used consistently throughout the module:

- **Signal names:** `cdx_etf_basis`, `cdx_vix_gap`, `spread_momentum`
- **Function names:** `compute_cdx_etf_basis`, `compute_cdx_vix_gap`, `compute_spread_momentum`
- **Function parameters:** `cdx_etf_basis`, `cdx_vix_gap`, `spread_momentum`
- **Config attributes:** `cdx_etf_basis_weight`, `cdx_vix_gap_weight`, `spread_momentum_weight`
- **DataFrame columns:** `cdx_etf_basis`, `cdx_vix_gap`, `spread_momentum`

This consistency ensures clarity across signal computation, aggregation, configuration, and testing.

## Architecture

```
models/
  __init__.py          # Public API exports
  config.py            # Configuration dataclasses
  signals.py           # Individual signal functions
  aggregator.py        # Signal combination logic
  README.md            # This file
```

## Core Components

### Signal Functions (`signals.py`)

Three pure functions implementing the pilot strategy signals:

1. **`compute_cdx_etf_basis`**: CDX-ETF pricing gap signal
   - Captures flow-driven mispricing between CDX index and ETF
   - Positive = CDX cheap (long credit risk)
   - Negative = CDX expensive (short credit risk)

2. **`compute_cdx_vix_gap`**: Cross-asset risk sentiment divergence
   - Identifies CDX-VIX stress mismatches
   - Positive = credit stress outpacing equity stress (long credit risk)
   - Negative = equity stress outpacing credit stress (short credit risk)

3. **`compute_spread_momentum`**: Short-term spread continuation
   - Volatility-adjusted 5-10 day momentum
   - Positive = tightening momentum (long credit risk)
   - Negative = widening momentum (short credit risk)

All signals return **z-score normalized** series for comparability.

### Aggregation (`aggregator.py`)

- **`aggregate_signals`**: Combines signals using weighted average
- Returns composite positioning score (z-score units)
- Typical range: -3 to +3
- Threshold-based positioning logic applied downstream

### Configuration (`config.py`)

Two immutable dataclasses:

- **`SignalConfig`**: Lookback windows and validation parameters
- **`AggregatorConfig`**: Signal weights and position thresholds

## Usage Example

```python
from macrocredit.data.loader import load_cdx_data, load_vix_data, load_etf_data
from macrocredit.models import (
    compute_cdx_etf_basis,
    compute_cdx_vix_gap,
    compute_spread_momentum,
    aggregate_signals,
    SignalConfig,
    AggregatorConfig,
)

# Load data
cdx_df = load_cdx_data("data/raw/cdx_ig_5y.parquet")
vix_df = load_vix_data("data/raw/vix.parquet")
etf_df = load_etf_data("data/raw/hyg.parquet")

# Configure signals
signal_config = SignalConfig(lookback=20, min_periods=10)

# Generate individual signals
basis_signal = compute_cdx_etf_basis(cdx_df, etf_df, signal_config)
vix_signal = compute_cdx_vix_gap(cdx_df, vix_df, signal_config)
mom_signal = compute_spread_momentum(cdx_df, signal_config)

# Aggregate into composite score
agg_config = AggregatorConfig(
    cdx_etf_basis_weight=0.35,
    cdx_vix_gap_weight=0.35,
    spread_momentum_weight=0.30,
    threshold=1.5,
)
composite = aggregate_signals(basis_signal, vix_signal, mom_signal, agg_config)

# Apply position logic
positions = composite.apply(
    lambda x: "short_credit" if x > agg_config.threshold
    else "long_credit" if x < -agg_config.threshold
    else "neutral"
)
```

## Design Principles

1. **Pure Functions**: No side effects, deterministic outputs
2. **Type Safety**: Full type hints for all parameters and returns
3. **Configuration**: Immutable dataclasses for reproducibility
4. **Logging**: INFO for operations, DEBUG for statistics
5. **Normalization**: All signals in comparable z-score units

## Signal Characteristics

| Signal | Horizon | Nature | Typical Range |
|--------|---------|--------|---------------|
| ETF-CDX Basis | 5-10 days | Mean-reverting | ±2.5 σ |
| VIX-CDX Gap | 3-7 days | Regime shifts | ±3.0 σ |
| Spread Momentum | 3-10 days | Continuation/fade | ±2.0 σ |

## Testing

See `tests/models/` for unit tests covering:
- Signal computation accuracy
- Edge cases (missing data, insufficient periods)
- Configuration validation
- Aggregation logic

## Future Extensions (Post-Pilot)

- Multi-tenor signal generation
- Regime-dependent weight adjustment
- Signal decay functions
- Risk-adjusted position sizing
- Signal diagnostics and reporting

---

**Last Updated**: October 26, 2025  
**Maintainer**: stabilefrisur
