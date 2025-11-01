# Project Status — aponyx

**Last Updated:** November 1, 2025  
**Version:** 0.1.0  
**Maintainer:** stabilefrisur

---

## Quick Reference

| Property | Value |
|----------|-------|
| **Project Type** | Systematic fixed-income research framework |
| **Primary Focus** | CDX overlay tactical credit strategies |
| **Python Version** | 3.12 (modern syntax, no legacy compatibility) |
| **Environment Manager** | `uv` |
| **Maturity Level** | Early-stage research framework |
| **License** | MIT |

**Core Dependencies:**
- `pandas>=2.2.0`, `numpy>=2.0.0`, `pyarrow>=17.0.0`, `xbbg>=0.7.0`

**Visualization:**
- `plotly>=5.24.0`, `streamlit>=1.39.0` (optional)

**Development Tools:**
- `pytest>=8.0.0`, `ruff>=0.6.0`, `black>=24.0.0`, `mypy>=1.11.0`

---

## Project Purpose

aponyx is a **systematic fixed-income research framework** for developing and backtesting tactical credit strategies. The project centers on a **CDX overlay pilot strategy** that exploits temporary dislocations in liquid credit indices to generate short-term tactical alpha.

**Core Investment Objectives:**
- Generate short-term tactical alpha (holding period: days to weeks)
- Provide liquidity hedge and modest convexity enhancement
- Maintain capital efficiency through derivatives overlay
- Create uncorrelated returns to slower-moving core credit allocation

**Research Philosophy:**
- Prioritize **signal evaluation independence** over premature signal combination
- Each signal backtested individually to establish clear performance attribution
- Reproducible research with deterministic outputs and metadata logging
- Modular architecture separating strategy logic from infrastructure

---

## Architecture Overview

The project implements a **strict layered architecture** with functional boundaries:

```
src/aponyx/
  data/               # Load, validate, transform market data
  models/             # Signal generation and strategy logic
  backtest/           # Simulation, P&L tracking, metrics
  visualization/      # Plotly charts, Streamlit dashboards
  persistence/        # Parquet/JSON I/O, data registry
  config/             # Paths, constants, defaults
```

### Layer Responsibilities

| Layer | Purpose | Can Import From | Cannot Import From |
|-------|---------|-----------------|-------------------|
| **data/** | Data loading, cleaning, validation | `config`, `persistence` | `models`, `backtest`, `visualization` |
| **models/** | Signal computation | `config`, `data` (schemas only) | `backtest`, `visualization` |
| **backtest/** | P&L simulation, metrics | `config`, `models` (protocols) | `data` (direct), `visualization` |
| **visualization/** | Charts, dashboards | None (accepts generic DataFrames) | `data`, `models`, `backtest` |
| **persistence/** | I/O operations | `config` | All others |
| **config/** | Constants, paths | None | All |

**Design Principles:**
1. **Modularity:** Layers are decoupled; data layer knows nothing about strategy logic
2. **Reproducibility:** Deterministic outputs with seed control and metadata logging
3. **Type Safety:** Strict type hints using modern Python syntax (`str | None`, `dict[str, Any]`)
4. **Simplicity:** Functions over classes; `@dataclass` for data containers
5. **Transparency:** Clear separation of strategy logic from infrastructure

---

## Implementation Status

### ✅ Data Layer (`src/aponyx/data/`)

**Implemented:**
- File-based data loading with Parquet support (`FileSource`)
- Bloomberg Terminal integration with xbbg wrapper (`BloombergSource`)
- Schema validation for CDX, VIX, ETF data (`validate_cdx_schema`, `validate_vix_schema`, `validate_etf_schema`)
- TTL-based caching system (`DataCache`)
- Data registry with metadata tracking (`DataRegistry`)
- Sample data generation for testing (`generate_sample_cdx`, `generate_sample_vix`, `generate_sample_etf`)
- Provider pattern with `DataSource` protocol (`sources.py`)
- Fetch functions: `fetch_cdx`, `fetch_vix`, `fetch_etf`

**Requirements:**
- Bloomberg integration requires active Bloomberg Terminal session
- xbbg wrapper included in standard dependencies

**Planned:**
- 🔜 REST API provider pattern

**Not in Scope:**
- ❌ Database integration (files only by design)
- ❌ Authentication/authorization (handled externally)

### ✅ Models Layer (`src/aponyx/models/`)

**Implemented:**
- Three pilot signals:
  - `compute_cdx_etf_basis` - Flow-driven mispricing from CDX-ETF basis
  - `compute_cdx_vix_gap` - Cross-asset risk sentiment divergence
  - `compute_spread_momentum` - Short-term continuation in spreads
- Signal registry pattern with JSON catalog (`SignalRegistry`, `signal_catalog.json`)
- Batch signal computation (`compute_registered_signals`)
- Configurable signal parameters (`SignalConfig` dataclass)
- Signal catalog management (`SignalCatalog` for registry operations)

**Key Files:**
- `signals.py` - Signal computation functions
- `registry.py` - Signal registry and batch computation
- `catalog.py` - Signal catalog management utilities
- `signal_catalog.json` - Signal metadata and configuration

**Planned:**
- 🔜 Additional signal ideas (expansion of catalog)
- 🔜 Multi-signal combination strategies

**Not in Scope:**
- ❌ Real-time signal generation (research framework only)

### ✅ Backtest Layer (`src/aponyx/backtest/`)

**Implemented:**
- Core backtesting engine (`run_backtest`)
- Position generation with entry/exit thresholds (`BacktestConfig`)
- P&L simulation with transaction costs
- Performance metrics calculation (`compute_performance_metrics`):
  - Sharpe, Sortino, Calmar ratios
  - Maximum drawdown and duration
  - Win rate, profit factor
  - Trade statistics and holding period analysis
- Metadata logging with timestamps and parameters (`BacktestResult`)
- Protocol-based adapters for signal/spread inputs (`adapters.py`)

**Key Files:**
- `engine.py` - Core backtest engine
- `metrics.py` - Performance calculations
- `config.py` - Configuration dataclasses
- `protocols.py` - Type protocols for inputs
- `adapters.py` - Input adaptation utilities

**Planned:**
- 🔜 Advanced position sizing (currently binary on/off)
- 🔜 Multi-asset portfolio backtesting

**Not in Scope:**
- ❌ Real-time trading integration
- ❌ Production risk management

### ✅ Persistence Layer (`src/aponyx/persistence/`)

**Implemented:**
- Parquet I/O with column filtering and date ranges (`save_parquet`, `load_parquet`)
- JSON I/O for metadata (`save_json`, `load_json`)
- Data registry system (`DataRegistry`)
- Comprehensive logging at INFO and DEBUG levels

**Key Files:**
- `parquet_io.py` - Parquet read/write operations
- `json_io.py` - JSON read/write operations
- `registry.py` - Data registry management

**Not in Scope:**
- ❌ Database backends (Parquet/JSON only by design)
- ❌ Cloud storage integration

### 🔜 Visualization Layer (`src/aponyx/visualization/`)

**Implemented:**
- Core plotting functions:
  - `plot_equity_curve` - Cumulative P&L chart
  - `plot_signal` - Signal values with entry/exit thresholds
  - `plot_drawdown` - Underwater chart
- `Visualizer` class for theme management
- Returns Plotly `Figure` objects (no auto-display)

**Planned:**
- 🔜 Signal attribution chart (`plot_attribution` - stub exists)
- 🔜 Position exposures chart (`plot_exposures` - stub exists)
- 🔜 Multi-panel dashboard (`plot_dashboard` - stub exists)
- 🔜 Streamlit dashboard (`app.py` contains only placeholder)

**Key Files:**
- `plots.py` - Plotting functions (partial implementation)
- `visualizer.py` - Theme and style management
- `app.py` - Streamlit dashboard (stub)

**Not in Scope:**
- ❌ Real-time data visualization
- ❌ Interactive parameter tuning UI

### ✅ Testing (`tests/`)

**Implemented:**
- Unit tests for all layers:
  - `tests/data/` - Data validation and loading
  - `tests/models/` - Signal computation, registry, catalog
  - `tests/backtest/` - Engine and metrics
  - `tests/persistence/` - I/O operations and registry
  - `tests/visualization/` - Plotting functions
- Deterministic test data with fixed seeds
- Pytest configuration with coverage tracking
- Comprehensive test coverage

**Testing Philosophy:**
- Test API contracts (return types, shapes, edge cases)
- Test determinism (same input → same output with fixed seeds)
- Test calculations (z-scores, P&L, metrics)
- Test error handling (missing columns, empty data)
- Do NOT test visual rendering or external services

### ✅ Documentation (`docs/`, `examples/`)

**Implemented:**
- Comprehensive design documents (8 files in `docs/`):
  - `cdx_overlay_strategy.md` - Investment strategy and signal definitions
  - `python_guidelines.md` - Code standards and best practices
  - `logging_design.md` - Logging conventions and metadata
  - `signal_registry_usage.md` - Signal management workflow
  - `visualization_design.md` - Chart architecture
  - `caching_design.md` - Cache layer architecture
  - `adding_data_providers.md` - Provider extension guide
  - `documentation_structure.md` - Single source of truth principles
- Runnable examples for each layer (`examples/`)
- NumPy-style docstrings throughout codebase
- Copilot instructions for AI-assisted development (`.github/copilot-instructions.md`)

**Documentation Structure (Single Source of Truth):**
- **API Reference:** Module docstrings
- **Quickstart:** `README.md`
- **Design Docs:** `docs/*.md`
- **Examples:** `examples/*.py`

---

## Design Patterns and Conventions

### 1. Signal Sign Convention

**All model signals follow consistent sign convention:**
- **Positive signal values** → Long credit risk → Buy CDX (sell protection)
- **Negative signal values** → Short credit risk → Sell CDX (buy protection)

**Rationale:** Ensures clear interpretation when evaluating signals individually or comparing performance across different signal ideas.

**Implementation:** See `src/aponyx/models/signals.py` for examples.

### 2. Signal Registry Pattern

Signals are managed via **JSON catalog** + **compute function registry**:

**Files:**
- `src/aponyx/models/signal_catalog.json` - Signal metadata
- `src/aponyx/models/registry.py` - Registry implementation
- `src/aponyx/models/catalog.py` - Catalog management

**Benefits:**
- Add new signals by editing JSON + implementing compute function
- No code changes to batch computation logic
- Easy enable/disable for experiments
- Clear metadata and data requirements

**Usage:**
```python
registry = SignalRegistry("src/aponyx/models/signal_catalog.json")
signals = compute_registered_signals(registry, market_data, config)
```

### 3. Provider Pattern for Data Sources

**Abstract `DataSource` protocol** supports multiple providers:

**Files:**
- `src/aponyx/data/sources.py` - Protocol definition
- `src/aponyx/data/providers/file.py` - File implementation
- `src/aponyx/data/providers/bloomberg.py` - Bloomberg Terminal implementation

**Current Implementations:**
- ✅ `FileSource` - Local Parquet/CSV files
- ✅ `BloombergSource` - Bloomberg Terminal via xbbg (requires active session)

**Example:**
```python
# File-based
source = FileSource("data/raw/cdx_data.parquet")
cdx_df = fetch_cdx(source, index_name="CDX_IG_5Y")

# Bloomberg Terminal
source = BloombergSource()
cdx_df = fetch_cdx(source, index_name="CDX_IG", tenor="5Y")
```

### 4. Functions Over Classes

**Default to pure functions** for transformations, calculations, and data processing.

**Only use classes for:**
1. State management (`DataRegistry`, connection pools)
2. Multiple related methods on shared state
3. Lifecycle management (context managers)
4. Plugin/interface patterns (base classes)

**Use `@dataclass` for data containers:**
- `SignalConfig` - Signal parameters
- `BacktestConfig` - Backtest configuration
- `BacktestResult` - Backtest outputs
- `PerformanceMetrics` - Performance statistics

**Files demonstrating this pattern:**
- `src/aponyx/models/signals.py` - Pure functions for signal computation
- `src/aponyx/backtest/config.py` - Dataclass configurations
- `src/aponyx/backtest/engine.py` - Functional backtest logic

### 5. Logging Standards

**Module-level loggers:**
```python
import logging
logger = logging.getLogger(__name__)
```

**%-formatting (not f-strings):**
```python
logger.info("Loaded %d rows from %s", len(df), path)
```

**Levels:**
- **INFO:** User-facing operations (file loaded, backtest started)
- **DEBUG:** Implementation details (filter applied, cache hit)
- **WARNING:** Recoverable errors (missing optional column)

**Never in library code:**
```python
logging.basicConfig(...)  # User's responsibility, not library's
```

**Examples:** See any module in `src/aponyx/` for consistent logging patterns.

### 6. Type Hints (Modern Python Syntax)

**Use built-in generics and union syntax:**
```python
def process_data(
    data: dict[str, Any],
    filters: list[str] | None = None,
    threshold: int | float = 0.0,
) -> pd.DataFrame | None:
    ...
```

**Avoid old syntax:**
```python
# ❌ Don't use: Optional, Union, List, Dict
from typing import Optional, Union, List, Dict
```

**Files:** All modules in `src/aponyx/` use modern type syntax.

---

## Data Flow and Workflow

**Typical Research Workflow:**

```
1. Data Loading
   FileSource("data/raw/cdx.parquet")
   → fetch_cdx(source, index_name="CDX_IG_5Y")
   → validate_cdx_schema(df)
   → Returns: pd.DataFrame with DatetimeIndex

2. Signal Generation
   SignalRegistry("signal_catalog.json")
   → compute_registered_signals(registry, market_data, config)
   → compute_cdx_etf_basis(cdx_df, etf_df, config)
   → Returns: dict[str, pd.Series] of signals

3. Backtesting (per signal)
   BacktestConfig(entry_threshold=1.5, ...)
   → run_backtest(signal, spread, config)
   → Returns: BacktestResult(positions, pnl, metadata)

4. Performance Analysis
   compute_performance_metrics(result.pnl, result.positions)
   → Returns: PerformanceMetrics(sharpe_ratio, max_drawdown, ...)

5. Visualization
   plot_equity_curve(result.pnl)
   → Returns: plotly.graph_objects.Figure
   → .show() or st.plotly_chart() for rendering
```

**Data Dependencies:**

```
market_data: dict[str, pd.DataFrame]
├─ "cdx": DataFrame with 'spread' column
├─ "vix": DataFrame with 'close' column
└─ "etf": DataFrame with 'close' column

↓ (passed to signal registry)

signals: dict[str, pd.Series]
├─ "cdx_etf_basis": z-score normalized signal
├─ "cdx_vix_gap": z-score normalized signal
└─ "spread_momentum": z-score normalized signal

↓ (evaluated individually)

BacktestResult for each signal
├─ positions: DataFrame (signal, position, days_held, spread)
├─ pnl: DataFrame (spread_pnl, cost, net_pnl, cumulative_pnl)
└─ metadata: dict (config, summary stats)

↓ (analyzed)

PerformanceMetrics
├─ sharpe_ratio, sortino_ratio, calmar_ratio
├─ max_drawdown, max_drawdown_duration
├─ total_return, avg_trade_pnl
└─ win_rate, profit_factor
```

**Key Files:**
- Data loading: `src/aponyx/data/fetch.py`
- Signal generation: `src/aponyx/models/registry.py`
- Backtesting: `src/aponyx/backtest/engine.py`
- Metrics: `src/aponyx/backtest/metrics.py`
- Visualization: `src/aponyx/visualization/plots.py`

---

## Notable Design Decisions

### 1. No Backward Compatibility

**Decision:** Use modern Python syntax without legacy support.

**Rationale:**
- Early-stage project allows adopting best practices immediately
- No legacy cruft or deprecated patterns
- Cleaner, more readable code

**Impact:** Use `str | None` not `Optional[str]`, `dict[str, Any]` not `Dict[str, Any]`, etc.

### 2. Files Only (No Databases)

**Decision:** Parquet/JSON only; no SQL, MongoDB, or other databases.

**Rationale:**
- Simplicity for research workflows
- Version control friendly (Parquet files in git LFS)
- No server dependencies
- Sufficient for pilot strategy data volumes

**Impact:** All persistence via `src/aponyx/persistence/parquet_io.py` and `json_io.py`.

### 3. Independent Signal Evaluation

**Decision:** Each signal backtested individually before combination.

**Rationale:**
- Establish clear performance attribution
- Understand signal behavior in isolation
- Avoid premature optimization through signal blending
- Enable apples-to-apples comparison on same backtest config

**Impact:** `compute_registered_signals` returns dict of signals; each evaluated separately.

### 4. Return Figures, Don't Display

**Decision:** Visualization functions return `plotly.graph_objects.Figure` without auto-display.

**Rationale:**
- Works in Jupyter, Streamlit, HTML export, testing
- Caller controls rendering context
- Enables post-processing (annotations, subplot composition)
- Testable without rendering

**Impact:** User must call `.show()` or `st.plotly_chart()` explicitly. See `src/aponyx/visualization/plots.py`.

### 5. TTL-Based Caching (Not LRU)

**Decision:** Simple time-based cache expiration, no size limits or LRU eviction.

**Rationale:**
- Predictable behavior for research workflows
- No complex invalidation logic
- Manual cleanup acceptable for single-user research

**Impact:** Cache grows until manual cleanup; no automatic eviction. See `src/aponyx/data/cache.py`.

### 6. No Authentication in Library

**Decision:** No credential management, API keys, or auth logic in library code.

**Rationale:**
- Connections established outside project (Bloomberg Terminal, APIs)
- Library assumes authenticated data access
- Security handled at infrastructure level

**Impact:** Providers accept connection parameters but don't implement auth.

### 7. Module-Level Loggers (Never `basicConfig`)

**Decision:** Use `logger = logging.getLogger(__name__)` in all modules; never call `logging.basicConfig()`.

**Rationale:**
- Library shouldn't force logging configuration on users
- Hierarchical logger names enable fine-grained control
- Works cleanly with pytest (no spurious output)

**Impact:** Applications configure logging, library uses module loggers. See `docs/logging_design.md`.

---

## Reproducibility and Metadata

**All stochastic operations use fixed seeds:**
```python
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
```

**All backtest runs include metadata:**
```python
metadata = {
    "timestamp": datetime.now().isoformat(),
    "version": __version__,
    "config": {...},
    "summary": {
        "start_date": str(aligned.index[0]),
        "end_date": str(aligned.index[-1]),
        "total_days": len(aligned),
        "n_trades": int(n_trades),
        "total_pnl": float(total_pnl),
    },
}
```

**Saved alongside results:**
```python
save_json(metadata, "logs/run_metadata.json")
```

**Files:**
- Sample data with fixed seeds: `src/aponyx/data/sample_data.py`
- Metadata logging: `src/aponyx/backtest/engine.py`
- Metadata I/O: `src/aponyx/persistence/json_io.py`

---

## Repository Structure

```
src/aponyx/           # Main package
  data/                    # Data loading, validation, caching
    providers/             # Provider implementations (file, bloomberg)
  models/                  # Signal computation and registry
  backtest/                # Backtesting engine and metrics
  visualization/           # Plotting and dashboards
  persistence/             # Parquet/JSON I/O
  config/                  # Constants and configuration

tests/                     # Unit tests (mirrors src/ structure)
  data/
  models/
  backtest/
  persistence/
  visualization/

examples/                  # Runnable demonstrations
  data_demo.py
  models_demo.py
  backtest_demo.py
  visualization_demo.py
  persistence_demo.py
  end_to_end_demo.ipynb

docs/                      # Design documentation
  cdx_overlay_strategy.md
  python_guidelines.md
  logging_design.md
  signal_registry_usage.md
  visualization_design.md
  caching_design.md
  adding_data_providers.md
  documentation_structure.md
  maintenance/             # Advanced workflows

data/                      # Data storage
  raw/                     # Source data files
  processed/               # Transformed data
  cache/                   # TTL-based cache

logs/                      # Run metadata and logs

.github/
  copilot-instructions.md  # AI assistant configuration

pyproject.toml             # Project metadata and dependencies
README.md                  # Quickstart guide
LICENSE                    # MIT license
```

---

## Next Steps (Inferred from Stubs)

1. Complete Streamlit dashboard implementation (`src/aponyx/visualization/app.py`)
2. Implement signal attribution and exposure charts (`plot_attribution`, `plot_exposures`)
3. Expand signal catalog with additional ideas
4. Multi-signal combination experiments

---

## Context for AI Assistants

This document provides comprehensive context for GPT-based AI assistants working on the aponyx project. When generating code or suggestions:

1. **Respect layer boundaries** - Data layer cannot import from models/backtest
2. **Use modern Python syntax** - `str | None`, `dict[str, Any]`, etc.
3. **Follow signal sign convention** - Positive = long credit risk
4. **Add module-level loggers** - Never use `logging.basicConfig()`
5. **Return figures, don't display** - Let caller control rendering
6. **Use functions over classes** - Default to pure functions
7. **Include type hints** - All function signatures fully typed
8. **Write NumPy-style docstrings** - Parameters, Returns, Notes sections
9. **Add tests for new features** - Deterministic tests with fixed seeds
10. **Log metadata for backtests** - Timestamp, version, config, summary stats

**Key reference files:**
- Architecture: This document (layer table, design patterns)
- Code standards: `.github/copilot-instructions.md`, `docs/python_guidelines.md`
- Investment context: `docs/cdx_overlay_strategy.md`
- Signal workflow: `docs/signal_registry_usage.md`
- Examples: `examples/*.py` for usage patterns

---

**End of Document**
