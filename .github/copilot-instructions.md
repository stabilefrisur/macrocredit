# Copilot Instructions — Systematic Macro Credit Project (VS Code Agent Mode)

## Purpose

These instructions optimize **Copilot Chat and inline completions** in **VS Code Agent mode** (Claude Sonnet 4.5 / GPT‑5) for the *Systematic Macro Credit* project.  
The goal is to ensure the AI assistant generates **clean, modular, and reproducible** Python code aligned with project architecture and investment research standards.

---

## Project Overview

You are working within a **systematic fixed‑income research environment**.  
The framework supports:
- Development and testing of **pilot investment strategies** (e.g., CDX overlay).
- Modular architecture for **data**, **model**, **backtest**, **visualization**, and **persistence** layers.
- Reproducible, documented, and version‑controlled research.

### Repository Layout

```
src/macrocredit/
  data/               # Loaders, cleaning, transformation
  models/             # Signal & strategy logic
  backtest/           # Backtesting engine and risk tracking
  visualization/      # Plotly & Streamlit dashboards
  persistence/        # Parquet & JSON I/O utilities
  config/             # Paths, constants, environment
  __init__.py         # Package initialization
  main.py             # CLI entry point / notebook runner

tests/                # Unit tests for reproducibility
  data/
  models/
  backtest/
  visualization/
  persistence/

.docs/                # Documentation and strategy specs
  cdx_overlay_strategy.md # Investment strategy context
.github/              # GitHub workflows and agent instructions
pyproject.toml        # Project dependencies and build system
README.md             # Project overview and setup instructions
```

---

## ⚙️ Environment Standards

- **Python:** 3.13  
- **Type Hints:** Use modern Python 3.13 syntax (`str | None` instead of `Optional[str]`, `int | float` instead of `Union[int, float]`)
- **Environment:** managed with [`uv`](https://docs.astral.sh/uv/)  
- **Linting / Formatting:** `ruff`, `black`, `mypy`
- **Testing:** `pytest`
- **Docs:** `mkdocs` or `sphinx`
- **Visualization:** `plotly`, `streamlit`

All dependencies live in `pyproject.toml`.  
Use relative imports and avoid global state.

---

## Environment Standards

- **Python:** 3.13

---

## Agent Behavior Guidelines

### General
1. **Always prioritize modular, PEP 8‑compliant, type‑annotated code.**
2. **Never mix strategy logic with infrastructure code.**
3. **Always document functions and classes using NumPy‑style docstrings.**
4. **Propose structured changes — not isolated code fragments.**
5. **Assume collaboration**: other developers must read and extend your code easily.

### Style
- Follow **PEP 8** and **type hints** strictly.
- Use **Python 3.13 type syntax**: `str | None` not `Optional[str]`, `int | float` not `Union[int, float]`.
- Use **built-in generics**: `list[str]` not `List[str]`, `dict[str, Any]` not `Dict[str, Any]`.
- Use **black** and **ruff** formatting conventions.
- Add **docstrings** and comments explaining rationale and data flow.
- **No decorative emojis** in code or docstrings. Only ✅ and ❌ for clarity in examples.

### Code Organization Philosophy
- **Prefer functions over classes.** Default to pure functions for transformations, calculations, and data processing.
- Only use classes when you need: (1) state management, (2) multiple related methods on shared state, (3) lifecycle management, or (4) plugin/interface patterns.
- **Use `@dataclass` for data containers** (parameters, results, metrics) — not regular classes.
- Use `@dataclass(frozen=True)` for immutable configuration/parameters.
- Avoid "calculator" or "helper" classes that just wrap a single function.

### Logging
- Use **module-level loggers**: `logger = logging.getLogger(__name__)`
- **Never** call `logging.basicConfig()` in library code.
- Use **%-formatting**: `logger.info("Loaded %d rows", len(df))` not f-strings.
- **INFO**: User-facing operations. **DEBUG**: Implementation details. **WARNING**: Recoverable errors.

### Documentation Example
```python
def compute_spread_momentum(spread: pd.Series, window: int = 5) -> pd.Series:
    """
    Compute short‑term momentum in CDX spreads using z‑score normalization.

    Parameters
    ----------
    spread : pd.Series
        Daily CDX spread levels.
    window : int, default 5
        Rolling lookback period in days.

    Returns
    -------
    pd.Series
        Normalized momentum signal.
    """
```

### Documentation Structure

**Single Source of Truth Principle**: Each piece of information has exactly one authoritative location.

| Doc Type | Location | Purpose |
|----------|----------|---------|
| **API Reference** | Module docstrings | Function/class contracts, type info, parameters |
| **Quickstart** | `README.md` | Installation, quick examples, navigation |
| **Design Docs** | `docs/*.md` | Architecture, standards, strategy rationale |
| **Examples** | `examples/*.py` headers | Runnable demonstrations with explanatory headers |

**What to document where:**
- **Docstrings**: API contracts (parameters, returns, raises), edge cases, usage notes
- **Examples**: Workflow demonstrations with clear headers explaining purpose and expected output
- **Design docs**: Architectural decisions, cross-cutting concerns (*why*, not *how*)
- **README**: Installation, project structure, quickstart commands

**Never:**
- Create README files in implementation directories (`src/macrocredit/*/README.md`)
- Duplicate API documentation outside of docstrings
- Write tutorial-style docs that duplicate runnable examples
- Document usage patterns in design docs (use examples instead)

---

## Agent Context Hints for Claude Sonnet / GPT-5

| Context | Preferred Behavior |
|----------|--------------------|
| Editing `/data/` | Focus on reproducible data loading, cleaning, and transformation. Avoid strategy logic. |
| Editing `/models/` | Focus on signal functions and strategy modules. Use clean abstractions. **Signal convention: positive values = long credit risk (buy CDX).** |
| Editing `/backtest/` | Implement transparent, deterministic backtest logic. Include metadata logging. |
| Editing `/visualization/` | Generate reusable Plotly/Streamlit components. Separate plotting from computation. |
| Editing `/persistence/` | Handle Parquet/JSON I/O and registry management. No database dependencies. |
| Editing `/tests/` | Write unit tests for determinism, type safety, and reproducibility. |

When generating code, the assistant should **infer module context from file path** and **adhere to functional boundaries** automatically.

### Signal Sign Convention (Models Layer)

**All model signals must follow a consistent sign convention:**

- **Positive signal values** → Long credit risk → Buy CDX (sell protection)
- **Negative signal values** → Short credit risk → Sell CDX (buy protection)

This convention ensures that:
1. Signals can be aggregated without confusion about directionality
2. Positive composite scores clearly indicate bullish credit positioning
3. Risk limits and thresholds apply consistently across all signals

**Signal naming convention:**

Use consistent signal names throughout the models layer:
- **Signal names:** `cdx_etf_basis`, `cdx_vix_gap`, `spread_momentum`
- **Function names:** `compute_cdx_etf_basis`, `compute_cdx_vix_gap`, `compute_spread_momentum`
- **Function parameters:** `cdx_etf_basis`, `cdx_vix_gap`, `spread_momentum`
- **Config attributes:** `cdx_etf_basis_weight`, `cdx_vix_gap_weight`, `spread_momentum_weight`
- **DataFrame columns:** `cdx_etf_basis`, `cdx_vix_gap`, `spread_momentum`

**Implementation guidelines:**
- When creating new signals, verify the sign matches this convention
- Use consistent signal names across functions, parameters, and configuration
- Document signal interpretation clearly in docstrings
- Use negation (`-`) when raw calculations naturally produce inverse signs
- Test signal directionality with simple synthetic data

**Example:**
```python
# Spread momentum: tightening = bullish = positive signal
spread_change = current_spread - past_spread  # Negative when tightening
signal = -spread_change / volatility  # Negated to match convention
```

---

## Completion Optimization Rules

- Always suggest **imports relative to project structure**, not absolute paths.  
- Provide **runnable examples** with synthetic or minimal data.  
- Use **clear function and variable naming** (snake_case, descriptive).  
- When generating new modules, **include header comments** describing purpose and dependencies.  
- Include **type hints** and **unit test templates** by default.

### Example Ideal Output (inline completion)

```python
# models/cdx_overlay_model.py

import logging
from ..data.loader import load_market_data
from ..persistence.io import save_json
import pandas as pd

logger = logging.getLogger(__name__)

def compute_vix_cdx_gap(
    vix_df: pd.DataFrame,
    cdx_df: pd.DataFrame,
    lookback: int = 20
) -> pd.Series:
    """
    Compute the relative stress signal between equity vol (VIX) and CDX spreads.

    The signal identifies divergence between cross‑asset risk sentiment.
    Positive values indicate VIX outpacing credit widening.

    Parameters
    ----------
    vix_df : pd.DataFrame
        VIX index levels with 'VIX' column.
    cdx_df : pd.DataFrame
        CDX index spreads with 'spread' column.
    lookback : int, default 20
        Rolling window for mean and std calculation.

    Returns
    -------
    pd.Series
        Normalized VIX‑CDX gap signal.
        
    Notes
    -----
    Uses z-score normalization to make signals comparable across regimes.
    """
    logger.info(
        "Computing VIX-CDX gap: vix_rows=%d, cdx_rows=%d, lookback=%d",
        len(vix_df),
        len(cdx_df),
        lookback,
    )
    
    vix_deviation = vix_df['VIX'] - vix_df['VIX'].rolling(lookback).mean()
    cdx_deviation = cdx_df['spread'] - cdx_df['spread'].rolling(lookback).mean()
    gap = vix_deviation - cdx_deviation
    signal = gap / gap.rolling(lookback).std()
    
    logger.debug("Generated %d signal values", signal.notna().sum())
    return signal
```

---

## The Agent Should Never

- Use external databases or APIs (use Parquet/JSON only).  
- Use old typing syntax (`Optional`, `Union`, `List`, `Dict`).
- Call `logging.basicConfig()` in library code or use f-strings in log messages.
- Hardcode file paths or credentials.  
- Generate non‑deterministic results without a fixed random seed.  
- Mix backtest logic with data ingestion.  
- Produce undocumented or untyped code.  
- Add notebook cells or magic commands inside modules.
- Add decorative emojis to code, comments, or docstrings.
- Create classes when a simple function would suffice.
- Use regular classes for data containers instead of `@dataclass`.
- Create README files in implementation directories (`src/macrocredit/*/README.md`).
- Duplicate API documentation outside of module docstrings.
- Write tutorial-style docs that duplicate runnable examples.
- Implement authentication, authorization, or credential management (handled externally).
- Create connection setup code for data providers (connections established outside project).

---

## Testing & Logging Expectations

- All stochastic components must be **seeded deterministically**.  
- Every backtest or signal computation must log metadata (timestamp, parameters, version).
- Include lightweight tests for data I/O, signal correctness, and regression.
- Use module-level loggers: `logger = logging.getLogger(__name__)`
- Log at **INFO** for user operations, **DEBUG** for details, **WARNING** for errors.

Example:
```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def run_backtest(params: dict) -> dict:
    """Run backtest with logging."""
    logger.info("Starting backtest: params=%s", params)
    
    # ... backtest logic ...
    
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "params": params,
        "version": __version__,
    }
    save_json(metadata, "run_metadata.json")
    
    logger.info("Backtest complete: sharpe=%.2f, trades=%d", sharpe, n_trades)
    return results
```

---

## Git Commit Standards

Follow **Conventional Commits** format for consistency and automated changelog generation:

### Format
```
<type>: <description>

[optional body]
```

### Rules
- **Type**: Lowercase, from the list below
- **Description**: Capitalize first letter, no period at end, imperative mood ("Add" not "Added")
- **Length**: Keep first line under 72 characters
- **Body**: Optional, explain *why* not *what*, wrap at 72 characters

### Types
- `feat`: New feature or capability
- `fix`: Bug fix or correction
- `docs`: Documentation changes only
- `refactor`: Code restructuring without behavior change
- `test`: Adding or updating tests
- `perf`: Performance improvement
- `chore`: Maintenance (dependencies, tooling, config)
- `style`: Formatting, missing semicolons (not CSS)

### Examples

✅ **Good:**
```
feat: Add VIX-CDX divergence signal computation

Implements z-score normalized gap between equity vol and credit spreads
to identify cross-asset risk sentiment divergence.
```

```
refactor: Extract data loading to separate module

Improves modularity and testability by separating I/O from computation.
```

```
docs: Update persistence layer documentation
```

❌ **Bad:**
```
Added new feature
```

```
Fix: bug in backtest
```

```
update docs.
```

### Multi-file Commits
When changing multiple files, use the most significant type and describe the overall change:
```
refactor: Modernize type hints to Python 3.13 syntax

- Update copilot instructions with new standards
- Add comprehensive Python guidelines document
- Remove legacy Optional/Union usage examples
```

---

## Recommended Agent Prompts

When using Copilot Chat or VS Code inline completions, prefer prompts like:

- "Add a deterministic backtest class that tracks daily P&L and logs parameters."  
- "Refactor this data loader to follow project persistence standards."  
- "Write unit tests for this model to ensure reproducible signal outputs."  
- "Add Streamlit components to visualize signal performance."

Avoid generic prompts like *"optimize this code"* — always specify layer and intent.

---

## Summary

Copilot should behave like a **quantitative developer assistant**, not a strategy designer.  
It should:
- Maintain modularity, transparency, and reproducibility.
- Focus on infrastructure excellence and analytical clarity.
- Produce code ready for production research pipelines.

> Maintained by **stabilefrisur**.  
> Version 1.1 — Optimized for VS Code Agent Mode (Claude Sonnet 4.5 / GPT‑5)  
> Last Updated: October 26, 2025
