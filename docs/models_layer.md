# Models Layer Design — Signal Generation Standards

## Overview

The models layer implements signal generation logic for systematic credit strategies. This document defines architectural standards, design patterns, and the critical **signal sign convention**.

---

## Signal Sign Convention

### Core Principle

**All signals must follow a uniform directional convention:**

```
Positive signal value  →  Long credit risk  →  Buy CDX  →  Sell protection
Negative signal value  →  Short credit risk →  Sell CDX →  Buy protection
```

### Rationale

1. **Aggregation clarity**: Weighted averages of signals maintain interpretability
2. **Risk management**: Position limits apply consistently across all signals
3. **Backtesting transparency**: Composite scores directly map to positions
4. **Human intuition**: Positive = bullish credit, negative = bearish credit

### Implementation Requirements

When implementing any signal:

1. **Verify directionality** with simple test cases
2. **Document interpretation** in function docstring
3. **Use negation** when raw calculations produce inverse signs
4. **Normalize consistently** using z-scores or similar methods
5. **Follow naming convention**: Use consistent signal names across functions, parameters, config attributes, and DataFrame columns

### Signal Naming Convention

**CRITICAL:** Signal names must be used consistently throughout the models layer:

- **Signal names:** `cdx_etf_basis`, `cdx_vix_gap`, `spread_momentum`
- **Function names:** `compute_cdx_etf_basis`, `compute_cdx_vix_gap`, `compute_spread_momentum`
- **Function parameters:** `cdx_etf_basis`, `cdx_vix_gap`, `spread_momentum`
- **Config attributes:** `cdx_etf_basis_weight`, `cdx_vix_gap_weight`, `spread_momentum_weight`
- **DataFrame columns:** `cdx_etf_basis`, `cdx_vix_gap`, `spread_momentum`

This naming consistency ensures:
- Clear traceability from signal generation through aggregation
- Self-documenting code with unambiguous parameter mappings
- Easier debugging and maintenance
- Consistent testing patterns

### Current Signal Implementations

| Signal | Raw Calculation | Sign Adjustment | Interpretation |
|--------|----------------|-----------------|----------------|
| **CDX-ETF Basis** | `CDX - ETF` spreads | None (natural) | Positive = CDX cheap (wide spreads) |
| **CDX-VIX Gap** | `CDX_dev - VIX_dev` | None (natural) | Positive = credit stress > equity stress |
| **Spread Momentum** | `-(spread_t - spread_{t-n})` | **Negated** | Positive = spreads tightening |

### Example: Spread Momentum

```python
def compute_spread_momentum(cdx_df: pd.DataFrame, config: SignalConfig) -> pd.Series:
    """
    Compute short-term volatility-adjusted momentum in CDX spreads.
    
    Positive signal suggests long credit risk (spreads tightening, momentum favorable).
    Negative signal suggests short credit risk (spreads widening, momentum unfavorable).
    """
    spread = cdx_df["spread"]
    spread_change = spread - spread.shift(config.lookback)
    
    # Negate because widening (positive change) should be negative signal
    rolling_std = spread.rolling(window=config.lookback).std()
    signal = -spread_change / rolling_std  # Note the negation
    
    return signal


# Usage in aggregator with consistent naming
def aggregate_signals(
    cdx_etf_basis: pd.Series,
    cdx_vix_gap: pd.Series,
    spread_momentum: pd.Series,
    config: AggregatorConfig | None = None,
) -> pd.Series:
    """Parameters use exact signal names for clarity."""
    config = config or AggregatorConfig()
    
    composite = (
        cdx_etf_basis * config.cdx_etf_basis_weight
        + cdx_vix_gap * config.cdx_vix_gap_weight
        + spread_momentum * config.spread_momentum_weight
    )
    return composite
```

---

## Architectural Principles

### 1. Functional Design

- **Prefer pure functions** over stateful classes
- Each signal is a standalone function with clear inputs/outputs
- No side effects (except logging)
- Deterministic given the same inputs

### 2. Configuration Management

- Use `@dataclass(frozen=True)` for signal parameters
- Default values suitable for pilot strategies
- All config passed explicitly (no globals)

### 3. Normalization Standards

- **Z-score normalization** is the default
- Use rolling windows for regime independence
- Document window sizes and min_periods clearly
- Handle insufficient data gracefully (return NaN)

### 4. Data Alignment

- All signals return `pd.Series` with DatetimeIndex
- Missing data forward-filled where appropriate
- Common dates handled via `reindex()` or joins
- No assumptions about data frequency (daily expected)

---

## Signal Quality Standards

### Required Elements

Every signal function must include:

1. **Type hints** on all parameters and return values
2. **NumPy-style docstring** with Parameters, Returns, Notes sections
3. **Logging**: INFO for computation start, DEBUG for statistics
4. **Validation**: Check for required columns, sufficient data
5. **Tests**: At least basic smoke tests and determinism checks

### Docstring Template

```python
def compute_signal_name(
    input_df: pd.DataFrame,
    config: SignalConfig | None = None,
) -> pd.Series:
    """
    Brief one-line description.

    Detailed explanation of what the signal captures and why it matters.
    MUST include interpretation: what positive/negative values mean.

    Parameters
    ----------
    input_df : pd.DataFrame
        Description including required columns.
    config : SignalConfig | None
        Configuration parameters. Uses defaults if None.

    Returns
    -------
    pd.Series
        Z-score normalized signal with DatetimeIndex.

    Notes
    -----
    - Implementation details
    - Normalization approach
    - Edge case handling
    """
```

### Testing Standards

Minimum test coverage for each signal:

1. **Structure test**: Returns pd.Series of correct length
2. **Normalization test**: Approximate z-score properties (mean ~0, std ~1)
3. **Edge case test**: Handles insufficient data (returns NaN)
4. **Determinism test**: Same inputs produce identical outputs
5. **Sign test**: Simple synthetic data verifies positive = bullish

---

## Signal Aggregation

### Weighted Combination

The `aggregate_signals()` function combines individual signals:

```python
composite = w1 * signal1 + w2 * signal2 + w3 * signal3
```

**Requirements:**
- Weights must sum to 1.0 (validated in `AggregatorConfig`)
- All input signals must be z-score normalized
- Output preserves z-score interpretation
- Missing values in ANY signal produce NaN in composite

### Position Mapping

```python
# Signal convention: positive = long credit risk (buy CDX)
if composite > threshold:
    position = "long_credit"   # Buy CDX, sell protection
elif composite < -threshold:
    position = "short_credit"  # Sell CDX, buy protection
else:
    position = "neutral"
```

---

## Future Extensions

Potential enhancements for post-pilot development:

1. **Multi-tenor signals**: Generate signals across 5Y, 7Y, 10Y tenors
2. **Regime detection**: Adjust signal weights based on market regime
3. **Signal decay**: Exponential weighting for time-decaying signals
4. **Confidence scores**: Probabilistic signal strength metrics
5. **Cross-validation**: Out-of-sample signal performance tracking

---

## Checklist for New Signals

Before adding a new signal to the models layer:

- [ ] Function follows naming convention: `compute_<signal_name>`
- [ ] Signal name used consistently across functions, parameters, config, and DataFrames
- [ ] Sign convention verified: positive = long credit risk
- [ ] Full type hints on all parameters and return
- [ ] Complete NumPy-style docstring with interpretation
- [ ] Logging at INFO level for computation, DEBUG for stats
- [ ] Configuration via `SignalConfig` dataclass
- [ ] Z-score normalization with rolling windows
- [ ] At least 3 unit tests (structure, determinism, edge cases)
- [ ] Added to `__init__.py` exports
- [ ] README.md updated with signal description
- [ ] Demo script or example provided

---

**Maintained by**: stabilefrisur  
**Version**: 1.0  
**Last Updated**: October 26, 2025
