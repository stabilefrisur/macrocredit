# Layer Implementation Review Prompt (Agent Mode)

## Context

You are reviewing the initial implementation of a layer in the **Systematic Macro Credit** project.  
This is a **pilot implementation** for investment research — prioritize simplicity, modularity, and extensibility over comprehensive feature coverage.

**Core Principles:**
- **Research focus:** Minimize infrastructure complexity
- **Modularity:** Each layer should be independent with clear boundaries
- **Extensibility:** Design interfaces to integrate established packages later
- **Simplicity:** Start minimal, extend incrementally based on research needs

---

## Review Checklist

### 1. Interface Design & Abstraction

**Objective:** Ensure clean, minimal interfaces that enable future extensibility

- [ ] **Clear API surface:** Are public functions/classes well-defined and minimal?
- [ ] **Separation of concerns:** Does this layer have exactly one responsibility?
- [ ] **Protocol/ABC usage:** Are interfaces defined using `Protocol` or `ABC` where appropriate?
- [ ] **Type signatures:** Are all public functions fully type-annotated with modern Python 3.13 syntax?
- [ ] **Extension points:** Can this layer easily integrate external packages (e.g., specialized data loaders, alternative backtest engines)?
- [ ] **Dependency direction:** Does this layer depend only on lower-level layers (no circular dependencies)?

**Red flags:**
- ❌ Tightly coupled to specific implementations (hardcoded classes/functions)
- ❌ Mixing multiple responsibilities (e.g., data loading + transformation + persistence in one module)
- ❌ Complex inheritance hierarchies
- ❌ God objects or utility classes that do too much

**Green patterns:**
- ✅ Simple function-based APIs for transformations
- ✅ Dataclasses for configuration and results
- ✅ Protocol definitions for swappable components
- ✅ Pure functions with clear inputs/outputs

---

### 2. Code Organization & Structure

**Objective:** Maintain functional, modular architecture aligned with project standards

- [ ] **Function-first design:** Are classes only used when state management or lifecycle is needed?
- [ ] **Dataclass usage:** Are data containers implemented as `@dataclass` (frozen for immutable config)?
- [ ] **Module cohesion:** Does each module have a single, clear purpose?
- [ ] **Import structure:** Are imports relative within the package?
- [ ] **No global state:** Are all dependencies explicitly passed as parameters?
- [ ] **Minimal file size:** Is each module under 300 lines (consider splitting if larger)?

**Example structure:**
```python
# Good: Function-based transformation pipeline
def clean_spread_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate spread time series."""
    ...

def normalize_spreads(df: pd.DataFrame, method: str = "zscore") -> pd.DataFrame:
    """Normalize spread levels for cross-sectional comparison."""
    ...

# Good: Dataclass for configuration
@dataclass(frozen=True)
class BacktestConfig:
    """Backtest parameters."""
    initial_capital: float
    position_limit: float
    rebalance_freq: str

# Bad: Class wrapping a single function
class SpreadCalculator:  # ❌ Unnecessary class
    def calculate(self, df: pd.DataFrame) -> pd.Series:
        ...
```

---

### 3. Layer Boundaries & Dependencies

**Objective:** Ensure strict layer separation and minimal coupling

**Expected layer hierarchy:**
```
config/ (lowest)
  ↓
data/ → persistence/
  ↓
models/
  ↓
backtest/
  ↓
visualization/ (highest)
```

**Check:**
- [ ] **No upward dependencies:** Does this layer import only from same-level or lower layers?
- [ ] **Clear inputs/outputs:** Are layer boundaries defined by data structures (DataFrames, dataclasses)?
- [ ] **No leaky abstractions:** Does this layer hide its implementation details?
- [ ] **Minimal shared state:** Are interactions stateless or explicitly managed?

**Example violations:**
```python
# ❌ Data layer importing from models layer
from macrocredit.models.signals import compute_momentum

# ❌ Models layer directly reading files
df = pd.read_parquet("data/raw/spreads.parquet")

# ✅ Models layer accepting clean data
def compute_signals(spreads: pd.DataFrame, vix: pd.DataFrame) -> pd.DataFrame:
    ...
```

---

### 4. Type Safety & Documentation

**Objective:** Ensure code is self-documenting and type-safe

- [ ] **Modern type syntax:** Uses `str | None`, `list[str]`, `dict[str, Any]` (not `Optional`, `List`, `Dict`)
- [ ] **Full type coverage:** All public functions have complete type hints
- [ ] **NumPy-style docstrings:** All public functions document parameters, returns, and examples
- [ ] **Raises section:** Functions document expected exceptions
- [ ] **Type guards:** Uses `isinstance()` or `TypeGuard` for runtime validation where needed

**Documentation template:**
```python
def compute_signal(
    data: pd.DataFrame,
    window: int = 20,
    threshold: float = 2.0,
) -> pd.Series:
    """
    Compute z-score normalized signal from time series data.

    Parameters
    ----------
    data : pd.DataFrame
        Input data with datetime index and 'value' column.
    window : int, default 20
        Rolling window for mean/std calculation.
    threshold : float, default 2.0
        Signal threshold for position sizing.

    Returns
    -------
    pd.Series
        Normalized signal values with same index as input.

    Raises
    ------
    ValueError
        If window is negative or data is empty.

    Examples
    --------
    >>> df = pd.DataFrame({'value': [100, 102, 98, 101]})
    >>> signal = compute_signal(df, window=2)
    >>> signal.iloc[-1]  # Latest signal value
    0.707
    
    Notes
    -----
    Uses Welford's online algorithm for numerical stability.
    """
```

---

### 5. Logging & Observability

**Objective:** Enable debugging and monitoring without cluttering code

- [ ] **Module-level logger:** Uses `logger = logging.getLogger(__name__)`
- [ ] **No basicConfig:** Library code never calls `logging.basicConfig()`
- [ ] **%-formatting:** Log messages use `logger.info("Loaded %d rows", n)` not f-strings
- [ ] **Appropriate levels:**
  - `INFO`: User-facing operations (file loaded, backtest started)
  - `DEBUG`: Implementation details (parameter values, intermediate calculations)
  - `WARNING`: Recoverable issues (missing data, fallback to defaults)
  - `ERROR`: Failures requiring attention
- [ ] **Structured context:** Logs include relevant parameters and counts

**Example:**
```python
import logging

logger = logging.getLogger(__name__)

def load_market_data(start_date: str, end_date: str) -> pd.DataFrame:
    """Load market data for date range."""
    logger.info("Loading market data: start=%s, end=%s", start_date, end_date)
    
    df = _read_parquet_files(start_date, end_date)
    logger.debug("Loaded %d rows, %d columns", len(df), len(df.columns))
    
    if df.isna().sum().sum() > 0:
        logger.warning("Found %d missing values, applying forward fill", df.isna().sum().sum())
        df = df.fillna(method='ffill')
    
    return df
```

---

### 6. Testability & Reproducibility

**Objective:** Ensure layer can be tested in isolation and produces deterministic results

- [ ] **Pure functions:** Most logic is in pure functions (same input → same output)
- [ ] **Dependency injection:** External dependencies passed as parameters, not imported globally
- [ ] **Deterministic:** All random operations use fixed seeds
- [ ] **Test fixtures:** Layer includes sample data generators for testing
- [ ] **Unit test coverage:** Core functions have corresponding tests in `tests/` directory
- [ ] **Mock-friendly:** External I/O (files, network) is isolated and mockable

**Example:**
```python
# ✅ Testable: pure function, dependency injected
def compute_returns(
    prices: pd.Series,
    method: str = "log",
) -> pd.Series:
    """Compute returns from price series."""
    if method == "log":
        return np.log(prices / prices.shift(1))
    return prices.pct_change()

# ❌ Hard to test: global import, side effects
def compute_returns_bad():
    df = pd.read_csv("../data/prices.csv")  # Global file dependency
    return np.log(df['close'] / df['close'].shift(1))

# ✅ Test example
def test_log_returns():
    """Test log return calculation."""
    prices = pd.Series([100, 105, 102])
    returns = compute_returns(prices, method="log")
    
    expected = pd.Series([np.nan, np.log(1.05), np.log(102/105)])
    pd.testing.assert_series_equal(returns, expected)
```

---

### 7. Pilot Simplicity Check

**Objective:** Ensure we're building the minimum viable implementation

**Ask:**
- [ ] **Is this the simplest thing that works?** Can we remove features without breaking core use cases?
- [ ] **Are we solving problems we don't have yet?** Are there speculative features we can defer?
- [ ] **Can we use established packages?** Are we reinventing `pandas`, `numpy`, `scipy` functionality?
- [ ] **Is error handling proportional?** Do we have complex error recovery for simple operations?

**Simplification opportunities:**
- Replace custom caching with simple Parquet files
- Replace complex configuration with dataclasses and defaults
- Replace custom validation with `pydantic` or simple assertions
- Defer optimization until profiling shows bottlenecks

---

## Review Output Format

Provide a structured review with the following sections:

### ✅ Strengths
- List 3-5 things this implementation does well
- Highlight good design patterns or code quality

### ⚠️ Issues Found

For each issue:
1. **Category:** (Interface, Structure, Dependencies, Types, Logging, Testing, Simplicity)
2. **Severity:** (Critical, Moderate, Minor)
3. **Description:** What's wrong and why it matters
4. **Recommendation:** Specific fix with code example if applicable

### 🔧 Refactoring Recommendations

Provide 2-3 concrete refactoring suggestions to improve:
- Modularity and extensibility
- Simplicity and maintainability
- Testability and reproducibility

Each recommendation should include:
- Current pattern (code snippet)
- Proposed pattern (code snippet)
- Rationale (why the change improves the design)

### 📋 Action Items

Prioritized list of changes:
1. **Critical:** Must fix before merging
2. **Important:** Should fix in this iteration
3. **Nice-to-have:** Can defer to future iterations

---

## Example Review

### Layer: `data/loader.py`

#### ✅ Strengths
- Clean separation between raw data reading and validation
- Uses Parquet for efficient storage and type preservation
- Good logging coverage for debugging data issues
- Type hints are complete and use modern Python 3.13 syntax

#### ⚠️ Issues Found

**1. Tight Coupling to File Format**
- **Category:** Interface
- **Severity:** Moderate
- **Description:** `load_market_data()` directly calls `pd.read_parquet()`, making it hard to extend to other sources (CSV, databases, APIs)
- **Recommendation:**
```python
# Current (❌)
def load_market_data(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)

# Proposed (✅)
from typing import Protocol

class DataSource(Protocol):
    """Protocol for data loading strategies."""
    def read(self, path: str) -> pd.DataFrame: ...

def load_market_data(source: DataSource, path: str) -> pd.DataFrame:
    """Load data using pluggable source strategy."""
    logger.info("Loading data from %s", path)
    return source.read(path)

# Usage
parquet_source = ParquetDataSource()
df = load_market_data(parquet_source, "data/spreads.parquet")
```

**2. Global Date Parsing Configuration**
- **Category:** Structure
- **Severity:** Minor
- **Description:** Date format is hardcoded as module constant, should be configurable
- **Recommendation:**
```python
# Current (❌)
DATE_FORMAT = "%Y-%m-%d"  # Global constant

# Proposed (✅)
@dataclass(frozen=True)
class LoaderConfig:
    """Data loader configuration."""
    date_format: str = "%Y-%m-%d"
    parse_dates: list[str] = field(default_factory=lambda: ["date"])

def load_market_data(
    path: str,
    config: LoaderConfig = LoaderConfig(),
) -> pd.DataFrame:
    ...
```

#### 🔧 Refactoring Recommendations

**1. Extract validation into separate module**

Currently validation is mixed with loading logic. Separate concerns:

```python
# data/loader.py
def load_raw_data(path: str) -> pd.DataFrame:
    """Load raw data without validation."""
    return pd.read_parquet(path)

# data/validation.py
def validate_market_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate market data schema and contents."""
    required_cols = ["date", "spread", "volume"]
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Missing columns: {set(required_cols) - set(df.columns)}")
    return df

# Usage
df = validate_market_data(load_raw_data("data.parquet"))
```

**Rationale:** Enables reusing validation across different data sources and testing validation logic independently.

#### 📋 Action Items

**Critical:**
1. Add type hints to `_parse_dates()` helper function
2. Fix circular import between `loader.py` and `transform.py`

**Important:**
3. Refactor to use Protocol for extensible data sources
4. Extract validation to separate module

**Nice-to-have:**
5. Add configuration dataclass for loader parameters
6. Add docstring examples to all public functions

---

## Usage Instructions

**When to use this prompt:**
- After completing initial implementation of a layer
- Before submitting PR for layer code
- During code review phase
- When refactoring existing layer

**How to use:**
1. Copy this prompt into agent chat
2. Specify: "Review the `[layer_name]` layer implementation"
3. Provide context: point to relevant files or paste code
4. Agent will apply checklist and generate structured review
5. Address critical/important items before merging

---

> **Maintained by:** stabilefrisur  
> **Version:** 1.0  
> **Last Updated:** October 27, 2025  
> **Target:** VS Code Agent Mode (Claude Sonnet 4.5 / GPT-5)
