# Examples

Runnable demonstrations of the macrocredit framework using synthetic market data.

## Quick Start

```bash
# From project root
uv run python examples/backtest_demo.py      # Complete strategy backtest (504 days)
uv run python examples/models_demo.py        # Signal generation (252 days)
uv run python examples/visualization_demo.py # Interactive charts (requires viz extra)
uv run python examples/persistence_demo.py   # Data I/O and registry (209 days)
uv run python examples/data_demo.py          # Data loading and transformation
```

## Example Scripts

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `backtest_demo.py` | End-to-end backtest workflow | Metrics, trade history, transaction costs |
| `models_demo.py` | Signal generation workflow | Signal computation, statistics, positions |
| `visualization_demo.py` | Interactive plotting and dashboards | Equity curves, signals, drawdown charts |
| `persistence_demo.py` | Data I/O and registry management | Parquet files, metadata, registry queries |
| `data_demo.py` | Data loading and transformation | Schema validation, alignment, z-scores |

All scripts include inline comments explaining each step. See the script source code for detailed documentation.

## Test Data

All examples use **`example_data.py`** for consistent synthetic data generation:

```python
from example_data import generate_example_data

# Generate 252 days of synthetic CDX, VIX, and ETF data
cdx_df, vix_df, etf_df = generate_example_data(
    start_date="2024-01-01",
    periods=252,
    seed=42  # Reproducible results
)
```

## Extending Examples

### Creating New Examples

1. Import test data generator:
   ```python
   from example_data import generate_example_data
   ```

2. Generate synthetic data:
   ```python
   cdx_df, vix_df, etf_df = generate_example_data(periods=252, seed=42)
   ```

3. Demonstrate your feature with clear logging and comments

### Customizing Data

```python
# Different time ranges
generate_example_data(periods=63)    # 3 months
generate_example_data(periods=1260)  # 5 years

# Different dates
generate_example_data(start_date="2020-01-01")

# Different random paths
generate_example_data(seed=123)
```

## Best Practices

**Do:**
- Use `generate_example_data()` for consistency
- Keep examples focused on one layer
- Include logging and type hints
- Show realistic usage patterns

**Don't:**
- Duplicate data generation logic
- Mix concerns from multiple layers
- Create non-deterministic outputs
- Hardcode file paths

---

**Last Updated**: October 27, 2025
