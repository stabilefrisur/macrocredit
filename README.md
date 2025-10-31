# Systematic Macro Credit

A modular Python framework for developing and backtesting systematic credit strategies, starting with a **CDX overlay pilot strategy**.

## Quick Start

### Installation

Requires **Python 3.13+** and [`uv`](https://docs.astral.sh/uv/) for environment management.

```bash
# Clone repository
git clone https://github.com/stabilefrisur/macrocredit.git
cd macrocredit

# Install dependencies
uv sync

# Install visualization dependencies (optional)
uv sync --extra viz

# Run examples
uv run python examples/backtest_demo.py
```

### Basic Usage

```python
from macrocredit.data import fetch_cdx, fetch_etf, FileSource
from macrocredit.models import compute_cdx_etf_basis, SignalConfig
from macrocredit.backtest import run_backtest, BacktestConfig

# Load market data with validation
cdx_df = fetch_cdx(FileSource("data/raw/cdx_data.parquet"), index_name="CDX_IG_5Y")
etf_df = fetch_etf(FileSource("data/raw/etf_data.parquet"), ticker="HYG")

# Generate signal
signal_config = SignalConfig(lookback=20, min_periods=10)
signal = compute_cdx_etf_basis(cdx_df, etf_df, signal_config)

# Run backtest
backtest_config = BacktestConfig(entry_threshold=1.5, exit_threshold=0.75)
results = run_backtest(signal, cdx_df["spread"], backtest_config)
print(f"Sharpe Ratio: {results.metrics['sharpe_ratio']:.2f}")
```

## Project Structure

```
macrocredit/
├── src/macrocredit/       # Core framework
│   ├── data/              # Data loading, validation, transformation
│   ├── models/            # Signal generation for credit strategies
│   ├── backtest/          # Backtesting engine and metrics
│   ├── visualization/     # Plotly charts and Streamlit dashboard
│   ├── persistence/       # Parquet/JSON I/O and registry
│   └── config/            # Configuration and constants
├── examples/              # Runnable demonstrations
├── tests/                 # Unit tests
└── docs/                  # Architecture and design docs
```

### Key Layers

| Layer | Purpose | Entry Point |
|-------|---------|-------------|
| **Data** | Load, validate, transform market data | `macrocredit.data` |
| **Models** | Generate signals for independent evaluation | `macrocredit.models` |
| **Backtest** | Simulate execution and compute metrics | `macrocredit.backtest` |
| **Visualization** | Interactive charts and dashboards | `macrocredit.visualization` |
| **Persistence** | Save/load data with metadata registry | `macrocredit.persistence` |

## Documentation

- **[CDX Overlay Strategy](docs/cdx_overlay_strategy.md)** - Investment thesis and pilot implementation
- **[Python Guidelines](docs/python_guidelines.md)** - Code standards and best practices
- **[Logging Design](docs/logging_design.md)** - Logging conventions and metadata tracking
- **[Examples](examples/)** - Runnable demos for each layer

## Features

✅ **Type-safe data loading** with schema validation  
✅ **Modular signal framework** with composable transformations  
✅ **Deterministic backtesting** with transaction cost modeling  
✅ **Interactive visualization** with Plotly charts (equity, signals, drawdown)  
✅ **Parquet-based persistence** with JSON metadata registry  
✅ **Comprehensive logging** with run metadata tracking

## Development

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=macrocredit --cov-report=term-missing

# Specific module
uv run pytest tests/models/
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

### Examples

Each example demonstrates a specific layer with synthetic data:

```bash
uv run python examples/data_demo.py          # Data loading and transformation
uv run python examples/models_demo.py        # Signal generation
uv run python examples/backtest_demo.py      # Complete backtest workflow
uv run python examples/visualization_demo.py # Interactive charts (requires viz extra)
uv run python examples/persistence_demo.py   # Data I/O and registry
```

## Design Principles

1. **Modularity** - Separate data, models, backtest, and persistence layers
2. **Reproducibility** - Deterministic outputs with seed control and metadata logging
3. **Type safety** - Strict type hints and runtime validation
4. **Simplicity** - Prefer functions over classes, explicit over implicit
5. **Transparency** - Clear separation between strategy logic and infrastructure

## Architecture Notes

### Signal Convention

All model signals follow a **consistent sign convention**:
- **Positive values** → Long credit risk (buy CDX / sell protection)
- **Negative values** → Short credit risk (sell CDX / buy protection)

This convention ensures clear interpretation when evaluating signals individually
or when combining signals in future experiments.

### Data Flow

```
Raw Data (Parquet/CSV)
    ↓
Data Layer (load, validate, transform)
    ↓
Models Layer (signal computation)
    ↓
Backtest Layer (simulation, metrics)
    ↓
Persistence Layer (save results, metadata)
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

This is a research project under active development. See [Python Guidelines](docs/python_guidelines.md) for code standards.

---

**Maintained by stabilefrisur**  
Version 0.1.0 | Last Updated: October 27, 2025
