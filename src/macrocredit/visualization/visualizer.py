"""
Visualizer class wrapping plotting functions for extensibility.

Provides object-oriented interface for future enhancements like
theming, caching, export utilities, and Streamlit integration.
"""

import logging

import pandas as pd
import plotly.graph_objects as go

from .plots import (
    plot_attribution,
    plot_dashboard,
    plot_drawdown,
    plot_equity_curve,
    plot_exposures,
    plot_signal,
)

logger = logging.getLogger(__name__)


class Visualizer:
    """
    Wrapper class for visualization functions with extensibility hooks.

    Provides unified interface for all plotting operations and future
    enhancements like custom themes, batch exports, or caching.

    Parameters
    ----------
    theme : str, default "plotly_white"
        Plotly template name for consistent styling.
    export_path : str | None
        Optional directory for automatic HTML/PNG export.

    Examples
    --------
    >>> viz = Visualizer()
    >>> fig = viz.equity_curve(daily_pnl)
    >>> fig.show()
    """

    def __init__(
        self,
        theme: str = "plotly_white",
        export_path: str | None = None,
    ) -> None:
        """Initialize visualizer with configuration."""
        self.theme = theme
        self.export_path = export_path
        logger.info("Visualizer initialized: theme=%s", theme)

    def equity_curve(
        self,
        pnl: pd.Series,
        title: str = "Cumulative P&L",
        show_drawdown_shading: bool = False,
    ) -> go.Figure:
        """
        Plot cumulative P&L equity curve.

        Delegates to plot_equity_curve with instance configuration.

        Parameters
        ----------
        pnl : pd.Series
            Daily P&L series with DatetimeIndex.
        title : str, default "Cumulative P&L"
            Chart title.
        show_drawdown_shading : bool, default False
            If True, shade drawdown regions.

        Returns
        -------
        go.Figure
            Plotly figure object.
        """
        fig = plot_equity_curve(pnl, title, show_drawdown_shading)
        fig.update_layout(template=self.theme)
        self._maybe_export(fig, "equity_curve")
        return fig

    def signal(
        self,
        signal: pd.Series,
        title: str | None = None,
        threshold_lines: list[float] | None = None,
    ) -> go.Figure:
        """
        Plot time series of a signal.

        Delegates to plot_signal with instance configuration.

        Parameters
        ----------
        signal : pd.Series
            Signal values with DatetimeIndex.
        title : str | None
            Chart title.
        threshold_lines : list[float] | None
            Horizontal reference lines.

        Returns
        -------
        go.Figure
            Plotly figure object.
        """
        fig = plot_signal(signal, title, threshold_lines)
        fig.update_layout(template=self.theme)
        self._maybe_export(fig, "signal")
        return fig

    def drawdown(
        self,
        pnl: pd.Series,
        title: str = "Drawdown",
        show_underwater_chart: bool = True,
    ) -> go.Figure:
        """
        Plot drawdown curve.

        Delegates to plot_drawdown with instance configuration.

        Parameters
        ----------
        pnl : pd.Series
            Daily P&L series with DatetimeIndex.
        title : str, default "Drawdown"
            Chart title.
        show_underwater_chart : bool, default True
            If True, displays as underwater chart.

        Returns
        -------
        go.Figure
            Plotly figure object.
        """
        fig = plot_drawdown(pnl, title, show_underwater_chart)
        fig.update_layout(template=self.theme)
        self._maybe_export(fig, "drawdown")
        return fig

    def attribution(
        self,
        signal_contributions: pd.DataFrame,
        title: str = "Signal Attribution",
    ) -> go.Figure:
        """
        Plot signal-level P&L attribution (placeholder).

        Parameters
        ----------
        signal_contributions : pd.DataFrame
            DatetimeIndex with columns for each signal's P&L.
        title : str, default "Signal Attribution"
            Chart title.

        Returns
        -------
        go.Figure
            Plotly figure object.

        Raises
        ------
        NotImplementedError
            Feature not yet implemented.
        """
        return plot_attribution(signal_contributions, title)

    def exposures(
        self,
        positions: pd.DataFrame,
        title: str = "Position Exposures",
    ) -> go.Figure:
        """
        Plot strategy exposures over time (placeholder).

        Parameters
        ----------
        positions : pd.DataFrame
            DatetimeIndex with exposure metrics.
        title : str, default "Position Exposures"
            Chart title.

        Returns
        -------
        go.Figure
            Plotly figure object.

        Raises
        ------
        NotImplementedError
            Feature not yet implemented.
        """
        return plot_exposures(positions, title)

    def dashboard(
        self,
        backtest_results: dict,
    ) -> go.Figure:
        """
        Generate comprehensive multi-panel dashboard (placeholder).

        Parameters
        ----------
        backtest_results : dict
            Dictionary with P&L, signals, positions, and metrics.

        Returns
        -------
        go.Figure
            Plotly figure with subplots.

        Raises
        ------
        NotImplementedError
            Feature not yet implemented.
        """
        return plot_dashboard(backtest_results)

    def _maybe_export(self, fig: go.Figure, name: str) -> None:
        """
        Export figure to HTML if export_path is configured.

        Parameters
        ----------
        fig : go.Figure
            Plotly figure to export.
        name : str
            Base filename (without extension).

        Notes
        -----
        Future enhancement for batch export and archival.
        """
        if self.export_path is not None:
            # Placeholder for export logic
            logger.debug("Export path configured but not yet implemented: %s", name)
