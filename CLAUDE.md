# OmniHarness Instructions for Claude Code

On every session startup:
1. Check OmniHarness memory status by running `python3 -m omniharness.cli status` (or `omniharness status`).
2. Use the ContextCompressor module (`omniharness.compressor` or `omniharness compress`) before reading huge tracebacks, large build logs, or verbose diffs to conserve context window tokens and prevent context bloat.
