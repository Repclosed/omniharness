# OmniHarness

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%28%2B%29-blue.svg)](https://www.python.org/downloads/)

**OmniHarness** is a lightweight, zero-dependency token optimization harness and persistent memory engine for Claude Code, Cursor, and terminal AI agents. It stops AI coding agents from burning 80% of their token budgets on redundant terminal logs, repetitive tracebacks, and bloated context.

---

## Features

- **Token & Output Compressor**: Trims verbose test output, deduplicates repetitive log spam, compresses complex stack traces, and folds unchanged git diff context.
- **Persistent Memory Engine**: Manages structured markdown memory files with YAML frontmatter and auto-generated `MEMORY.md` indices for persistent agent context across sessions.
- **Rich CLI Interface**: Beautiful, colorized terminal commands powered by `rich`.
- **Python API**: Clean, robust Python modules ready to embed in custom agent pipelines.

---

## Installation

Clone the repository and install in editable mode:

```bash
pip install -r requirements.txt
pip install -e .
```

---

## Usage

### 1. Token Compression

Compress command output, build logs, or stack traces:

```bash
# Compress stdin stream
cat build.log | omniharness compress --strategy dedup --stats

# Compress a specific file with a token budget
omniharness compress traceback.log --strategy traceback --max-tokens 500
```

Available strategies:
- `auto`: Automatically detects tracebacks, diffs, and log spam.
- `dedup`: Suppresses consecutive duplicate lines.
- `traceback`: Condenses stack traces by keeping header, exception, and key frames.
- `diff`: Folds unchanged context in git diffs.
- `trim`: Strict token-budget truncation.

### 2. Persistent Memory Engine

Manage structured memory for your coding agents:

```bash
# Add a memory fact
omniharness memory add coding-standards "Always use type annotations" "All Python functions must have explicit type hints and docstrings." --type feedback

# List stored memories
omniharness memory list

# Search memories
omniharness memory search "type hints"

# Retrieve a specific memory
omniharness memory get coding-standards

# Delete a memory
omniharness memory delete coding-standards
```

### 3. Python API

```python
from omniharness.compressor import compress, estimate_tokens
from omniharness.memory import MemoryEngine

# Compress verbose output
raw_log = "Error: something failed\n" * 100
compressed = compress(raw_log, strategy="dedup")
print(f"Tokens: {estimate_tokens(compressed)}")

# Use memory engine
engine = MemoryEngine()
engine.add_memory("deploy-url", "Production server URL", "https://api.example.com")
mem = engine.get_memory("deploy-url")
print(mem["content"])
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
