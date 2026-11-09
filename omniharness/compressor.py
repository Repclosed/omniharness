"""OmniHarness Context & Output Compressor.

Reduces token waste from verbose command outputs, repetitive terminal logs,
stack traces, and raw diffs without losing semantic meaning.
"""

import re
from typing import Optional, List

ANSI_ESCAPE_RE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from terminal output."""
    return ANSI_ESCAPE_RE.sub('', text)

def estimate_tokens(text: str) -> int:
    """Estimate token count using a standard heuristic (~4 characters per token)."""
    if not text:
        return 0
    return max(1, len(text) // 4)

def dedup_lines(text: str, max_consecutive: int = 2) -> str:
    """Deduplicate excessive consecutive identical lines or log spam."""
    lines = text.splitlines()
    if not lines:
        return text

    result: List[str] = []
    last_line = None
    consecutive_count = 0

    for line in lines:
        if line == last_line:
            consecutive_count += 1
            if consecutive_count <= max_consecutive:
                result.append(line)
            elif consecutive_count == max_consecutive + 1:
                result.append(f"... [repeated {consecutive_count} times suppressed] ...")
        else:
            last_line = line
            consecutive_count = 1
            result.append(line)

    return "\n".join(result)

def summarize_traceback(text: str, max_frames: int = 10) -> str:
    """Compress long stack traces by retaining essential exception info and key frames."""
    lines = text.splitlines()
    if not lines:
        return text

    # Check if there's a traceback marker
    has_tb = any("Traceback (most recent call last):" in line for line in lines)
    if not has_tb:
        return text

    header_idx = 0
    for i, line in enumerate(lines):
        if "Traceback (most recent call last):" in line:
            header_idx = i
            break

    header = lines[:header_idx]
    tb_lines = lines[header_idx:]

    # Separate frames and exception message
    frames = []
    exception_lines = []
    is_exception = False

    for line in tb_lines:
        if line.startswith("  File ") or line.startswith("    "):
            if not is_exception:
                frames.append(line)
        else:
            if "Error:" in line or "Exception:" in line or line.strip() and not line.startswith(" "):
                is_exception = True
            if is_exception:
                exception_lines.append(line)

    if len(frames) > max_frames:
        # Keep first few and last few frames
        half = max_frames // 2
        omitted_count = len(frames) - max_frames
        compressed_frames = frames[:half] + [f"    ... [{omitted_count} intermediate stack frames omitted] ..."] + frames[-half:]
    else:
        compressed_frames = frames

    return "\n".join(header + compressed_frames + exception_lines)

def compress_diff(text: str, max_context: int = 3) -> str:
    """Compress git diffs by trimming unneeded context lines."""
    lines = text.splitlines()
    result: List[str] = []
    context_buffer: List[str] = []

    for line in lines:
        if line.startswith('+') or line.startswith('-') or line.startswith('@@'):
            if context_buffer and len(context_buffer) > (max_context * 2):
                result.append(context_buffer[0])
                result.append(f"  ... [{len(context_buffer) - 2} unchanged lines folded] ...")
                result.append(context_buffer[-1])
            else:
                result.extend(context_buffer)
            context_buffer = []
            result.append(line)
        else:
            context_buffer.append(line)

    if context_buffer:
        result.extend(context_buffer)

    return "\n".join(result)

def compress(text: str, strategy: str = "auto", max_tokens: Optional[int] = None) -> str:
    """Compress text according to specified strategy ('auto', 'dedup', 'traceback', 'diff', 'trim')."""
    if not text:
        return ""

    cleaned = strip_ansi(text)

    if strategy in ("auto", "traceback") and "Traceback" in cleaned:
        cleaned = summarize_traceback(cleaned)

    if strategy in ("auto", "diff") and ("diff --git" in cleaned or "--- a/" in cleaned):
        cleaned = compress_diff(cleaned)

    if strategy in ("auto", "dedup"):
        cleaned = dedup_lines(cleaned)

    if max_tokens is not None:
        current_tokens = estimate_tokens(cleaned)
        if current_tokens > max_tokens:
            max_chars = max_tokens * 4
            cleaned = cleaned[:max_chars] + f"\n\n... [Truncated: {current_tokens} est. tokens exceeded limit of {max_tokens}] ..."

    return cleaned
