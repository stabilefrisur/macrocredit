# Examples

Demonstration scripts showing how to use the macrocredit framework for systematic credit strategies.

## Overview

Each example script demonstrates a specific layer of the framework using synthetic market data. All examples use centralized data generation from `example_data.py` to ensure consistency and reproducibility.

## Quick Start

Run examples directly from this directory:

```bash
cd examples
python models_demo.py
python backtest_demo.py
python persistence_demo.py
python data_demo.py
```

## Examples

### `models_demo.py`
**Purpose**: Demonstrate the models layer for signal generation and aggregation.

**What it shows**:
- Computing individual signals (CDX-ETF basis, CDX-VIX gap, spread momentum)
- Aggregating signals with custom weights
- Generating position recommendations from composite signals
- Signal statistics and position distribution

**Dataset**: 252 days (1 year) of synthetic CDX, VIX, and HYG data

**Output**: Signal values, position classifications, and summary statistics

---

### `backtest_demo.py`
**Purpose**: Demonstrate the backtest layer for strategy evaluation.

**What it shows**:
- Signal computation and aggregation
- Running a complete backtest with entry/exit rules
- Computing performance metrics (Sharpe, Sortino, Calmar, drawdown)
- Trade history and position tracking
- Transaction costs and holding period analysis

**Dataset**: 504 days (2 years) of synthetic data for robust statistics

**Output**: Performance metrics, trade history, P&L analysis

---

### `persistence_demo.py`
**Purpose**: Demonstrate the persistence layer for data I/O and registry management.

**What it shows**:
- Saving and loading Parquet files
- Managing a data registry with metadata
- Filtering datasets by instrument and date range
- Saving/loading JSON metadata and run artifacts
- Registry queries and dataset discovery

**Dataset**: 209 days with multiple instruments (CDX IG, CDX HY, VIX, HYG)

**Output**: Parquet files in `data/raw/`, registry in `data/registry.json`

---

### `data_demo.py`
**Purpose**: Demonstrate the data layer for loading and transformation.

**What it shows**:
- Loading CDX, VIX, and ETF data from files
- Computing spread changes and returns
- Aligning multiple time series
- Computing rolling z-scores for normalization
- Data validation and schema checking

**Dataset**: Uses `generate_full_sample_dataset()` to create raw Parquet files

**Output**: Transformed data and validation results

---

## Centralized Test Data

All examples use **`example_data.py`** for consistent synthetic data generation.

### Main Functions

#### `generate_example_data(start_date, periods, seed)`
Universal dataset generator for all examples.

**Parameters**:
- `start_date`: Start date (default: "2024-01-01")
- `periods`: Number of trading days (default: 252)
- `seed`: Random seed for reproducibility (default: 42)

**Returns**: `(cdx_df, vix_df, etf_df)` with date-indexed DataFrames

**Common usage**:
```python
# Standard 1-year dataset
cdx, vix, etf = generate_example_data()

# Extended 2-year dataset for backtests
cdx, vix, etf = generate_example_data(
    start_date="2023-01-01",
    periods=504
)
```

#### `generate_persistence_data(start_date, periods, seed)`
Extended dataset for persistence layer demonstrations.

**Returns**: Dictionary with `cdx_ig_5y`, `cdx_hy_5y`, `vix`, `hyg_etf` DataFrames

**Features**: Includes volume data and multiple instruments for registry demos

---

## Data Characteristics

All synthetic data uses realistic market dynamics:

### CDX IG 5Y
- Base spread: 100 bp
- Volatility: 5 bp daily
- Dynamics: Mean-reverting with drift

### VIX
- Base level: 15
- Volatility: 2-3 points daily
- Dynamics: Mean-reverting with occasional spikes

### HYG ETF
- Base price: $100
- Volatility: 5 bp daily
- Dynamics: Geometric Brownian motion

### CDX HY 5Y (persistence demos only)
- Base spread: 350 bp
- Volatility: 20 bp daily
- Dynamics: Mean-reverting with higher volatility

---

## Design Principles

### Consistency
All examples use the same data generation logic from `example_data.py`. This ensures:
- Reproducible results across examples
- Consistent market dynamics and parameters
- Single source of truth for test data

### Modularity
Each example focuses on a single layer:
- **Data layer**: Loading, transformation, validation
- **Models layer**: Signal computation, aggregation
- **Backtest layer**: Strategy evaluation, metrics
- **Persistence layer**: I/O, registry, metadata

### Simplicity
Examples demonstrate clean, idiomatic usage:
- Minimal boilerplate
- Clear separation of concerns
- Type-annotated, documented code
- Realistic but simple synthetic data

---

## Running Examples

### Requirements
All examples require the macrocredit package and dependencies installed:

```bash
# From project root
pip install -e .
```

Or using `uv`:

```bash
uv pip install -e .
```

### Execution
Examples automatically add `src/` to the Python path, so they can be run directly:

```bash
cd examples
python models_demo.py
```

### Output
Examples log to stdout and create files in `data/` and `logs/` directories:
- **Parquet files**: `data/raw/` and `data/processed/`
- **Metadata**: `data/registry.json`
- **Run logs**: `logs/run_metadata.json`

---

## Extending Examples

### Creating New Examples

1. Import from `example_data`:
   ```python
   from example_data import generate_example_data
   ```

2. Generate test data:
   ```python
   cdx_df, vix_df, etf_df = generate_example_data(periods=252)
   ```

3. Demonstrate your layer/feature using the framework

4. Follow project conventions:
   - Type hints
   - NumPy-style docstrings
   - Logging with `logger.info()` (not f-strings)
   - Clean separation of concerns

### Customizing Data

For specialized examples, you can:

1. **Adjust time range**: Change `periods` parameter
   ```python
   # Short demo (3 months)
   generate_example_data(periods=63)
   
   # Long backtest (5 years)
   generate_example_data(periods=1260)
   ```

2. **Use different dates**: Change `start_date`
   ```python
   generate_example_data(start_date="2020-01-01")
   ```

3. **Modify seed**: For different synthetic paths
   ```python
   generate_example_data(seed=123)
   ```

4. **Add custom instruments**: Extend `generate_persistence_data()` or call generators directly from `macrocredit.data.sample_data`

---

## Best Practices

### Do
- ✅ Use `generate_example_data()` for consistency
- ✅ Log operations with `logging` module
- ✅ Keep examples focused on one layer
- ✅ Include docstrings and type hints
- ✅ Show realistic usage patterns

### Don't
- ❌ Duplicate data generation logic
- ❌ Mix concerns from multiple layers
- ❌ Use production database connections
- ❌ Create non-deterministic outputs
- ❌ Hardcode file paths

---

## Troubleshooting

### Import errors
If you see `ModuleNotFoundError: No module named 'macrocredit'`:

```bash
# Install package in development mode
cd /path/to/macrocredit
pip install -e .
```

### Missing directories
Examples create directories automatically, but ensure project structure exists:

```bash
mkdir -p data/raw data/processed logs
```

### Data inconsistencies
All examples use `seed=42` by default for reproducibility. If results differ, verify:
- Same package version
- Same Python version (3.13)
- Same dependency versions

---

## Additional Resources

- **Project README**: `../README.md` - Overall project documentation
- **Strategy docs**: `../docs/cdx_overlay_strategy.md` - Investment strategy details
- **Layer docs**: `../docs/{data,models,backtest,persistence}_layer.md` - Layer specifications
- **Python guidelines**: `../docs/python_guidelines.md` - Coding standards
- **Copilot instructions**: `../.github/copilot-instructions.md` - AI assistant configuration

---

## Contributing

When adding new examples:

1. Use `example_data.py` for data generation
2. Follow existing example structure
3. Document what the example demonstrates
4. Include clear output and logging
5. Keep examples under 200 lines if possible
6. Test that examples run successfully

---

**Last Updated**: October 26, 2025  
**Maintainer**: stabilefrisur
