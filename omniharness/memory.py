"""OmniHarness Persistent Memory Engine.

Manages markdown-based structured agent memories with frontmatter, indexing (MEMORY.md),
and semantic/keyword retrieval.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Any

DEFAULT_MEMORY_DIR = Path.home() / ".claude" / "projects" / "-root-omniharness" / "memory"

class MemoryEngine:
    """Manages persistent structured memories for AI agents."""

    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = Path(memory_dir) if memory_dir else DEFAULT_MEMORY_DIR
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Ensure memory directory and MEMORY.md exist."""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        index_path = self.memory_dir / "MEMORY.md"
        if not index_path.exists():
            index_path.write_text("# Memory Index\n\n", encoding="utf-8")

    def _parse_frontmatter(self, text: str) -> tuple[Dict[str, Any], str]:
        """Parse YAML-like frontmatter from markdown memory file."""
        frontmatter: Dict[str, Any] = {}
        body = text

        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm_text = parts[1]
                body = parts[2].strip()
                for line in fm_text.splitlines():
                    if ":" in line:
                        key, val = line.split(":", 1)
                        key = key.strip()
                        val = val.strip()
                        if key == "metadata":
                            continue
                        frontmatter[key] = val

        return frontmatter, body

    def add_memory(self, name: str, description: str, content: str, memory_type: str = "project") -> Path:
        """Add or update a persistent memory file."""
        self._ensure_dir()
        slug = re.sub(r'[^a-z0-9-]+', '-', name.lower()).strip('-')
        file_path = self.memory_dir / f"{slug}.md"

        frontmatter_content = f"""---
name: {slug}
description: {description}
metadata:
  type: {memory_type}
---

{content.strip()}
"""
        file_path.write_text(frontmatter_content, encoding="utf-8")
        self.rebuild_index()
        return file_path

    def get_memory(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by name/slug."""
        slug = re.sub(r'[^a-z0-9-]+', '-', name.lower()).strip('-')
        file_path = self.memory_dir / f"{slug}.md"
        if not file_path.exists():
            matches = list(self.memory_dir.glob(f"*{slug}*.md"))
            if matches:
                file_path = matches[0]
            else:
                return None

        content = file_path.read_text(encoding="utf-8")
        fm, body = self._parse_frontmatter(content)
        return {
            "name": fm.get("name", file_path.stem),
            "description": fm.get("description", ""),
            "path": str(file_path),
            "content": body
        }

    def list_memories(self) -> List[Dict[str, str]]:
        """List all stored memories."""
        self._ensure_dir()
        memories = []
        for file_path in self.memory_dir.glob("*.md"):
            if file_path.name == "MEMORY.md":
                continue
            try:
                text = file_path.read_text(encoding="utf-8")
                fm, _ = self._parse_frontmatter(text)
                memories.append({
                    "name": fm.get("name", file_path.stem),
                    "description": fm.get("description", ""),
                    "file": file_path.name
                })
            except Exception:
                continue
        return sorted(memories, key=lambda x: x["name"])

    def search_memories(self, query: str) -> List[Dict[str, str]]:
        """Search memories by keyword query in name, description, or content."""
        query_lower = query.lower()
        results = []
        for file_path in self.memory_dir.glob("*.md"):
            if file_path.name == "MEMORY.md":
                continue
            try:
                text = file_path.read_text(encoding="utf-8")
                if query_lower in text.lower():
                    fm, _ = self._parse_frontmatter(text)
                    results.append({
                        "name": fm.get("name", file_path.stem),
                        "description": fm.get("description", ""),
                        "file": file_path.name
                    })
            except Exception:
                continue
        return results

    def delete_memory(self, name: str) -> bool:
        """Delete a memory file by name."""
        slug = re.sub(r'[^a-z0-9-]+', '-', name.lower()).strip('-')
        file_path = self.memory_dir / f"{slug}.md"
        if file_path.exists():
            file_path.unlink()
            self.rebuild_index()
            return True
        return False

    def rebuild_index(self) -> None:
        """Rebuild MEMORY.md index file from existing memory files."""
        index_path = self.memory_dir / "MEMORY.md"
        lines = ["# Memory Index\n"]
        for file_path in sorted(self.memory_dir.glob("*.md")):
            if file_path.name == "MEMORY.md":
                continue
            try:
                text = file_path.read_text(encoding="utf-8")
                fm, _ = self._parse_frontmatter(text)
                title = fm.get("name", file_path.stem)
                desc = fm.get("description", "No description")
                lines.append(f"- [{title}]({file_path.name}) — {desc}")
            except Exception:
                continue

        index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
