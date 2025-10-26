# Persistence Layer

**Status:** ✅ Complete and tested (49/49 tests passing)

## Overview

The persistence layer provides clean abstractions for data storage and retrieval in the Systematic Macro Credit framework. It handles:

- **Parquet I/O**: Efficient time series storage with compression and filtering
- **JSON I/O**: Metadata, parameters, and run logs with enhanced type support
- **Data Registry**: Centralized catalog for tracking available datasets

## Modules

### `parquet_io.py`
Time series data storage using Apache Parquet format.

**Key Functions:**
- `save_parquet()`: Save DataFrames with automatic directory creation
- `load_parquet()`: Load with column/date filtering for efficient queries
- `list_parquet_files()`: Discover available Parquet files

**Features:**
- Multiple compression algorithms (snappy, gzip, zstd)
- Optional date range filtering on load
- Preserves DatetimeIndex for time series data

### `json_io.py`
Metadata and configuration persistence with enhanced JSON encoding.

**Key Functions:**
- `save_json()`: Serialize dictionaries with datetime/Path/numpy support
- `load_json()`: Deserialize JSON files

**Features:**
- Automatic type conversion (datetime → ISO format, Path → string, numpy → native)
- Formatted output for readability
- UTF-8 encoding with proper error handling

### `registry.py`
Centralized data catalog for managing datasets.

**Key Class: `DataRegistry`**

**Methods:**
- `register_dataset()`: Add dataset with metadata and auto-extract stats
- `get_dataset_info()`: Retrieve dataset metadata
- `list_datasets()`: Query datasets by instrument/tenor
- `update_dataset_stats()`: Refresh date ranges and row counts
- `remove_dataset()`: Remove from catalog (optionally delete file)

**Registry Entry Structure:**
```json
{
  "cdx_ig_5y": {
    "instrument": "CDX.NA.IG",
    "tenor": "5Y",
    "file_path": "data/raw/cdx_ig_5y.parquet",
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-10-25T00:00:00",
    "row_count": 215,
    "registered_at": "2024-10-25T14:30:00",
    "metadata": {
      "source": "Bloomberg",
      "frequency": "daily"
    }
  }
}
```

## Usage Examples

### Basic Parquet I/O
```python
from macrocredit.persistence import save_parquet, load_parquet
import pandas as pd

# Save time series
df = pd.DataFrame({'spread': [100, 105, 98]}, 
                  index=pd.date_range('2024-01-01', periods=3))
save_parquet(df, 'data/cdx_ig_5y.parquet')

# Load with filters
recent = load_parquet('data/cdx_ig_5y.parquet', 
                     start_date=pd.Timestamp('2024-10-01'),
                     columns=['spread'])
```

### Registry Management
```python
from macrocredit.persistence import DataRegistry

registry = DataRegistry('data/registry.json', 'data/')

# Register dataset
registry.register_dataset(
    name='cdx_ig_5y',
    file_path='data/cdx_ig_5y.parquet',
    instrument='CDX.NA.IG',
    tenor='5Y'
)

# Query registry
cdx_datasets = registry.list_datasets(instrument='CDX.NA.IG')
info = registry.get_dataset_info('cdx_ig_5y')
```

### Metadata Logging
```python
from macrocredit.persistence import save_json, load_json
from datetime import datetime

metadata = {
    'timestamp': datetime.now(),
    'params': {'window': 5, 'threshold': 0.5},
    'version': '0.1.0'
}
save_json(metadata, 'logs/run_20241025.json')
```

## Testing

Run the full test suite:
```bash
uv run pytest tests/persistence/ -v
```

Run with coverage:
```bash
uv run pytest tests/persistence/ --cov=macrocredit.persistence --cov-report=term-missing
```

## Demo

See `examples/persistence_demo.py` for a complete demonstration:
```bash
uv run python examples/persistence_demo.py
```

## Dependencies

- **pandas** ≥2.2.0: DataFrame operations
- **numpy** ≥2.0.0: Array handling in JSON encoder
- **pyarrow** ≥17.0.0: Parquet engine

## Design Principles

1. **No Database Dependencies**: All data stored in files (Parquet/JSON)
2. **Type Safety**: Comprehensive type hints throughout
3. **Deterministic**: Reproducible I/O operations
4. **Modular**: Clean separation between Parquet, JSON, and registry
5. **Tested**: 100% test coverage with edge cases

---

**Maintained by:** stabilefrisur  
**Version:** 0.1.0  
**Last Updated:** October 25, 2025
