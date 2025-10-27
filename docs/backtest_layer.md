# Backtest Layer

**Purpose:** Simulate CDX overlay strategy performance by converting composite signals into positions and tracking P&L with realistic transaction costs.

**Status:** ✅ Implemented  
**Dependencies:** `models` (composite signals), `data` (market data)  
**Outputs:** Position history, P&L breakdown, performance metrics

---

## Overview

The backtest layer provides a **lightweight, transparent framework** for evaluating systematic credit strategies. It converts composite positioning scores into discrete trades, simulates P&L with transaction costs, and generates performance statistics.

### Design Philosophy

**Intentionally minimal** to maintain:
- **Transparency**: Every calculation is explicit and auditable
- **Modularity**: Clean interfaces between config, execution, and metrics
- **Testability**: Deterministic results with comprehensive test coverage
- **Extensibility**: Easy integration with frameworks like `vectorbt`, `backtrader`, `quantstats`

### Constraints (Pilot Phase)

- Daily frequency only (no intraday)
- Single instrument overlay (no portfolio allocation)
- Binary position sizing (on/off, no scaling)
- Fixed thresholds (no regime detection)
- Fixed transaction costs (no slippage modeling)

---

## Architecture

```
backtest/
  config.py          # BacktestConfig dataclass
  engine.py          # run_backtest() and BacktestResult
  metrics.py         # compute_performance_metrics() and PerformanceMetrics
  protocols.py       # BacktestEngine and PerformanceCalculator protocols
  adapters.py        # Example adapters for third-party libraries (stubs)
  __init__.py        # Public API exports
```

**Extensibility via Protocols:**

The backtest layer defines `Protocol` interfaces for swappable components:
- `BacktestEngine`: Interface for backtest implementations (allows swapping simple → vectorbt)
- `PerformanceCalculator`: Interface for metrics computation (allows swapping simple → quantstats)

This enables testing against multiple backends and gradual migration to professional libraries while maintaining the same domain-specific API.

### Data Flow

```
Composite Signal + CDX Spread + BacktestConfig
    ↓
run_backtest()
    ↓
BacktestResult (positions_df, pnl_df, metadata)
    ↓
compute_performance_metrics()
    ↓
PerformanceMetrics (sharpe, drawdown, hit rate, etc.)
```

---

## Core Components

### BacktestConfig

`@dataclass(frozen=True)` for backtest parameters and trading constraints.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entry_threshold` | `float` | `1.5` | Signal threshold for entering positions (absolute value) |
| `exit_threshold` | `float` | `0.75` | Signal threshold for exiting positions (absolute value) |
| `position_size` | `float` | `10.0` | Notional in millions ($10MM) |
| `transaction_cost_bps` | `float` | `1.0` | Round-trip cost in basis points |
| `max_holding_days` | `int \| None` | `None` | Max days to hold (None = no limit) |
| `dv01_per_million` | `float` | `4750.0` | DV01 per $1MM for P&L calc |

**Key Features:**
- Hysteresis: `entry_threshold > exit_threshold` reduces whipsaw
- Validation: `__post_init__()` enforces invariants
- Immutability: `frozen=True` for safe sharing

```python
from macrocredit.backtest import BacktestConfig

config = BacktestConfig(
    entry_threshold=2.0,
    exit_threshold=0.5,
    position_size=25.0,
    transaction_cost_bps=0.75,
)
```

---

### run_backtest

Core engine that converts signals to positions and computes P&L.

```python
def run_backtest(
    composite_signal: pd.Series,
    spread: pd.Series,
    config: BacktestConfig | None = None,
) -> BacktestResult:
    ...
```

**Position Logic:**
- Long (+1) when `signal > entry_threshold` (sell protection)
- Short (-1) when `signal < -entry_threshold` (buy protection)
- Exit when `|signal| < exit_threshold` or `days_held >= max_holding_days`

**P&L Calculation:**
- Spread P&L: Long profits from tightening, short profits from widening
  - `P&L = -position × ΔSpread × DV01 × position_size`
- Transaction costs: Applied on entry and exit
  - `Cost = transaction_cost_bps × position_size × 100`
- Net P&L: `Spread P&L - Costs`

**Implementation Details:**
- P&L calculated using `position_before_update` to correctly capture exit day profits
- Ensures final day's P&L is included when closing positions
- Trade P&L aggregation uses pandas groupby for clarity and performance

**Output:**
- `positions` DataFrame: signal, position, days_held, spread
- `pnl` DataFrame: spread_pnl, cost, net_pnl, cumulative_pnl
- `metadata` dict: config, summary (dates, trades, total P&L)

```python
from macrocredit.backtest import run_backtest
from macrocredit.models import aggregate_signals

composite = aggregate_signals(basis, gap, momentum, agg_config)
result = run_backtest(composite, cdx_df["spread"], config)

print(f"Trades: {result.metadata['summary']['n_trades']}")
print(f"Total P&L: ${result.metadata['summary']['total_pnl']:,.0f}")
```

---

### BacktestResult

`@dataclass` container for backtest outputs.

| Attribute | Type | Description |
|-----------|------|-------------|
| `positions` | `pd.DataFrame` | Position history (signal, position, days_held, spread) |
| `pnl` | `pd.DataFrame` | P&L breakdown (spread_pnl, cost, net_pnl, cumulative_pnl) |
| `metadata` | `dict` | Config and execution summary |

---

### compute_performance_metrics

Compute comprehensive performance statistics from backtest results.

```python
def compute_performance_metrics(
    pnl_df: pd.DataFrame,
    positions_df: pd.DataFrame,
) -> PerformanceMetrics:
    ...
```

**Calculation Details:**
- Annualization: 252 trading days, zero risk-free rate
- Metrics use daily P&L (not equity curve) for overlay strategies
- Trades identified by position changes from 0 → ±1

```python
metrics = compute_performance_metrics(result.pnl, result.positions)

print(f"Sharpe: {metrics.sharpe_ratio:.2f}")
print(f"Max DD: ${metrics.max_drawdown:,.0f}")
print(f"Hit Rate: {metrics.hit_rate:.1%}")
```

---

### PerformanceMetrics

`@dataclass` with comprehensive performance statistics.

| Metric | Type | Description |
|--------|------|-------------|
| `sharpe_ratio` | `float` | Annualized Sharpe (252 days, rf=0) |
| `sortino_ratio` | `float` | Downside deviation only |
| `max_drawdown` | `float` | Peak-to-trough decline ($) |
| `calmar_ratio` | `float` | Return / max drawdown |
| `total_return` | `float` | Total P&L ($) |
| `annualized_return` | `float` | Annualized P&L ($) |
| `annualized_volatility` | `float` | Annualized std ($) |
| `hit_rate` | `float` | Proportion of winning trades |
| `avg_win` | `float` | Average winning trade P&L ($) |
| `avg_loss` | `float` | Average losing trade P&L ($) |
| `win_loss_ratio` | `float` | `|avg_win / avg_loss|` |
| `n_trades` | `int` | Total round-trip trades |
| `avg_holding_days` | `float` | Average days per trade |

---

## Usage Patterns

### Basic Backtest

```python
from macrocredit.backtest import run_backtest, compute_performance_metrics

# Run with defaults
result = run_backtest(composite, cdx_df["spread"])
metrics = compute_performance_metrics(result.pnl, result.positions)

print(f"Sharpe: {metrics.sharpe_ratio:.2f}, Trades: {metrics.n_trades}")
```

### Parameter Sensitivity

```python
thresholds = [1.0, 1.5, 2.0, 2.5]
results = []

for threshold in thresholds:
    config = BacktestConfig(entry_threshold=threshold, exit_threshold=threshold / 2)
    result = run_backtest(composite, spread, config)
    metrics = compute_performance_metrics(result.pnl, result.positions)
    results.append({"threshold": threshold, "sharpe": metrics.sharpe_ratio})

print(pd.DataFrame(results))
```

### Walk-Forward Analysis

```python
# In-sample optimization
train_signal = composite.loc[:"2023-12-31"]
train_spread = spread.loc[:"2023-12-31"]

best_config = None
best_sharpe = -999

for threshold in [1.0, 1.5, 2.0]:
    config = BacktestConfig(entry_threshold=threshold)
    result = run_backtest(train_signal, train_spread, config)
    metrics = compute_performance_metrics(result.pnl, result.positions)
    if metrics.sharpe_ratio > best_sharpe:
        best_sharpe = metrics.sharpe_ratio
        best_config = config

# Out-of-sample validation
test_signal = composite.loc["2024-01-01":]
test_spread = spread.loc["2024-01-01":]
oos_result = run_backtest(test_signal, test_spread, best_config)
oos_metrics = compute_performance_metrics(oos_result.pnl, oos_result.positions)

print(f"In-sample: {best_sharpe:.2f}, Out-of-sample: {oos_metrics.sharpe_ratio:.2f}")
```

---

## Testing Strategy

### Unit Tests (`tests/backtest/test_engine.py`)

- Deterministic position updates with known signals
- P&L calculation accuracy with synthetic spreads
- Transaction cost application on entry/exit
- Threshold hysteresis behavior
- Edge cases (empty data, single trade, no trades)

### Integration Tests

- End-to-end signal → backtest → metrics pipeline
- Consistency between backtest summary and metrics
- Handling of missing data and alignment

### Reproducibility

All backtests deterministic given same inputs:
- Identical results across multiple runs
- Metadata captures all parameters
- No hidden state or random dependencies

---

## Best Practices

### Use Configuration Objects

✅ **Good:**
```python
config = BacktestConfig(entry_threshold=1.5, exit_threshold=0.75)
result = run_backtest(signal, spread, config)
```

### Log Metadata for Reproducibility

```python
from macrocredit.persistence import save_json

result = run_backtest(signal, spread, config)
save_json(result.metadata, "backtest_run_20250126.json")
```

### Validate Inputs

```python
assert signal.index.equals(spread.index), "Misaligned indices"
assert not signal.isna().all(), "Signal is all NaN"
assert (spread > 0).all(), "Invalid negative spreads"
```

---

## Troubleshooting

### No Trades Generated

**Causes:** Signal never exceeds threshold, alignment issues, all NaN

**Solution:**
```python
print(f"Signal range: [{signal.min():.2f}, {signal.max():.2f}]")
print(f"Entry threshold: {config.entry_threshold}")
print(f"Valid values: {signal.notna().sum()}")
```

### High Transaction Costs

**Causes:** Too many trades, costs set too high

**Solution:**
```python
position_changes = result.positions["position"].diff().fillna(0)
turnover = (position_changes != 0).sum() / len(result.positions)
print(f"Turnover: {turnover:.1%}")

# Increase thresholds to reduce trades
config = BacktestConfig(entry_threshold=2.0, exit_threshold=1.0)
```

### Negative Sharpe

**Causes:** Signal convention mismatch, P&L error, poor signals

**Solution:**
```python
# Check P&L by position direction
pnl_by_pos = result.pnl.join(result.positions["position"])
print(pnl_by_pos.groupby("position")["net_pnl"].agg(["mean", "sum"]))

# Try inverting if needed
result_inverted = run_backtest(-composite, spread, config)
```

---

## Extension Points

### Risk Limits

```python
# Add stop-loss to position loop
if current_trade_pnl < -max_loss_per_trade:
    current_position = 0  # Force exit
```

### Dynamic Position Sizing

```python
@dataclass(frozen=True)
class DynamicBacktestConfig(BacktestConfig):
    min_position_size: float = 5.0
    max_position_size: float = 25.0
    sizing_mode: str = "signal_strength"
```

### Integration with Professional Libraries

The backtest layer provides `Protocol` interfaces for seamless integration:

```python
# Example: Using protocols to swap backends
from macrocredit.backtest import BacktestEngine, PerformanceCalculator

# Define custom adapter implementing BacktestEngine protocol
class VectorBTEngine:
    """Adapter wrapping vectorbt to match our API."""
    
    def run(
        self,
        composite_signal: pd.Series,
        spread: pd.Series,
        config: BacktestConfig | None = None,
    ) -> BacktestResult:
        # Convert to vectorbt format, run, convert back
        ...

# Use it transparently
engine = VectorBTEngine()
result = engine.run(signal, spread, config)  # Same API, different backend

# See backtest/adapters.py for stub implementations
```

**Benefits:**
1. **Testing**: Compare results from simple vs. sophisticated engines
2. **Migration**: Start simple, swap in optimized implementations later
3. **Independence**: Not locked into any specific framework

---

## API Reference

```python
from macrocredit.backtest import (
    BacktestConfig,          # Configuration
    run_backtest,            # Core engine
    BacktestResult,          # Output container
    compute_performance_metrics,  # Metrics computation
    PerformanceMetrics,      # Metrics container
    BacktestEngine,          # Protocol for backtest implementations
    PerformanceCalculator,   # Protocol for metrics computation
)
```

### Protocols for Extensibility

```python
from macrocredit.backtest import BacktestEngine, PerformanceCalculator

# Our implementation follows these protocols
result = run_backtest(signal, spread, config)  # Implements BacktestEngine
metrics = compute_performance_metrics(result.pnl, result.positions)  # Implements PerformanceCalculator

# Future: Swap in professional libraries (stubs in adapters.py)
# from macrocredit.backtest.adapters import VectorBTEngine
# engine = VectorBTEngine()
# result = engine.run(signal, spread, config)
```

---

## Related Documentation

- [models_layer.md](models_layer.md) — Signal generation and aggregation
- [data_layer.md](data_layer.md) — Market data loading and transformation
- [persistence_layer.md](persistence_layer.md) — Saving backtest results

---

**Maintainer:** stabilefrisur  
**Last Updated:** October 27, 2025
