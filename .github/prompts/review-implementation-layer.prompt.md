---
mode: agent
model: Claude Sonnet 4.5
description: 'Review the ${workspaceFolder} implementation layer'
---
# Layer Implementation Review

## Project Context

**Systematic Macro Credit** — Investment research framework prioritizing modularity and simplicity over infrastructure complexity.

**Core Principles:**
- **Research focus:** Minimal infrastructure maintenance burden
- **Function-first:** Classes only when state/lifecycle management needed
- **Extensibility:** Clean interfaces for integrating external packages later
- **Python 3.12:** Modern type syntax (`str | None`, `list[str]`, `dict[str, Any]`)

**Layer Hierarchy:**
```
config/ → data/ ↔ persistence/ → models/ → backtest/ → visualization/
```

**Signal Convention (Models Layer):**
- Positive signal = long credit risk (buy CDX)
- Negative signal = short credit risk (sell CDX)
- Signal names consistent: `cdx_etf_basis`, `cdx_vix_gap`, `spread_momentum`

---

## Review Checklist

### 1. Interface Design
- [ ] Minimal, well-defined public API with clear boundaries
- [ ] Single responsibility per module
- [ ] Uses `Protocol` or `ABC` for swappable components
- [ ] Extension points for integrating external packages
- [ ] Modern Python type annotations throughout

### 2. Code Organization
- [ ] Functions preferred over classes (classes only for state/lifecycle)
- [ ] Data containers use `@dataclass` (frozen for immutable config)
- [ ] No global state — dependencies passed as parameters
- [ ] Modules under 300 lines, single clear purpose
- [ ] Relative imports within package

### 3. Layer Boundaries
- [ ] No upward dependencies (only imports from same/lower layers)
- [ ] Interactions via data structures (DataFrames, dataclasses)
- [ ] Implementation details hidden from other layers
- [ ] No circular dependencies

### 4. Type Safety & Docs
- [ ] Complete type hints using modern Python syntax (no `Optional`, `Union`, `List`, `Dict`)
- [ ] NumPy-style docstrings with Parameters, Returns, Raises, Examples
- [ ] Signal directionality documented (models layer)
- [ ] Public functions fully documented

### 5. Logging
- [ ] Module-level logger: `logger = logging.getLogger(__name__)`
- [ ] Never calls `logging.basicConfig()` in library code
- [ ] Uses %-formatting: `logger.info("Loaded %d rows", n)` not f-strings
- [ ] Appropriate levels: INFO (user ops), DEBUG (details), WARNING (recoverable)

### 6. Testability
- [ ] Pure functions for core logic (deterministic)
- [ ] Dependencies injected, not imported globally
- [ ] Random operations use fixed seeds
- [ ] Corresponding unit tests exist in `tests/` directory

### 7. Pilot Simplicity
- [ ] Minimum viable implementation (no speculative features)
- [ ] Not reinventing pandas/numpy/scipy functionality
- [ ] Error handling proportional to complexity
- [ ] Can defer optimization/caching until needed

---

## Review Output Format

### ✅ Strengths
List 3-5 things done well

### ⚠️ Critical Issues
**Must fix before merging**

For each:
- **Issue:** Description
- **Fix:** Specific recommendation (code snippet if needed)

### ⚠️ Important Issues
**Should fix in this iteration**

For each:
- **Issue:** Description
- **Recommendation:** Suggested improvement

### 🔧 Top Refactoring Opportunities
2-3 concrete suggestions to improve modularity, simplicity, or testability

### 📋 Action Items
Prioritized list:
1. Critical (blockers)
2. Important (this iteration)
3. Nice-to-have (defer)

---

## Review Workflow

**After identifying issues, the agent should:**
1. **Implement fixes directly** using edit/files tool
2. **Run tests** to verify changes don't break functionality
3. **Provide a summary** of changes made with git commit message

**Invoke with:**
```
Review the [layer_name] layer implementation using the concise review prompt.
Focus on: [interface design / layer boundaries / simplicity / etc.]
```

**Files to review:**
- Specify module path or paste code inline

**Agent will:**
1. Apply checklist systematically
2. Identify critical vs. nice-to-have issues
3. **Implement fixes directly** (not just recommend)
4. Run tests to verify correctness
5. Provide git commit message for changes

---

> **Version:** 1.1
> **Optimized for:** Claude Sonnet 4.5 / GPT-5 Agent Mode  
> **Last Updated:** October 27, 2025
