"""
Backtest Layer Demonstration - Complete Strategy Evaluation

Demonstrates end-to-end backtest workflow:
1. Generate synthetic market data (504 trading days, ~2 years)
2. Compute individual signals (basis, gap, momentum)
3. Aggregate signals with custom weights
4. Run backtest with entry/exit rules and transaction costs
5. Compute comprehensive performance metrics:
   - Risk-adjusted returns (Sharpe, Sortino, Calmar ratios)
   - Drawdown analysis
   - Win rate and profit factor
   - Trade statistics and holding periods
6. Analyze trade history and exposure distribution

Output: Performance metrics, P&L analysis, trade-by-trade details

Configuration:
  - Entry threshold: 1.5 (absolute z-score)
  - Exit threshold: 0.75 (absolute z-score)
  - Position size: $10MM notional
  - Transaction cost: 1.0 bps
  - DV01: $4,750 per $1MM notional
"""

import logging

from example_data import generate_example_data
from macrocredit.models import (
    aggregate_signals,
    compute_cdx_etf_basis,
    compute_cdx_vix_gap,
    compute_spread_momentum,
    AggregatorConfig,
    SignalConfig,
)
from macrocredit.backtest import (
    BacktestConfig,
    run_backtest,
    compute_performance_metrics,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run complete backtest demonstration."""
    print("\n" + "=" * 70)
    print("CDX OVERLAY STRATEGY - BACKTEST DEMONSTRATION")
    print("=" * 70)

    # 1. Generate market data
    print("\n[1] Generating market data...")
    cdx_df, vix_df, etf_df = generate_example_data(
        start_date="2023-01-01",
        periods=504,
    )
    print(f"    Generated {len(cdx_df)} days of synthetic data")

    # 2. Compute signals
    print("\n[2] Computing individual signals...")
    signal_config = SignalConfig(lookback=20, min_periods=10)

    basis = compute_cdx_etf_basis(cdx_df, etf_df, signal_config)
    gap = compute_cdx_vix_gap(cdx_df, vix_df, signal_config)
    momentum = compute_spread_momentum(cdx_df, signal_config)

    print(f"    CDX-ETF basis: {basis.notna().sum()} valid observations")
    print(f"    CDX-VIX gap: {gap.notna().sum()} valid observations")
    print(f"    Spread momentum: {momentum.notna().sum()} valid observations")

    # 3. Aggregate signals
    print("\n[3] Aggregating signals into composite score...")
    agg_config = AggregatorConfig(
        cdx_etf_basis_weight=0.4,
        cdx_vix_gap_weight=0.4,
        spread_momentum_weight=0.2,
    )

    composite = aggregate_signals(basis, gap, momentum, agg_config)
    print(f"    Composite signal: mean={composite.mean():.3f}, std={composite.std():.3f}")
    print(f"    Range: [{composite.min():.2f}, {composite.max():.2f}]")

    # 4. Run backtest
    print("\n[4] Running backtest...")
    backtest_config = BacktestConfig(
        entry_threshold=1.5,
        exit_threshold=0.75,
        position_size=10.0,  # $10MM notional
        transaction_cost_bps=1.0,
        max_holding_days=None,
        dv01_per_million=4750.0,
    )

    result = run_backtest(composite, cdx_df["spread"], backtest_config)

    print(f"\n    Backtest period: {result.metadata['summary']['start_date']} to "
          f"{result.metadata['summary']['end_date']}")
    print(f"    Total trades: {result.metadata['summary']['n_trades']}")
    print(f"    Total P&L: ${result.metadata['summary']['total_pnl']:,.0f}")
    print(f"    Avg P&L per trade: ${result.metadata['summary']['avg_pnl_per_trade']:,.0f}")

    # 5. Compute performance metrics
    print("\n[5] Computing performance metrics...")
    metrics = compute_performance_metrics(result.pnl, result.positions)

    print("\n" + "-" * 70)
    print("PERFORMANCE SUMMARY")
    print("-" * 70)
    print(f"  Sharpe Ratio:           {metrics.sharpe_ratio:>8.2f}")
    print(f"  Sortino Ratio:          {metrics.sortino_ratio:>8.2f}")
    print(f"  Calmar Ratio:           {metrics.calmar_ratio:>8.2f}")
    print(f"  Max Drawdown:           ${metrics.max_drawdown:>8,.0f}")
    print(f"  Total Return:           ${metrics.total_return:>8,.0f}")
    print(f"  Annualized Return:      ${metrics.annualized_return:>8,.0f}")
    print(f"  Annualized Volatility:  ${metrics.annualized_volatility:>8,.0f}")
    print("-" * 70)
    print(f"  Hit Rate:               {metrics.hit_rate:>8.1%}")
    print(f"  Average Win:            ${metrics.avg_win:>8,.0f}")
    print(f"  Average Loss:           ${metrics.avg_loss:>8,.0f}")
    print(f"  Win/Loss Ratio:         {metrics.win_loss_ratio:>8.2f}")
    print(f"  Number of Trades:       {metrics.n_trades:>8}")
    print(f"  Avg Holding Days:       {metrics.avg_holding_days:>8.1f}")
    print("-" * 70)

    # 6. Show sample trades
    print("\n[6] Sample trade history (first 10 position changes):")
    print("-" * 70)

    position_changes = result.positions[result.positions["position"].diff().fillna(0) != 0]
    sample_trades = position_changes.head(10)

    for date, row in sample_trades.iterrows():
        position_label = {1: "LONG", -1: "SHORT", 0: "FLAT"}[row["position"]]
        print(f"  {date.strftime('%Y-%m-%d')}: {position_label:>6} | "
              f"Signal: {row['signal']:>6.2f} | Spread: {row['spread']:>6.1f}")

    # 7. Show P&L distribution
    print("\n[7] P&L distribution (daily net P&L):")
    print("-" * 70)

    pnl_stats = result.pnl["net_pnl"].describe()
    print(f"  Mean:     ${pnl_stats['mean']:>10,.0f}")
    print(f"  Std Dev:  ${pnl_stats['std']:>10,.0f}")
    print(f"  Min:      ${pnl_stats['min']:>10,.0f}")
    print(f"  25%:      ${pnl_stats['25%']:>10,.0f}")
    print(f"  50%:      ${pnl_stats['50%']:>10,.0f}")
    print(f"  75%:      ${pnl_stats['75%']:>10,.0f}")
    print(f"  Max:      ${pnl_stats['max']:>10,.0f}")

    # 8. Exposure analysis
    print("\n[8] Exposure analysis:")
    print("-" * 70)

    total_days = len(result.positions)
    long_days = (result.positions["position"] == 1).sum()
    short_days = (result.positions["position"] == -1).sum()
    flat_days = (result.positions["position"] == 0).sum()

    print(f"  Long credit:     {long_days:>4} days ({long_days/total_days:>5.1%})")
    print(f"  Short credit:    {short_days:>4} days ({short_days/total_days:>5.1%})")
    print(f"  Flat:            {flat_days:>4} days ({flat_days/total_days:>5.1%})")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
