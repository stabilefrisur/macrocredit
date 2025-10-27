# Documentation Structure

## Single Source of Truth Principle

| Doc Type | Location | Purpose | Audience |
|----------|----------|---------|----------|
| **API Reference** | Module docstrings | Function/class contracts | Developers (in-editor) |
| **Quickstart** | `README.md` | Installation, examples, overview | New users |
| **Design Docs** | `docs/*.md` | Architecture, standards, strategy | Contributors |
| **Examples** | `examples/*.py` + headers | Runnable demonstrations | Researchers |

**Rule**: Each piece of information has exactly one authoritative location.

---

## Documentation Map

### Root Level
- **`README.md`** - Installation, quickstart, project overview, navigation

### Documentation (`docs/`)
- **`cdx_overlay_strategy.md`** - Investment strategy and implementation
- **`python_guidelines.md`** - Code standards and best practices
- **`logging_design.md`** - Logging conventions and metadata tracking
- **`layer_review_prompt.md`** - Development workflow template
- **`documentation_structure.md`** - This file

### Examples (`examples/`)
- **`README.md`** - Quick start commands and script overview
- **`*_demo.py`** - Self-documenting executable demonstrations

### Source Code (`src/macrocredit/`)
- **Module/function docstrings** - NumPy-style API documentation
- **Inline comments** - Implementation details and rationale

---

## What Belongs Where

### Root `README.md`
✅ Installation, quick start, project structure, links to docs  
❌ Implementation details, API reference, exhaustive examples

### `docs/*.md`
✅ Architecture decisions, design patterns, cross-cutting concerns  
❌ Code usage examples, API documentation, implementation summaries

### `examples/README.md`
✅ Quick run commands, script purpose table  
❌ Detailed explanations (use script headers), code snippets (use actual scripts)

### Demo Script Headers
✅ What it demonstrates, workflow steps, key configuration, expected output  
❌ Installation instructions, design rationale

### Docstrings
✅ API contracts (params, returns, raises), type info, edge cases  
❌ Project overview, installation instructions

---

## Maintenance Workflow

### When Adding a Feature

1. Implement with NumPy-style docstrings
2. Write unit tests
3. Add demo script (if new layer/capability)
4. Update root README (only if affects quickstart)
5. Update design doc (only if architectural change)

### Where to Document

| Question | Location |
|----------|----------|
| "How do I install?" | Root README |
| "How do I use function X?" | Function docstring |
| "How do I run a backtest?" | `backtest_demo.py` header + code |
| "Why this design?" | `docs/*.md` |
| "What's the API?" | Module/function docstrings |

### What NOT to Do

❌ Create README files in implementation directories  
❌ Write "implementation summary" docs in `docs/`  
❌ Duplicate usage examples across files  
❌ Document API details outside docstrings  
❌ Create tutorial-style docs that duplicate demos

---

**Principle**: Executable code (demos, tests, docstrings) is the documentation. Design docs explain *why*, not *how*.
