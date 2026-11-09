"""Unit tests for OmniHarness compressor and memory engine."""

import unittest
from pathlib import Path
import tempfile
import shutil

from omniharness.compressor import strip_ansi, estimate_tokens, dedup_lines, summarize_traceback, compress_diff, compress
from omniharness.memory import MemoryEngine

class TestOmniHarness(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.memory_engine = MemoryEngine(memory_dir=Path(self.test_dir))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_strip_ansi(self):
        colored = "\x1b[31mError message\x1b[0m"
        self.assertEqual(strip_ansi(colored), "Error message")

    def test_estimate_tokens(self):
        text = "Hello world!" # 12 chars -> ~3 tokens
        self.assertGreaterEqual(estimate_tokens(text), 1)
        self.assertEqual(estimate_tokens(""), 0)

    def test_dedup_lines(self):
        text = "line1\nline2\nline2\nline2\nline2\nline3"
        compressed = dedup_lines(text, max_consecutive=1)
        self.assertIn("line1", compressed)
        self.assertIn("line2", compressed)
        self.assertIn("line3", compressed)
        self.assertIn("suppressed", compressed)

    def test_summarize_traceback(self):
        tb = """Traceback (most recent call last):
  File "app.py", line 10, in <module>
    main()
  File "app.py", line 5, in main
    do_something()
ValueError: invalid literal
"""
        res = summarize_traceback(tb, max_frames=2)
        self.assertIn("Traceback", res)
        self.assertIn("ValueError", res)

    def test_compress_diff(self):
        diff = """diff --git a/file.py b/file.py
index 1234567..89abcdef 100644
--- a/file.py
+++ b/file.py
@@ -1,5 +1,5 @@
 context1
 context2
 context3
-old line
+new line
 context4
"""
        res = compress_diff(diff, max_context=1)
        self.assertIn("+new line", res)
        self.assertIn("-old line", res)

    def test_compress_general(self):
        raw = "Hello\nWorld"
        res = compress(raw, max_tokens=10)
        self.assertTrue(len(res) > 0)

    def test_memory_engine(self):
        # Add memory
        path = self.memory_engine.add_memory(
            name="test-memory",
            description="A test memory item",
            content="This is the body of the test memory.",
            memory_type="project"
        )
        self.assertTrue(path.exists())

        # Get memory
        mem = self.memory_engine.get_memory("test-memory")
        self.assertIsNotNone(mem)
        self.assertEqual(mem["name"], "test-memory")
        self.assertEqual(mem["description"], "A test memory item")
        self.assertIn("body of the test", mem["content"])

        # List memories
        mems = self.memory_engine.list_memories()
        self.assertEqual(len(mems), 1)

        # Search memories
        results = self.memory_engine.search_memories("body")
        self.assertEqual(len(results), 1)

        # Delete memory
        success = self.memory_engine.delete_memory("test-memory")
        self.assertTrue(success)
        self.assertIsNone(self.memory_engine.get_memory("test-memory"))

if __name__ == "__main__":
    unittest.main()
