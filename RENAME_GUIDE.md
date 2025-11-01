# Project Rename Guide: macrocredit → aponyx

Complete step-by-step guide for safely renaming the project from "macrocredit" to "aponyx" across local folders, git, GitHub, and all imports.

**Estimated time:** 30-45 minutes

---

## Pre-Rename Checklist

Before starting, ensure:
- [ ] All changes are committed and pushed
- [ ] No uncommitted work in progress
- [ ] Close VS Code and any running processes
- [ ] Create a backup of the project folder ✅ (already done: `macrocredit_backup`)

```bash
# Verify git status
cd c:\Users\ROG3003\PythonProjects\macrocredit
git status

# Commit any pending changes
git add .
git commit -m "chore: Prepare for project rename to aponyx"
git push origin master
```

---

## Step 1: Rename Python Package Directory

```bash
# Navigate to project root
cd c:\Users\ROG3003\PythonProjects\macrocredit

# Rename the package directory
mv src/macrocredit src/aponyx
```

**Verify:** `src/aponyx/` directory exists

---

## Step 2: Update pyproject.toml

Update the project metadata in `pyproject.toml`:

**Change:**
```toml
[project]
name = "aponyx"  # Changed from "macrocredit"
description = "Aponyx - Systematic Macro Credit Strategy Framework"
```

**If you have CLI entry points, update them:**
```toml
[project.scripts]
aponyx = "aponyx.main:main"  # Changed from macrocredit.main:main
```

---

## Step 3: Update All Import Statements

**Use VS Code Find and Replace in Files:**

1. Press `Ctrl+Shift+H` (Find and Replace in Files)
2. Click the `.*` button to enable regex mode

**Replace these patterns (one at a time):**

| Find | Replace | Files Affected |
|------|---------|----------------|
| `from macrocredit` | `from aponyx` | All Python files |
| `import macrocredit` | `import aponyx` | All Python files |
| `"macrocredit"` | `"aponyx"` | Strings in Python files |
| `'macrocredit'` | `'aponyx'` | Strings in Python files |

**Files to review after replacement:**

- [ ] `src/aponyx/**/*.py` - All source code
- [ ] `tests/**/*.py` - All test files
- [ ] `examples/*.py` - All example scripts
- [ ] `examples/end_to_end_demo.ipynb` - Jupyter notebook
- [ ] `docs/**/*.md` - Documentation with code examples
- [ ] `README.md` - Main readme
- [ ] `PROJECT_STATUS.md` - Project status
- [ ] `.github/copilot-instructions.md` - Copilot instructions

---

## Step 4: Update Package Version Info

Update `src/aponyx/__init__.py`:

```python
"""
Aponyx - Systematic Macro Credit Strategy Framework.

A modular Python framework for developing and backtesting systematic credit strategies.
"""

__version__ = "0.1.0"


def hello() -> str:
    """Return greeting message."""
    return "Hello from aponyx!"
```

---

## Step 5: Update README.md

Update project title and all references:

**Title:**
```markdown
# Aponyx

A modular Python framework for developing and backtesting systematic credit strategies.
```

**Installation section:**
```markdown
## Installation

```bash
# Clone repository
git clone https://github.com/stabilefrisur/aponyx.git
cd aponyx

# Create virtual environment with uv
uv venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv sync
```
```

**Quick Start examples:**
```python
from aponyx.data import fetch_cdx
from aponyx.models import compute_cdx_etf_basis
```

**Project Structure:**
```markdown
## Project Structure

```
src/aponyx/           # Main package (changed from macrocredit)
  data/               # Data loading and transformation
  models/             # Signal and strategy logic
  backtest/           # Backtesting engine
  visualization/      # Plotly and Streamlit components
  persistence/        # Data I/O utilities
```
```

---

## Step 6: Update Copilot Instructions

Update `.github/copilot-instructions.md`:

**Header:**
```markdown
# Copilot Instructions — Aponyx Project (VS Code Agent Mode)
```

**Project Overview section:**
```markdown
## Project Overview

You are working within a **systematic fixed-income research environment**.
The Aponyx framework supports:
- Development and testing of **pilot investment strategies**
```

**Repository Layout:**
```markdown
### Repository Layout

```
src/aponyx/           # Changed from macrocredit
  data/               # Loaders, cleaning, transformation
  models/             # Signal & strategy logic
  ...
```
```

**All code examples:**
```python
# Change all examples from:
from macrocredit.data import load_market_data

# To:
from aponyx.data import load_market_data
```

---

## Step 7: Update PROJECT_STATUS.md

Replace all occurrences of "macrocredit" with "aponyx" in:
- File paths
- Import statements
- Project references

---

## Step 8: Update Documentation Files

Check and update all files in `docs/`:

- [ ] `docs/adding_data_providers.md`
- [ ] `docs/caching_design.md`
- [ ] `docs/cdx_overlay_strategy.md`
- [ ] `docs/documentation_structure.md`
- [ ] `docs/logging_design.md`
- [ ] `docs/python_guidelines.md`
- [ ] `docs/signal_registry_usage.md`
- [ ] `docs/visualization_design.md`

**Look for:**
- Import statements in code examples
- File path references
- Project name mentions

---

## Step 9: Update Examples

Update all files in `examples/`:

- [ ] `examples/backtest_demo.py`
- [ ] `examples/data_demo.py`
- [ ] `examples/end_to_end_demo.ipynb` (check markdown cells)
- [ ] `examples/example_data.py`
- [ ] `examples/models_demo.py`
- [ ] `examples/persistence_demo.py`
- [ ] `examples/visualization_demo.py`
- [ ] `examples/README.md`

---

## Step 10: Rename Project Folder

```bash
# Navigate to parent directory
cd c:\Users\ROG3003\PythonProjects

# Rename the project folder
mv macrocredit aponyx

# Navigate into renamed folder
cd aponyx
```

**Verify:** You are now in `c:\Users\ROG3003\PythonProjects\aponyx`

---

## Step 11: Update GitHub Repository

### Option A: Rename Repository on GitHub (Recommended)

1. Go to: `https://github.com/stabilefrisur/macrocredit/settings`
2. Scroll to "Repository name" section
3. Change name to: `aponyx`
4. Click "Rename" button

**GitHub automatically:**
- Redirects old URLs to new repository
- Updates references
- Preserves all issues, PRs, and history

### Option B: Create New Repository

If you prefer a fresh start:

```bash
# Remove old remote
git remote remove origin

# Create new repo "aponyx" on GitHub via web UI

# Add new remote
git remote add origin https://github.com/stabilefrisur/aponyx.git
git push -u origin master
```

---

## Step 12: Update Local Git Configuration

```bash
# Update remote URL (if needed after GitHub rename)
git remote set-url origin https://github.com/stabilefrisur/aponyx.git

# Verify remote
git remote -v
```

**Expected output:**
```
origin  https://github.com/stabilefrisur/aponyx.git (fetch)
origin  https://github.com/stabilefrisur/aponyx.git (push)
```

---

## Step 13: Rebuild Virtual Environment

```bash
# Navigate to project root
cd c:\Users\ROG3003\PythonProjects\aponyx

# Remove old virtual environment
rm -rf .venv

# Create new virtual environment
uv venv

# Activate environment
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# Sync dependencies (installs "aponyx" package)
uv sync

# Install with optional dependencies if needed
uv sync --extra viz --extra dev
```

**Verify installation:**
```bash
uv run python -c "import aponyx; print(aponyx.__version__)"
```

**Expected output:** `0.1.0`

---

## Step 14: Commit and Push Changes

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "refactor: Rename project from macrocredit to aponyx

- Rename Python package directory
- Update all imports and references
- Update project metadata in pyproject.toml
- Update documentation and examples
- Update copilot instructions"

# Push to renamed repository
git push origin master
```

---

## Step 15: Verify Everything Works

Run comprehensive tests to ensure the rename was successful:

```bash
# Run all tests
uv run pytest

# Run specific test modules
uv run pytest tests/data/
uv run pytest tests/models/
uv run pytest tests/backtest/

# Run example scripts
uv run python examples/data_demo.py
uv run python examples/models_demo.py
uv run python examples/backtest_demo.py

# Verify imports
uv run python -c "import aponyx; print('Success')"
uv run python -c "from aponyx.data import fetch_cdx; print('Success')"
uv run python -c "from aponyx.models import compute_cdx_etf_basis; print('Success')"
```

---

## Verification Checklist

After completing all steps, verify:

- [ ] `src/aponyx/` directory exists (not `src/macrocredit/`)
- [ ] Project folder is `aponyx/` (not `macrocredit/`)
- [ ] GitHub repository renamed to `aponyx`
- [ ] All imports use `from aponyx` (not `from macrocredit`)
- [ ] `pyproject.toml` has `name = "aponyx"`
- [ ] Tests pass: `uv run pytest`
- [ ] Examples run without import errors
- [ ] Git remote points to new repository URL
- [ ] Documentation updated with new name
- [ ] Virtual environment rebuilt successfully
- [ ] No references to "macrocredit" in code (search to verify)

---

## Common Issues and Solutions

### Issue: Import errors after rename

**Symptom:** `ModuleNotFoundError: No module named 'macrocredit'`

**Solution:**
```bash
# Rebuild virtual environment
rm -rf .venv
uv venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
uv sync
```

### Issue: Git push fails to old repository

**Symptom:** `remote: Repository not found`

**Solution:**
```bash
# Update remote URL
git remote set-url origin https://github.com/stabilefrisur/aponyx.git
git remote -v  # Verify
```

### Issue: VS Code still shows old package name

**Solution:**
- Restart VS Code
- `Ctrl+Shift+P` → "Developer: Reload Window"
- Close and reopen workspace

### Issue: Pytest can't find modules

**Solution:**
```bash
# Verify pytest configuration in pyproject.toml
# Should have:
[tool.pytest.ini_options]
pythonpath = "src"
```

### Issue: Some files still reference "macrocredit"

**Solution:**
```bash
# Search for any remaining references
grep -r "macrocredit" --include="*.py" --include="*.md" --include="*.toml"

# Manually update any found references
```

---

## Post-Rename Tasks

1. **Update GitHub repository settings:**
   - Description: "Aponyx - Systematic Macro Credit Strategy Framework"
   - Website: (if applicable)
   - Topics: `python`, `credit-trading`, `systematic-strategy`, `fixed-income`

2. **Update social preview image** (if you had one)

3. **Notify collaborators** of the rename (if applicable)

4. **Update any external links** to the repository

5. **Delete backup folder** (after confirming everything works):
   ```bash
   rm -rf c:\Users\ROG3003\PythonProjects\macrocredit_backup
   ```

---

## Rollback Plan

If something goes wrong and you need to rollback:

```bash
# Navigate to parent directory
cd c:\Users\ROG3003\PythonProjects

# Remove failed rename
rm -rf aponyx

# Restore from backup
cp -r macrocredit_backup macrocredit

# Navigate back to project
cd macrocredit

# Reset git if needed
git reset --hard HEAD
```

---

## Summary

This guide covers:
- ✅ Renaming Python package directory
- ✅ Updating all imports and references
- ✅ Updating project metadata
- ✅ Renaming project folder
- ✅ Updating GitHub repository
- ✅ Rebuilding virtual environment
- ✅ Comprehensive verification
- ✅ Troubleshooting common issues

**Total steps:** 15
**Time required:** 30-45 minutes
**Difficulty:** Moderate

---

**Last updated:** November 1, 2025
**Project:** Aponyx (formerly macrocredit)
**Author:** stabilefrisur
