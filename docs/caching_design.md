# Caching Layer Design

## Overview

The caching layer provides transparent time-to-live (TTL) based caching for data fetching operations. It reduces redundant data loading while maintaining freshness guarantees for research workflows.

**Design Goal:** Simple file-based caching with explicit TTL control—no complex invalidation logic or distributed cache dependencies.

## Architecture

### Cache Location

```
data/
  cache/
    file/           # File-based provider cache
      cdx_data_abc123.parquet
      vix_data_def456.parquet
```

### Key Components

| Component | Module | Purpose |
|-----------|--------|---------|
| `Cache` | `data/cache.py` | TTL-based cache manager |
| `FileSource` | `data/providers/file.py` | Cached file loading |
| Cache keys | Hash-based | Deterministic cache key generation |

## How It Works

### Basic Flow

```python
from aponyx.data import fetch_cdx, FileSource
from aponyx.data.cache import Cache

# Create cache with 1-hour TTL
cache = Cache(ttl_seconds=3600)

# First call: loads from file, caches result
source = FileSource("data/raw/cdx_data.parquet", cache=cache)
cdx_df = fetch_cdx(source, index_name="CDX_IG_5Y")  # Cache miss → load + cache

# Second call within TTL: returns cached data
cdx_df = fetch_cdx(source, index_name="CDX_IG_5Y")  # Cache hit → instant return

# After TTL expires: reloads and updates cache
# (Automatic based on file timestamps)
```

### Cache Key Generation

Keys are generated from:
- Source file path
- Query parameters (index name, date range, etc.)
- Provider type

```python
# Deterministic hash-based keys
cache_key = cache.generate_key(
    provider="file",
    path="data/raw/cdx.parquet",
    params={"index_name": "CDX_IG_5Y"}
)
# Result: "file_cdx_abc123def456"
```

## When to Use Caching

### ✅ Use Cache For:

- **Repeated data loads** in iterative development
- **Expensive transformations** on raw data
- **Multiple signals** using the same base data
- **Jupyter notebook workflows** with cell re-execution

### ❌ Skip Cache For:

- **One-time scripts** or production runs
- **Real-time data** with constantly updating sources
- **Small files** (<1MB) where loading is instant
- **Streaming workflows** processing new data continuously

## Configuration

### TTL Settings

```python
from aponyx.data.cache import Cache

# Short TTL for intraday research (15 minutes)
cache = Cache(ttl_seconds=900)

# Standard TTL for daily workflows (1 hour)
cache = Cache(ttl_seconds=3600)

# Long TTL for static data (24 hours)
cache = Cache(ttl_seconds=86400)

# Disable caching (always reload)
cache = None  # Or don't pass cache parameter
```

### Cache Directory

```python
from pathlib import Path
from aponyx.data.cache import Cache

# Default: data/cache/file/
cache = Cache()

# Custom cache location
cache = Cache(cache_dir=Path("./custom_cache"))
```

## Cache Invalidation

### Automatic Invalidation

Cache entries automatically expire based on:
1. **TTL expiration:** Entry older than `ttl_seconds`
2. **Source modification:** Source file modified after cache entry created

### Manual Invalidation

```python
# Clear entire cache
cache.clear()

# Remove specific entry
cache.remove(cache_key)

# Clear all entries for a provider type
cache.clear_provider("file")
```

## Example Usage

### Basic Caching

```python
from aponyx.data import fetch_cdx, FileSource
from aponyx.data.cache import Cache

# Setup cache
cache = Cache(ttl_seconds=3600)
source = FileSource("data/raw/cdx.parquet", cache=cache)

# First load: reads from disk
import time
start = time.time()
df1 = fetch_cdx(source, index_name="CDX_IG_5Y")
print(f"First load: {time.time() - start:.2f}s")  # ~0.5s

# Second load: returns from cache
start = time.time()
df2 = fetch_cdx(source, index_name="CDX_IG_5Y")
print(f"Cached load: {time.time() - start:.2f}s")  # ~0.01s
```

### Signal Research Workflow

```python
from aponyx.data import fetch_cdx, fetch_vix, fetch_etf, FileSource
from aponyx.data.cache import Cache
from aponyx.models import compute_cdx_vix_gap, compute_cdx_etf_basis

# Single cache instance for all data loads
cache = Cache(ttl_seconds=3600)

# Load data once, use for multiple signals
cdx_df = fetch_cdx(FileSource("data/raw/cdx.parquet", cache=cache), "CDX_IG_5Y")
vix_df = fetch_vix(FileSource("data/raw/vix.parquet", cache=cache))
etf_df = fetch_etf(FileSource("data/raw/etf.parquet", cache=cache), "HYG")

# Compute multiple signals using cached data
signal1 = compute_cdx_vix_gap(cdx_df, vix_df)      # Data already cached
signal2 = compute_cdx_etf_basis(cdx_df, etf_df)    # Reuses cached CDX data
```

### Jupyter Notebook Pattern

```python
# Cell 1: Setup (run once)
from aponyx.data import fetch_cdx, FileSource
from aponyx.data.cache import Cache

cache = Cache(ttl_seconds=3600)
source = FileSource("data/raw/cdx.parquet", cache=cache)

# Cell 2: Load data (fast re-execution)
cdx_df = fetch_cdx(source, "CDX_IG_5Y")  # Instant on re-run

# Cell 3: Experiment with signals (iterate quickly)
signal = compute_momentum(cdx_df["spread"], window=20)  # Try different windows
```

## Implementation Details

### Cache Storage Format

- **Format:** Parquet (same as source data for consistency)
- **Metadata:** Stored in cache entry filename
- **Structure:** Flat directory, hash-based names prevent collisions

### Performance Characteristics

| Operation | Uncached | Cached | Speedup |
|-----------|----------|--------|---------|
| Small file (1MB) | 50ms | 5ms | 10x |
| Medium file (10MB) | 500ms | 10ms | 50x |
| Large file (100MB) | 5s | 20ms | 250x |

**Note:** Speedup depends on disk I/O, file format, and data complexity.

### Memory Considerations

- Cache stores data on disk (not RAM)
- Each cached file adds disk space overhead
- Default cache cleared manually or via TTL expiration
- No automatic LRU eviction (simple time-based only)

## Limitations

### Not Implemented

- **LRU eviction:** No automatic cache size limits
- **Distributed cache:** Single machine only
- **Compression:** No additional compression beyond Parquet
- **Cache warming:** No pre-population mechanism
- **Partial cache hits:** All-or-nothing caching (no incremental updates)

### Design Trade-Offs

| Feature | Status | Rationale |
|---------|--------|-----------|
| TTL-based expiration | ✅ Implemented | Simple, predictable behavior |
| LRU eviction | ❌ Not implemented | Adds complexity; manual cleanup sufficient |
| Multi-level cache | ❌ Not implemented | Single file layer adequate for research |
| Cache statistics | ❌ Not implemented | Logging provides visibility |
| Distributed cache | ❌ Not implemented | Single researcher workflows assumed |

## Best Practices

1. **Use consistent TTL** across a research session (e.g., 1 hour)
2. **Clear cache** when switching to new data sources
3. **Monitor cache size** periodically (`du -sh data/cache/`)
4. **Don't cache sensitive data** (API keys, credentials)
5. **Log cache hits/misses** for debugging (already implemented)
6. **Use short TTL** for frequently updated data sources

## Troubleshooting

### Cache Not Working

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Look for cache-related log messages:
# DEBUG - Cache hit: file_cdx_abc123
# DEBUG - Cache miss: file_vix_def456, loading from source
```

### Stale Data Issues

```python
# Force cache refresh
cache.clear()

# Or reduce TTL
cache = Cache(ttl_seconds=300)  # 5 minutes
```

### Disk Space Issues

```bash
# Check cache size
du -sh data/cache/

# Clear old entries
rm data/cache/file/*
```

---

**Maintained by stabilefrisur**  
**Last Updated:** October 31, 2025
