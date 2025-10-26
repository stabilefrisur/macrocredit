"""Tests for data loader functionality."""

import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from macrocredit.data.loader import (
    load_cdx_data,
    load_vix_data,
    load_etf_data,
    load_all_data,
)
from macrocredit.persistence.parquet_io import save_parquet

logger = logging.getLogger(__name__)


@pytest.fixture
def sample_cdx_data() -> pd.DataFrame:
    """Create sample CDX data for testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    return pd.DataFrame(
        {
            "date": dates,
            "spread": 100 + pd.Series(range(100)).apply(lambda x: x * 0.5),
            "index": ["CDX_IG_5Y"] * 100,
            "tenor": ["5Y"] * 100,
            "series": [42] * 100,
        }
    )


@pytest.fixture
def sample_vix_data() -> pd.DataFrame:
    """Create sample VIX data for testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    return pd.DataFrame(
        {
            "date": dates,
            "close": 15 + pd.Series(range(100)).apply(lambda x: (x % 20) * 0.5),
            "open": 15 + pd.Series(range(100)).apply(lambda x: ((x + 1) % 20) * 0.5),
        }
    )


@pytest.fixture
def sample_etf_data() -> pd.DataFrame:
    """Create sample ETF data for testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    return pd.DataFrame(
        {
            "date": dates,
            "close": 80 + pd.Series(range(100)).apply(lambda x: x * 0.1),
            "ticker": ["HYG"] * 100,
            "volume": [1000000] * 100,
        }
    )


def test_load_cdx_parquet(sample_cdx_data: pd.DataFrame) -> None:
    """Test loading CDX data from Parquet file."""
    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "cdx.parquet"
        save_parquet(sample_cdx_data, file_path)

        df = load_cdx_data(file_path)

        assert isinstance(df.index, pd.DatetimeIndex)
        assert "spread" in df.columns
        assert len(df) == 100
        assert df["spread"].min() >= 0


def test_load_cdx_csv(sample_cdx_data: pd.DataFrame) -> None:
    """Test loading CDX data from CSV file."""
    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "cdx.csv"
        sample_cdx_data.to_csv(file_path, index=False)

        df = load_cdx_data(file_path)

        assert isinstance(df.index, pd.DatetimeIndex)
        assert "spread" in df.columns
        assert len(df) == 100


def test_load_cdx_with_index_filter(sample_cdx_data: pd.DataFrame) -> None:
    """Test loading CDX data with index filter."""
    # Add multiple indices
    sample_cdx_data = sample_cdx_data.copy()
    sample_cdx_data.loc[:49, "index"] = "CDX_HY_5Y"

    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "cdx.parquet"
        save_parquet(sample_cdx_data, file_path)

        df = load_cdx_data(file_path, index_name="CDX_IG_5Y")

        assert len(df) == 50
        assert (df["index"] == "CDX_IG_5Y").all()


def test_load_cdx_with_tenor_filter(sample_cdx_data: pd.DataFrame) -> None:
    """Test loading CDX data with tenor filter."""
    # Add multiple tenors
    sample_cdx_data = sample_cdx_data.copy()
    sample_cdx_data.loc[:49, "tenor"] = "10Y"

    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "cdx.parquet"
        save_parquet(sample_cdx_data, file_path)

        df = load_cdx_data(file_path, tenor="5Y")

        assert len(df) == 50
        assert (df["tenor"] == "5Y").all()


def test_load_vix_parquet(sample_vix_data: pd.DataFrame) -> None:
    """Test loading VIX data from Parquet file."""
    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "vix.parquet"
        save_parquet(sample_vix_data, file_path)

        df = load_vix_data(file_path)

        assert isinstance(df.index, pd.DatetimeIndex)
        assert "close" in df.columns
        assert len(df) == 100
        assert df["close"].min() >= 0


def test_load_etf_parquet(sample_etf_data: pd.DataFrame) -> None:
    """Test loading ETF data from Parquet file."""
    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "etf.parquet"
        save_parquet(sample_etf_data, file_path)

        df = load_etf_data(file_path)

        assert isinstance(df.index, pd.DatetimeIndex)
        assert "close" in df.columns
        assert "ticker" in df.columns
        assert len(df) == 100


def test_load_etf_with_ticker_filter(sample_etf_data: pd.DataFrame) -> None:
    """Test loading ETF data with ticker filter."""
    # Add multiple tickers
    sample_etf_data = sample_etf_data.copy()
    sample_etf_data.loc[:49, "ticker"] = "LQD"

    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "etf.parquet"
        save_parquet(sample_etf_data, file_path)

        df = load_etf_data(file_path, ticker="HYG")

        assert len(df) == 50
        assert (df["ticker"] == "HYG").all()


def test_load_all_data(
    sample_cdx_data: pd.DataFrame,
    sample_vix_data: pd.DataFrame,
    sample_etf_data: pd.DataFrame,
) -> None:
    """Test loading all data sources at once."""
    with TemporaryDirectory() as tmpdir:
        cdx_path = Path(tmpdir) / "cdx.parquet"
        vix_path = Path(tmpdir) / "vix.parquet"
        etf_path = Path(tmpdir) / "etf.parquet"

        save_parquet(sample_cdx_data, cdx_path)
        save_parquet(sample_vix_data, vix_path)
        save_parquet(sample_etf_data, etf_path)

        data = load_all_data(cdx_path, vix_path, etf_path)

        assert "cdx" in data
        assert "vix" in data
        assert "etf" in data
        assert len(data["cdx"]) == 100
        assert len(data["vix"]) == 100
        assert len(data["etf"]) == 100


def test_load_unsupported_format() -> None:
    """Test that unsupported file formats raise ValueError."""
    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "data.txt"
        file_path.write_text("invalid data")

        with pytest.raises(ValueError, match="Unsupported file format"):
            load_cdx_data(file_path)
