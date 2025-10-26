# Backtest Layer

The backtest module provides a lightweight, transparent framework for simulating CDX overlay strategy performance. It converts composite signals into positions and tracks P&L with realistic transaction costs and constraints.

## Design Philosophy

This implementation is **intentionally minimal** to maintain:
- **Transparency**: Every calculation is explicit and auditable
- **Modularity**: Clean interfaces allow wrapping external libraries later
- **Testability**: Deterministic results with comprehensive test coverage
- **Extensibility**: Easy to add risk limits, alternative position sizing, etc.

The design accommodates future integration with more powerful frameworks like `vectorbt`, `backtrader`, or `quantstats` without requiring a complete rewrite.

## Core Components

### `BacktestConfig`
Configuration for backtest parameters and trading constraints.

```python
from macrocredit.backtest import BacktestConfig

config = BacktestConfig(
    entry_threshold=1.5,      # Signal level to enter position
    exit_threshold=0.75,      # Signal level to exit position
    position_size=10.0,       # Notional in millions ($10MM)
    transaction_cost_bps=1.0, # Round-trip cost in bps
    max_holding_days=None,    # Max days to hold (None = no limit)
    dv01_per_million=4750.0,  # DV01 per $1MM for P&L calc
)
```

**Key Features:**
- Hysteresis via `entry_threshold > exit_threshold` reduces whipsaw
- Simple binary positioning (on/off) for pilot phase
- Realistic transaction costs for CDX indices
- Optional time-based exit constraints

### `run_backtest`
Core engine that converts signals to positions and computes P&L.

```python
from macrocredit.backtest import run_backtest

result = run_backtest(
    composite_signal=composite_signal,  # Daily positioning scores
    spread=cdx_spread,                  # CDX spread levels
    config=config,
)
```

**Outputs:**
- `result.positions`: Position history (signal, position, days_held, spread)
- `result.pnl`: Daily P&L breakdown (spread_pnl, cost, net_pnl, cumulative_pnl)
- `result.metadata`: Configuration and summary statistics

**Position Logic:**
- Enter **long** (sell protection) when `signal > entry_threshold`
- Enter **short** (buy protection) when `signal < -entry_threshold`
- Exit when `|signal| < exit_threshold` or `days_held >= max_holding_days`
- No position scaling in pilot (binary ±1 or 0)

**P&L Calculation:**
- Long position: profits when spreads tighten
  - `P&L = -(spread_change) * DV01 * position_size`
- Short position: profits when spreads widen
  - `P&L = (spread_change) * DV01 * position_size`
- Transaction costs applied on entry and exit

### `compute_performance_metrics`
Comprehensive risk and performance statistics.

```python
from macrocredit.backtest import compute_performance_metrics

metrics = compute_performance_metrics(
    pnl_df=result.pnl,
    positions_df=result.positions,
)
```

**Metrics Included:**
- **Return-based**: Sharpe, Sortino, Calmar ratios
- **Risk-based**: Max drawdown, annualized volatility
- **Trade-based**: Hit rate, win/loss ratio, avg P&L per trade
- **Operational**: Number of trades, avg holding period

All metrics follow industry conventions (252 trading days, zero risk-free rate).

## Usage Example

### End-to-End Backtest

```python
import pandas as pd
from macrocredit.models import aggregate_signals, AggregatorConfig
from macrocredit.backtest import (
    BacktestConfig,
    run_backtest,
    compute_performance_metrics,
)

# Assume you have signals: basis, gap, momentum
# And market data: cdx_spread

# 1. Aggregate signals
composite = aggregate_signals(
    cdx_etf_basis=basis,
    cdx_vix_gap=gap,
    spread_momentum=momentum,
    config=AggregatorConfig(),
)

# 2. Configure backtest
backtest_config = BacktestConfig(
    entry_threshold=1.5,
    exit_threshold=0.75,
    position_size=10.0,
    transaction_cost_bps=1.0,
)

# 3. Run backtest
result = run_backtest(composite, cdx_spread, backtest_config)

# 4. Compute metrics
metrics = compute_performance_metrics(result.pnl, result.positions)

# 5. Analyze results
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
print(f"Max Drawdown: ${metrics.max_drawdown:,.0f}")
print(f"Hit Rate: {metrics.hit_rate:.1%}")
print(f"Total P&L: ${metrics.total_return:,.0f}")
```

### Accessing Trade History

```python
# Get all position changes (trades)
position_changes = result.positions[
    result.positions["position"].diff().fillna(0) != 0
]

# Get daily P&L statistics
daily_pnl_stats = result.pnl["net_pnl"].describe()

# Find max drawdown date
drawdown = result.pnl["cumulative_pnl"] - result.pnl["cumulative_pnl"].expanding().max()
max_dd_date = drawdown.idxmin()
```

## Implementation Notes

### Position Sizing
Current implementation uses **binary positioning** (±1 or 0):
- Simplifies pilot testing and reduces execution complexity
- Easy to extend to continuous sizing: `position = signal * scale_factor`
- Can add risk limits based on DV01, notional, or VaR

### P&L Mechanics
- **Spread P&L**: Calculated from daily spread changes while in position
- **Transaction costs**: Applied only on entry/exit, not carried daily
- **DV01 approximation**: Linear sensitivity assumption (valid for small moves)
- **No carry/roll**: Ignores coupon accrual and index roll dynamics

### Extensibility Points

This design makes it easy to:

1. **Wrap external libraries**:
   ```python
   # Example: Convert to vectorbt format
   import vectorbt as vbt
   
   positions_array = result.positions["position"].values
   spread_returns = cdx_spread.pct_change()
   
   portfolio = vbt.Portfolio.from_signals(
       close=spread_returns,
       entries=positions_array == 1,
       exits=positions_array == 0,
   )
   ```

2. **Add risk constraints**:
   ```python
   # In engine.py, add position sizing logic:
   if abs(current_dv01) > max_dv01:
       position_size *= (max_dv01 / abs(current_dv01))
   ```

3. **Implement alternative sizing**:
   ```python
   # Replace binary with continuous:
   position = np.clip(signal / entry_threshold, -1, 1)
   ```

## Testing

All components have comprehensive unit tests covering:
- Configuration validation
- Position generation logic
- P&L calculation accuracy
- Metrics computation
- Edge cases (no trades, all wins/losses, etc.)

Run tests:
```bash
pytest tests/backtest/ -v
```

## Future Enhancements

Potential extensions without architectural changes:

- **Multi-instrument**: Track positions across CDX IG/HY/XO
- **Dynamic sizing**: Scale position with signal strength or volatility
- **Risk limits**: DV01 caps, notional limits, drawdown stops
- **Roll management**: Handle index roll dates and OTR transitions
- **Regime detection**: Adjust thresholds based on market conditions
- **Walk-forward**: Rolling backtest windows for robustness testing

## Integration with Visualization

The `BacktestResult` structure is designed for easy plotting:

```python
import plotly.graph_objects as go

# Cumulative P&L chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=result.pnl.index,
    y=result.pnl["cumulative_pnl"],
    name="Cumulative P&L",
))

# Position overlay
fig.add_trace(go.Scatter(
    x=result.positions.index,
    y=result.positions["position"] * 100,  # Scale for visibility
    name="Position",
    yaxis="y2",
))
```

See `examples/backtest_demo.py` for a complete demonstration.
