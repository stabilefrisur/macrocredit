"""Unit tests for Parquet I/O utilities."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

from macrocredit.persistence.parquet_io import (
    save_parquet,
    load_parquet,
    list_parquet_files,
)


@pytest.fixture
def sample_timeseries():
    """Create sample time series data for testing."""
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    return pd.DataFrame(
        {
            "spread": np.random.uniform(90, 110, 10),
            "volume": np.random.randint(1000, 5000, 10),
        },
        index=dates,
    )


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary directory for test data."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


class TestSaveParquet:
    """Test cases for save_parquet function."""

    def test_save_basic(self, sample_timeseries, temp_data_dir):
        """Test basic save operation."""
        file_path = temp_data_dir / "test.parquet"
        result = save_parquet(sample_timeseries, file_path)

        assert result.exists()
        assert result == file_path.absolute()

    def test_save_creates_directories(self, sample_timeseries, tmp_path):
        """Test that parent directories are created automatically."""
        file_path = tmp_path / "nested" / "deep" / "test.parquet"
        result = save_parquet(sample_timeseries, file_path)

        assert result.exists()
        assert result.parent.exists()

    def test_save_with_compression(self, sample_timeseries, temp_data_dir):
        """Test different compression algorithms."""
        for compression in ["snappy", "gzip", "zstd"]:
            file_path = temp_data_dir / f"test_{compression}.parquet"
            result = save_parquet(sample_timeseries, file_path, compression=compression)
            assert result.exists()

    def test_save_without_index(self, sample_timeseries, temp_data_dir):
        """Test saving without index."""
        file_path = temp_data_dir / "no_index.parquet"
        save_parquet(sample_timeseries, file_path, index=False)

        df = pd.read_parquet(file_path)
        assert isinstance(df.index, pd.RangeIndex)

    def test_save_empty_dataframe_raises(self, temp_data_dir):
        """Test that saving empty DataFrame raises ValueError."""
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="Cannot save empty DataFrame"):
            save_parquet(empty_df, temp_data_dir / "empty.parquet")


class TestLoadParquet:
    """Test cases for load_parquet function."""

    def test_load_basic(self, sample_timeseries, temp_data_dir):
        """Test basic load operation."""
        file_path = temp_data_dir / "test.parquet"
        save_parquet(sample_timeseries, file_path)

        loaded = load_parquet(file_path)
        pd.testing.assert_frame_equal(loaded, sample_timeseries, check_freq=False)

    def test_load_with_column_filter(self, sample_timeseries, temp_data_dir):
        """Test loading specific columns."""
        file_path = temp_data_dir / "test.parquet"
        save_parquet(sample_timeseries, file_path)

        loaded = load_parquet(file_path, columns=["spread"])
        assert loaded.columns.tolist() == ["spread"]
        assert len(loaded) == len(sample_timeseries)

    def test_load_with_date_filter(self, sample_timeseries, temp_data_dir):
        """Test loading with date range filtering."""
        file_path = temp_data_dir / "test.parquet"
        save_parquet(sample_timeseries, file_path)

        start = pd.Timestamp("2024-01-03")
        end = pd.Timestamp("2024-01-07")
        loaded = load_parquet(file_path, start_date=start, end_date=end)

        assert loaded.index.min() >= start
        assert loaded.index.max() <= end
        assert len(loaded) == 5

    def test_load_nonexistent_file_raises(self, temp_data_dir):
        """Test that loading nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_parquet(temp_data_dir / "nonexistent.parquet")

    def test_load_date_filter_without_datetime_index_raises(self, temp_data_dir):
        """Test that date filtering on non-datetime index raises ValueError."""
        df = pd.DataFrame({"value": [1, 2, 3]})
        file_path = temp_data_dir / "no_datetime.parquet"
        save_parquet(df, file_path)

        with pytest.raises(ValueError, match="Date filtering requires DatetimeIndex"):
            load_parquet(file_path, start_date=pd.Timestamp("2024-01-01"))


class TestListParquetFiles:
    """Test cases for list_parquet_files function."""

    def test_list_all_files(self, sample_timeseries, temp_data_dir):
        """Test listing all Parquet files in directory."""
        for i in range(3):
            save_parquet(sample_timeseries, temp_data_dir / f"file_{i}.parquet")

        files = list_parquet_files(temp_data_dir)
        assert len(files) == 3
        assert all(f.suffix == ".parquet" for f in files)

    def test_list_with_pattern(self, sample_timeseries, temp_data_dir):
        """Test listing files with glob pattern."""
        save_parquet(sample_timeseries, temp_data_dir / "cdx_ig.parquet")
        save_parquet(sample_timeseries, temp_data_dir / "cdx_hy.parquet")
        save_parquet(sample_timeseries, temp_data_dir / "vix.parquet")

        cdx_files = list_parquet_files(temp_data_dir, pattern="cdx_*.parquet")
        assert len(cdx_files) == 2
        assert all("cdx" in f.name for f in cdx_files)

    def test_list_empty_directory(self, temp_data_dir):
        """Test listing files in empty directory."""
        files = list_parquet_files(temp_data_dir)
        assert files == []

    def test_list_nonexistent_directory(self, tmp_path):
        """Test listing files in nonexistent directory."""
        files = list_parquet_files(tmp_path / "nonexistent")
        assert files == []

    def test_list_sorted(self, sample_timeseries, temp_data_dir):
        """Test that results are sorted."""
        for name in ["c.parquet", "a.parquet", "b.parquet"]:
            save_parquet(sample_timeseries, temp_data_dir / name)

        files = list_parquet_files(temp_data_dir)
        names = [f.name for f in files]
        assert names == sorted(names)
