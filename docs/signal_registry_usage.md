# Signal Registry Pattern - Usage Guide

## Overview

The signal registry infrastructure enables scalable signal research by decoupling signal definitions from aggregation logic. Add new signals by editing a JSON catalog instead of modifying code.

## Quick Start

### Basic Usage

```python
from pathlib import Path
from macrocredit.models import (
    SignalRegistry,
    SignalConfig,
    AggregatorConfig,
    compute_registered_signals,
    aggregate_signals,
)

# Load signal catalog
registry = SignalRegistry("src/macrocredit/models/signal_catalog.json")

# Prepare market data
market_data = {
    "cdx": cdx_df,  # Must have 'spread' column
    "vix": vix_df,  # Must have 'close' column
    "etf": etf_df,  # Must have 'close' column
}

# Compute all enabled signals
signal_config = SignalConfig(lookback=20, min_periods=10)
signals = compute_registered_signals(registry, market_data, signal_config)

# Aggregate with custom weights
weights = {
    "cdx_etf_basis": 0.50,
    "cdx_vix_gap": 0.30,
    "spread_momentum": 0.20,
}
composite = aggregate_signals(signals, weights)
```

## Adding a New Signal

### Step 1: Implement Compute Function

Add to `src/macrocredit/models/signals.py`:

```python
def compute_my_new_signal(
    cdx_df: pd.DataFrame,
    other_df: pd.DataFrame,
    config: SignalConfig | None = None,
) -> pd.Series:
    """
    Compute my new signal.
    
    Signal convention: positive = long credit risk (buy CDX).
    """
    if config is None:
        config = SignalConfig()
    
    logger.info("Computing my new signal: lookback=%d", config.lookback)
    
    # Your signal logic here
    raw_signal = ...
    
    # Z-score normalize
    normalized = (raw_signal - mean) / std
    
    logger.debug("Generated %d valid signals", normalized.notna().sum())
    return normalized
```

### Step 2: Register in Catalog

Edit `src/macrocredit/models/signal_catalog.json`:

```json
[
  {
    "name": "my_new_signal",
    "description": "Brief description of what this signal captures",
    "compute_function_name": "compute_my_new_signal",
    "data_requirements": {
      "cdx": "spread",
      "other": "column_name"
    },
    "arg_mapping": ["cdx", "other"],
    "default_weight": 0.25,
    "enabled": true
  }
]
```

### Step 3: Use Immediately

```python
# Registry automatically picks up the new signal
signals = compute_registered_signals(registry, market_data, config)
# Now includes "my_new_signal"
```

## Signal Catalog Schema

### SignalMetadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique signal identifier (snake_case) |
| `description` | string | Human-readable signal description |
| `compute_function_name` | string | Function name in `signals.py` module |
| `data_requirements` | dict | Map of data keys to required column names |
| `arg_mapping` | list | Ordered list of data keys for function arguments |
| `default_weight` | float | Default aggregation weight (0.0 to 1.0) |
| `enabled` | boolean | Whether to compute this signal |

### Example Entry

```json
{
  "name": "cdx_etf_basis",
  "description": "Flow-driven mispricing from CDX-ETF basis",
  "compute_function_name": "compute_cdx_etf_basis",
  "data_requirements": {
    "cdx": "spread",
    "etf": "close"
  },
  "arg_mapping": ["cdx", "etf"],
  "default_weight": 0.35,
  "enabled": true
}
```

## Experimentation Workflows

### Disable a Signal

Set `"enabled": false` in catalog JSON, then reload registry.

### Test Different Weights

```python
# Use catalog defaults
enabled = registry.get_enabled()
default_weights = {name: meta.default_weight for name, meta in enabled.items()}

# Try custom weights
custom_weights = {
    "cdx_etf_basis": 0.60,
    "cdx_vix_gap": 0.25,
    "spread_momentum": 0.15,
}

composite_default = aggregate_signals(signals, default_weights)
composite_custom = aggregate_signals(signals, custom_weights)
```

### Run Subset of Signals

Modify catalog to disable unwanted signals, or manually filter:

```python
# Compute all signals
all_signals = compute_registered_signals(registry, market_data, config)

# Use subset for aggregation
subset_signals = {
    "cdx_etf_basis": all_signals["cdx_etf_basis"],
    "spread_momentum": all_signals["spread_momentum"],
}

subset_weights = {
    "cdx_etf_basis": 0.7,
    "spread_momentum": 0.3,
}

composite = aggregate_signals(subset_signals, subset_weights)
```

## Architecture Benefits

### Before (Hardcoded)

- Adding signal requires:
  1. Modify `signals.py` (compute function)
  2. Modify `aggregator.py` (function signature, parameters)
  3. Modify `config.py` (add weight attribute)
  4. Update all call sites (pass new parameter)
  5. Update tests

### After (Registry Pattern)

- Adding signal requires:
  1. Modify `signals.py` (compute function)
  2. Edit `signal_catalog.json` (add entry)
  3. Done - everything else is automatic

### Scalability

- **3 signals**: Both approaches work fine
- **10 signals**: Hardcoded becomes unwieldy (10 function parameters)
- **20+ signals**: Registry pattern essential (single dict parameter)

## Integration with Backtesting

The backtest layer is already decoupled and requires no changes:

```python
from macrocredit.backtest import BacktestConfig, run_backtest

# Compute and aggregate signals
signals = compute_registered_signals(registry, market_data, signal_config)
composite = aggregate_signals(signals, weights)

# Backtest only needs composite signal
bt_config = BacktestConfig(
    entry_threshold=1.5,
    exit_threshold=0.75,
    position_size=10.0,
)

result = run_backtest(composite, market_data["cdx"]["spread"], bt_config)
```

## Testing New Signals

```python
import pytest
from macrocredit.models.signals import compute_my_new_signal
from macrocredit.models.config import SignalConfig

def test_my_new_signal():
    # Generate test data
    cdx_df = ...
    other_df = ...
    
    config = SignalConfig(lookback=10)
    signal = compute_my_new_signal(cdx_df, other_df, config)
    
    # Validate
    assert isinstance(signal, pd.Series)
    assert signal.notna().sum() > 0
    
    # Test signal convention: positive = long credit
    # (Add specific logic tests)
```

## Best Practices

1. **Always z-score normalize signals** for comparability across different data regimes
2. **Follow signal convention**: positive = long credit risk (buy CDX)
3. **Log operations** using module-level logger with %-formatting
4. **Validate data requirements** are met before computing
5. **Include signal description** in catalog for documentation
6. **Test determinism** to ensure reproducible results
7. **Use explicit arg_mapping** to avoid parameter order confusion

## Migration from Hardcoded Signals

Existing code using the old API can still work by calling compute functions directly:

```python
# Old way (still works)
from macrocredit.models import (
    compute_cdx_etf_basis,
    compute_cdx_vix_gap,
    compute_spread_momentum,
)

basis = compute_cdx_etf_basis(cdx_df, etf_df, config)
gap = compute_cdx_vix_gap(cdx_df, vix_df, config)
momentum = compute_spread_momentum(cdx_df, config)

# New way (registry pattern)
signals = compute_registered_signals(registry, market_data, config)
```

Both patterns coexist during migration period.
