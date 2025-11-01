"""Unit tests for JSON I/O utilities."""

import pytest
import json
from pathlib import Path
from datetime import datetime
import numpy as np

from aponyx.persistence.json_io import (
    save_json,
    load_json,
    EnhancedJSONEncoder,
)


@pytest.fixture
def sample_metadata():
    """Create sample metadata dictionary."""
    return {
        "timestamp": datetime(2024, 10, 25, 14, 30, 0),
        "params": {
            "window": 5,
            "threshold": 0.5,
            "instruments": ["CDX.IG", "CDX.HY"],
        },
        "version": "0.1.0",
        "file_path": Path("/data/cdx_ig_5y.parquet"),
    }


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary directory for test data."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


class TestEnhancedJSONEncoder:
    """Test cases for EnhancedJSONEncoder."""

    def test_encode_datetime(self):
        """Test datetime serialization."""
        dt = datetime(2024, 10, 25, 14, 30, 0)
        result = json.dumps({"dt": dt}, cls=EnhancedJSONEncoder)
        assert "2024-10-25T14:30:00" in result

    def test_encode_path(self):
        """Test Path serialization."""
        p = Path("/some/path/to/file.parquet")
        result = json.dumps({"path": p}, cls=EnhancedJSONEncoder)
        data = json.loads(result)
        assert data["path"] == str(p)

    def test_encode_numpy_types(self):
        """Test numpy type serialization."""
        data = {
            "int": np.int64(42),
            "float": np.float64(3.14),
            "array": np.array([1, 2, 3]),
        }
        result = json.dumps(data, cls=EnhancedJSONEncoder)
        loaded = json.loads(result)

        assert loaded["int"] == 42
        assert loaded["float"] == pytest.approx(3.14)
        assert loaded["array"] == [1, 2, 3]


class TestSaveJSON:
    """Test cases for save_json function."""

    def test_save_basic(self, sample_metadata, temp_data_dir):
        """Test basic save operation."""
        file_path = temp_data_dir / "metadata.json"
        result = save_json(sample_metadata, file_path)

        assert result.exists()
        assert result == file_path.absolute()

    def test_save_creates_directories(self, sample_metadata, tmp_path):
        """Test that parent directories are created automatically."""
        file_path = tmp_path / "nested" / "deep" / "metadata.json"
        result = save_json(sample_metadata, file_path)

        assert result.exists()
        assert result.parent.exists()

    def test_save_with_formatting(self, temp_data_dir):
        """Test that JSON is formatted for readability."""
        data = {"a": 1, "b": 2, "c": {"nested": 3}}
        file_path = temp_data_dir / "formatted.json"
        save_json(data, file_path)

        content = file_path.read_text()
        assert "\n" in content  # Multi-line
        assert "  " in content  # Indented

    def test_save_sorted_keys(self, temp_data_dir):
        """Test that keys are sorted alphabetically."""
        data = {"z": 1, "a": 2, "m": 3}
        file_path = temp_data_dir / "sorted.json"
        save_json(data, file_path)

        loaded = load_json(file_path)
        keys = list(loaded.keys())
        assert keys == sorted(keys)

    def test_save_without_sorting(self, temp_data_dir):
        """Test saving without key sorting."""
        data = {"z": 1, "a": 2, "m": 3}
        file_path = temp_data_dir / "unsorted.json"
        save_json(data, file_path, sort_keys=False)

        # Verify order preserved (Python 3.7+ dict order)
        content = file_path.read_text()
        z_pos = content.index('"z"')
        a_pos = content.index('"a"')
        m_pos = content.index('"m"')
        assert z_pos < a_pos < m_pos


class TestLoadJSON:
    """Test cases for load_json function."""

    def test_load_basic(self, sample_metadata, temp_data_dir):
        """Test basic load operation."""
        file_path = temp_data_dir / "metadata.json"
        save_json(sample_metadata, file_path)

        loaded = load_json(file_path)

        assert loaded["version"] == "0.1.0"
        assert loaded["params"]["window"] == 5
        assert loaded["timestamp"] == "2024-10-25T14:30:00"  # ISO format

    def test_load_nonexistent_file_raises(self, temp_data_dir):
        """Test that loading nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_json(temp_data_dir / "nonexistent.json")

    def test_load_invalid_json_raises(self, temp_data_dir):
        """Test that invalid JSON raises JSONDecodeError."""
        file_path = temp_data_dir / "invalid.json"
        file_path.write_text("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            load_json(file_path)

    def test_roundtrip_preservation(self, temp_data_dir):
        """Test that save/load roundtrip preserves basic types."""
        data = {
            "string": "hello",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"a": 1, "b": 2},
        }
        file_path = temp_data_dir / "roundtrip.json"

        save_json(data, file_path)
        loaded = load_json(file_path)

        assert loaded == data
