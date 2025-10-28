"""
Core plotting functions for backtest analysis and signal visualization.

All functions return Plotly figure objects for flexible rendering
(Streamlit, Jupyter, HTML export, etc.).
"""

import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


def plot_equity_curve(
    pnl: pd.Series,
    title: str = "Cumulative P&L",
    show_drawdown_shading: bool = False,
) -> go.Figure:
    """
    Plot cumulative P&L equity curve over time.

    Parameters
    ----------
    pnl : pd.Series
        Daily P&L series with DatetimeIndex.
    title : str, default "Cumulative P&L"
        Chart title.
    show_drawdown_shading : bool, default False
        If True, shade drawdown regions in red.

    Returns
    -------
    go.Figure
        Plotly figure object ready for display or export.

    Notes
    -----
    Cumulative P&L is computed as cumsum of input series.
    Returns interactive chart with hover tooltips and zoom controls.
    """
    logger.info("Plotting equity curve: %d observations", len(pnl))

    cumulative_pnl = pnl.cumsum()

    fig = px.line(
        x=cumulative_pnl.index,
        y=cumulative_pnl.values,
        labels={"x": "Date", "y": "Cumulative P&L"},
        title=title,
    )

    fig.update_traces(line=dict(color="steelblue", width=2))
    fig.update_layout(
        hovermode="x unified",
        template="plotly_white",
        showlegend=False,
    )

    if show_drawdown_shading:
        running_max = cumulative_pnl.cummax()
        drawdown = cumulative_pnl - running_max
        in_drawdown = drawdown < 0

        # Add shaded regions for drawdowns
        for start_idx in range(len(in_drawdown)):
            if in_drawdown.iloc[start_idx] and (
                start_idx == 0 or not in_drawdown.iloc[start_idx - 1]
            ):
                # Find end of drawdown period
                end_idx = start_idx
                while end_idx < len(in_drawdown) and in_drawdown.iloc[end_idx]:
                    end_idx += 1

                fig.add_vrect(
                    x0=cumulative_pnl.index[start_idx],
                    x1=cumulative_pnl.index[min(end_idx, len(in_drawdown) - 1)],
                    fillcolor="red",
                    opacity=0.1,
                    layer="below",
                    line_width=0,
                )

    logger.debug("Equity curve plot generated successfully")
    return fig


def plot_signal(
    signal: pd.Series,
    title: str | None = None,
    threshold_lines: list[float] | None = None,
) -> go.Figure:
    """
    Plot time series of a single signal (typically z-score normalized).

    Parameters
    ----------
    signal : pd.Series
        Signal values with DatetimeIndex.
    title : str | None
        Chart title. Defaults to signal name if available.
    threshold_lines : list[float] | None
        Horizontal reference lines (e.g., [-2, 2] for z-score thresholds).

    Returns
    -------
    go.Figure
        Plotly figure object with signal trace and optional threshold lines.

    Notes
    -----
    Designed for z-score normalized signals with typical ranges [-3, 3].
    Use threshold_lines to mark regime boundaries or trading rules.
    """
    logger.info("Plotting signal: %d observations", len(signal))

    if title is None:
        title = getattr(signal, "name", "Signal")

    fig = px.line(
        x=signal.index,
        y=signal.values,
        labels={"x": "Date", "y": "Signal Value"},
        title=title,
    )

    fig.update_traces(line=dict(color="darkorange", width=1.5))
    fig.update_layout(
        hovermode="x unified",
        template="plotly_white",
        showlegend=False,
    )

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    # Add threshold lines if specified
    if threshold_lines:
        for threshold in threshold_lines:
            fig.add_hline(
                y=threshold,
                line_dash="dot",
                line_color="red",
                opacity=0.4,
                annotation_text=f"±{abs(threshold)}",
            )

    logger.debug("Signal plot generated successfully")
    return fig


def plot_drawdown(
    pnl: pd.Series,
    title: str = "Drawdown",
    show_underwater_chart: bool = True,
) -> go.Figure:
    """
    Plot drawdown curve over time (peak-to-trough decline).

    Parameters
    ----------
    pnl : pd.Series
        Daily P&L series with DatetimeIndex.
    title : str, default "Drawdown"
        Chart title.
    show_underwater_chart : bool, default True
        If True, displays as underwater equity chart (negative values).
        If False, displays as percentage decline from peak.

    Returns
    -------
    go.Figure
        Plotly figure object showing drawdown evolution.

    Notes
    -----
    Drawdown is computed as current cumulative P&L minus running maximum.
    Always non-positive (zero at peaks, negative in drawdown).
    """
    logger.info("Plotting drawdown: %d observations", len(pnl))

    cumulative_pnl = pnl.cumsum()
    running_max = cumulative_pnl.cummax()
    drawdown = cumulative_pnl - running_max

    if not show_underwater_chart:
        # Convert to percentage decline
        drawdown = (drawdown / running_max.replace(0, 1)) * 100

    fig = px.area(
        x=drawdown.index,
        y=drawdown.values,
        labels={
            "x": "Date",
            "y": "Drawdown (%)" if not show_underwater_chart else "Drawdown",
        },
        title=title,
    )

    fig.update_traces(
        line=dict(color="crimson", width=1),
        fillcolor="rgba(220, 20, 60, 0.3)",
    )

    fig.update_layout(
        hovermode="x unified",
        template="plotly_white",
        showlegend=False,
    )

    # Add zero line
    fig.add_hline(y=0, line_dash="solid", line_color="black", opacity=0.3)

    max_dd = drawdown.min()
    logger.debug("Drawdown plot generated: max_dd=%.2f", max_dd)
    return fig


def plot_attribution(
    signal_contributions: pd.DataFrame,
    title: str = "Signal Attribution",
) -> go.Figure:
    """
    Plot signal-level P&L attribution over time.

    Parameters
    ----------
    signal_contributions : pd.DataFrame
        DatetimeIndex with columns for each signal's P&L contribution.
    title : str, default "Signal Attribution"
        Chart title.

    Returns
    -------
    go.Figure
        Plotly figure object with stacked area chart.

    Notes
    -----
    Placeholder for future implementation.
    Intended for decomposing composite strategy P&L by signal.
    """
    raise NotImplementedError("Signal attribution plotting not yet implemented")


def plot_exposures(
    positions: pd.DataFrame,
    title: str = "Position Exposures",
) -> go.Figure:
    """
    Plot strategy exposures over time (notional, delta, etc.).

    Parameters
    ----------
    positions : pd.DataFrame
        DatetimeIndex with columns for exposure metrics.
    title : str, default "Position Exposures"
        Chart title.

    Returns
    -------
    go.Figure
        Plotly figure object with multi-line chart.

    Notes
    -----
    Placeholder for future implementation.
    Intended for risk management and position monitoring.
    """
    raise NotImplementedError("Exposure plotting not yet implemented")


def plot_dashboard(
    backtest_results: dict,
) -> go.Figure:
    """
    Generate comprehensive multi-panel dashboard.

    Parameters
    ----------
    backtest_results : dict
        Dictionary containing P&L, signals, positions, and metrics.

    Returns
    -------
    go.Figure
        Plotly figure with subplots (equity, drawdown, signals, exposures).

    Notes
    -----
    Placeholder for future implementation.
    Intended for integrated view of all backtest outputs.
    """
    raise NotImplementedError("Dashboard plotting not yet implemented")
