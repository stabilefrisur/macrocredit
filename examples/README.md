# Examples

Runnable demonstrations of the aponyx framework using synthetic market data.

## Prerequisites

- Python 3.12 with `uv` environment manager
- Core dependencies: `pandas`, `numpy` (installed via `uv sync`)
- Optional: visualization dependencies (`uv sync --extra viz` for plotting demos)

## Quick Start

```bash
# From project root, ensure dependencies are installed
uv sync

# Run demonstrations
uv run python examples/data_demo.py          # Data loading and transformation
uv run python examples/models_demo.py        # Signal generation (252 days)
uv run python examples/backtest_demo.py      # Complete strategy backtest (504 days)
uv run python examples/persistence_demo.py   # Data I/O and registry (209 days)

# Visualization demo (requires viz extra)
uv sync --extra viz
uv run python examples/visualization_demo.py # Interactive charts
```

## Example Scripts

| Script | Purpose | Key Features | Expected Output |
|--------|---------|--------------|-----------------|
| `data_demo.py` | Data loading and transformation | Schema validation, alignment, z-scores | Prints data shapes, statistics |
| `models_demo.py` | Signal generation workflow | Signal computation, statistics, positions | Signal stats, correlation matrix |
| `backtest_demo.py` | End-to-end backtest workflow | Metrics, trade history, transaction costs | Sharpe ratio, max drawdown, trade count |
| `persistence_demo.py` | Data I/O and registry management | Parquet files, metadata, registry queries | File paths, registry entries |
| `visualization_demo.py` | Interactive plotting and dashboards | Equity curves, signals, drawdown charts | Plotly interactive HTML charts |

All scripts include inline comments explaining each step. See the script source code for detailed documentation.

## Expected Behavior

### Successful Output
Each demo prints structured information about the operations performed:

```bash
# data_demo.py
INFO - Fetching CDX data...
INFO - Loaded 252 rows...
CDX shape: (252, 2)

# backtest_demo.py  
INFO - Starting backtest...
Sharpe Ratio: 0.85
Max Drawdown: $15,234
Total Trades: 42
```

### Common Issues

**Import Error:** "No module named 'aponyx'"
```bash
# Solution: Install package in development mode
uv sync
```

**Missing Visualization Dependencies**
```bash
# Error: "No module named 'plotly'" when running visualization_demo.py
# Solution: Install optional visualization extras
uv sync --extra viz
```

**Data Directory Errors**
```bash
# Error: "data/processed/ directory not found"
# Solution: Demos create directories automatically, but ensure write permissions
```

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

**Customization:**
- Change `periods=` for different time ranges (63 = 3 months, 1260 = 5 years)
- Change `start_date=` for different date ranges
- Change `seed=` for different random paths (use fixed seeds for reproducibility)

## Extending Examples

### Creating New Examples

1. Import test data generator:
   ```python
   from example_data import generate_example_data
   ```

2. Generate synthetic data with fixed seed:
   ```python
   cdx_df, vix_df, etf_df = generate_example_data(periods=252, seed=42)
   ```

3. Demonstrate your feature with clear logging and comments

4. Add script description to this README

### Best Practices

**Do:**
- Use `generate_example_data()` for consistency
- Keep examples focused on one layer or feature
- Include logging output to explain operations
- Use type hints in example code
- Show realistic usage patterns

**Don't:**
- Duplicate data generation logic across scripts
- Mix concerns from multiple layers in one demo
- Create non-deterministic outputs (always use fixed seeds)
- Hardcode file paths (use `Path` from `pathlib`)

---

**Last Updated**: October 31, 2025
