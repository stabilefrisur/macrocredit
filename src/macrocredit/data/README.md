# Data Layer Documentation

## Overview

The data layer provides robust, validated data loading and transformation for the Systematic Macro Credit strategy. It handles CDX indices, VIX volatility data, and credit ETF prices with standardized schemas and deterministic processing.

## Architecture

```
data/
├── __init__.py          # Public API
├── schemas.py           # Data schemas and constraints
├── validation.py        # Schema validation and quality checks
├── loader.py            # Parquet/CSV data loading
└── transform.py         # Data transformations and normalization
```

## Key Features

### 1. Type-Safe Data Loading

All loaders return validated DataFrames with:
- **DatetimeIndex**: Sorted, deduplicated timestamps
- **Schema compliance**: Required columns validated
- **Data quality**: Business logic constraints enforced
- **Format agnostic**: Supports Parquet and CSV

### 2. Data Validation

Three validation tiers:
1. **Structural**: Required columns present
2. **Type**: Correct data types and index
3. **Business logic**: Spreads/prices within valid ranges

### 3. Transformation Functions

Pure functions for common operations:
- Spread changes (diff/pct)
- Returns (simple/log)
- Series alignment (inner/outer)
- Rolling z-score normalization
- Resampling to daily frequency

## Usage Examples

### Loading CDX Data

```python
from macrocredit.data import load_cdx_data

# Load all CDX data
df = load_cdx_data("data/raw/cdx_spreads.parquet")

# Load specific index and tenor
df = load_cdx_data(
    "data/raw/cdx_spreads.parquet",
    index_name="CDX_IG",
    tenor="5Y"
)
```

### Loading VIX Data

```python
from macrocredit.data import load_vix_data

# Load VIX closing levels
df = load_vix_data("data/raw/vix.parquet")
```

### Loading ETF Data

```python
from macrocredit.data import load_etf_data

# Load all ETF data
df = load_etf_data("data/raw/etf_prices.parquet")

# Load specific ticker
df = load_etf_data("data/raw/etf_prices.parquet", ticker="HYG")
```

### Loading All Data at Once

```python
from macrocredit.data import load_all_data

data = load_all_data(
    cdx_path="data/raw/cdx_spreads.parquet",
    vix_path="data/raw/vix.parquet",
    etf_path="data/raw/etf_prices.parquet"
)

cdx_df = data["cdx"]
vix_df = data["vix"]
etf_df = data["etf"]
```

### Data Transformations

```python
from macrocredit.data import (
    compute_spread_changes,
    compute_returns,
    align_multiple_series,
    compute_rolling_zscore
)

# Compute spread changes
spread_changes = compute_spread_changes(
    cdx_df["spread"],
    window=1,
    method="diff"  # or "pct" for percentage
)

# Compute returns
vix_returns = compute_returns(
    vix_df["close"],
    window=1,
    log_returns=False
)

# Align multiple series
cdx_spread, vix_close = align_multiple_series(
    cdx_df["spread"],
    vix_df["close"],
    method="inner",  # Only common dates
    fill_method=None  # No forward/backward fill
)

# Normalize signals with z-score
signal = compute_rolling_zscore(
    spread_changes,
    window=20,
    min_periods=20
)
```

## Data Schemas

### CDX Schema

**Required columns:**
- `date`: Observation date (converted to DatetimeIndex)
- `spread`: CDX spread in basis points
- `index`: Index identifier (e.g., "CDX_IG_5Y")

**Optional columns:**
- `tenor`: Tenor string (e.g., "5Y", "10Y")
- `series`: CDX series number
- `volume`, `bid`, `ask`: Market microstructure data

**Constraints:**
- Spreads: 0 to 10,000 basis points
- No duplicate dates per index

### VIX Schema

**Required columns:**
- `date`: Observation date (converted to DatetimeIndex)
- `close`: VIX closing level

**Optional columns:**
- `open`, `high`, `low`: Intraday levels
- `volume`: Trading volume

**Constraints:**
- VIX: 0 to 200 (extreme stress cap)
- No duplicate dates

### ETF Schema

**Required columns:**
- `date`: Observation date (converted to DatetimeIndex)
- `close`: Closing price
- `ticker`: ETF ticker symbol

**Optional columns:**
- `open`, `high`, `low`: Intraday prices
- `volume`: Trading volume
- `adjusted_close`: Corporate action adjusted price

**Constraints:**
- Prices: 0 to 10,000 (sanity check)
- No duplicate dates per ticker

## Error Handling

All validation functions raise `ValueError` with descriptive messages:

```python
try:
    df = load_cdx_data("bad_data.parquet")
except ValueError as e:
    print(f"Validation failed: {e}")
    # Output: "Spread values outside valid range: ..."
```

## Best Practices

### 1. Use Parquet for Production
- Faster loading than CSV
- Type preservation
- Better compression

### 2. Validate Early
- Load and validate data before processing
- Let validation errors fail fast
- Log warnings for duplicates/anomalies

### 3. Preserve DatetimeIndex
- All functions expect and return DatetimeIndex
- Enables time-series operations
- Supports alignment and resampling

### 4. Use Pure Functions
- Transformations don't modify inputs
- Deterministic outputs for same inputs
- Easy to test and compose

### 5. Handle Missing Data Explicitly
- Don't auto-fill unless required
- Document fill methods when used
- Consider look-ahead bias

## Integration with Persistence Layer

The data layer uses the persistence layer for I/O:

```python
from macrocredit.persistence import save_parquet, load_parquet

# Save processed data
save_parquet(processed_df, "data/processed/cdx_clean.parquet")

# Load via data layer (adds validation)
df = load_cdx_data("data/processed/cdx_clean.parquet")
```

## Testing

Comprehensive tests cover:
- Schema validation (valid/invalid data)
- Loader functionality (Parquet/CSV)
- Transformations (edge cases, missing data)
- Error handling (missing columns, invalid values)

Run tests:
```bash
pytest tests/data/ -v
```

## Future Enhancements

Potential additions:
1. **Data fetching**: API integrations for live data
2. **Caching**: Cache validated DataFrames to avoid re-validation
3. **Streaming**: Handle large datasets with chunking
4. **Additional transforms**: Technical indicators, filters
5. **Data quality metrics**: Completeness, staleness tracking

## Related Documentation

- [Persistence Layer](../persistence/README.md)
- [CDX Overlay Strategy](../../docs/cdx_overlay_strategy.md)
- [Python Guidelines](../../docs/python_guidelines.md)
