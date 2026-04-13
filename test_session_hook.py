import json
import os
import tempfile
import unittest

from session_hook import calculate_used_tokens, calculate_turn_tokens, _tree_message
from forest import forest_lines

EXAMPLE = os.path.join(os.path.dirname(__file__), "test_transcript.jsonl")


def _assistant_line(input_tokens: int, output_tokens: int) -> str:
    return json.dumps({
        "type": "assistant",
        "message": {"usage": {"input_tokens": input_tokens, "output_tokens": output_tokens}},
    })


def _user_line() -> str:
    return json.dumps({"type": "user", "message": {"content": []}})


class TestCalculateUsedTokens(unittest.TestCase):
    def test_full_transcript(self):
        result = calculate_used_tokens(EXAMPLE)
        self.assertEqual(result, 131225)

    def test_missing_file(self):
        self.assertEqual(calculate_used_tokens("/nonexistent/path.jsonl"), 0)


class TestCalculateTurnTokens(unittest.TestCase):
    def _write(self, lines: list[str]) -> str:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        f.write("\n".join(lines))
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_no_user_message_counts_all_tokens(self):
        path = self._write([
            _assistant_line(100, 50),
            _assistant_line(200, 75),
        ])
        self.assertEqual(calculate_turn_tokens(path), 425)

    def test_counts_only_tokens_after_last_user_message(self):
        path = self._write([
            _assistant_line(100, 50),   # earlier turn — excluded
            _user_line(),
            _assistant_line(200, 75),   # earlier turn — excluded
            _user_line(),               # last user message
            _assistant_line(300, 100),  # current turn — included
        ])
        self.assertEqual(calculate_turn_tokens(path), 400)

    def test_multiple_trees_worth_of_tokens(self):
        # Verify the count is correct when a turn generates a large token count
        path = self._write([
            _user_line(),
            _assistant_line(600_000, 400_000),  # 1M tokens — one tree's worth
            _assistant_line(600_000, 400_000),  # another 1M — two trees total
        ])
        self.assertEqual(calculate_turn_tokens(path), 2_000_000)

    def test_missing_file(self):
        self.assertEqual(calculate_turn_tokens("/nonexistent/path.jsonl"), 0)


class TestTreeMessage(unittest.TestCase):
    def test_singular(self):
        self.assertEqual(_tree_message(1), "\033[92m🌱 You planted a tree!\033[0m")

    def test_plural(self):
        self.assertEqual(_tree_message(2), "\033[92m🌱 You planted 2 trees!\033[0m")
        self.assertEqual(_tree_message(5), "\033[92m🌱 You planted 5 trees!\033[0m")


class TestForestLines(unittest.TestCase):
    def test_no_trees(self):
        lines = forest_lines(0, 0, "🌱")
        self.assertEqual(lines, ["  (no trees yet — keep coding!)"])

    def test_only_old_trees(self):
        lines = forest_lines(3, 0, "🌱")
        self.assertEqual(lines, ["  🌳  🌳  🌳"])

    def test_only_new_trees(self):
        lines = forest_lines(0, 2, "🌱")
        self.assertEqual(lines, ["  🌱  🌱"])

    def test_old_and_new_trees(self):
        lines = forest_lines(2, 2, "🌿")
        self.assertEqual(lines, ["  🌳  🌳  🌿  🌿"])

    def test_wraps_at_ten_columns(self):
        lines = forest_lines(10, 2, "🌱")
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0].strip().count("🌳"), 10)
        self.assertEqual(lines[1].strip().count("🌱"), 2)

    def test_new_icon_reflects_growth_stage(self):
        for icon in ["🌱", "🌿", "🌳"]:
            lines = forest_lines(0, 1, icon)
            self.assertIn(icon, lines[0])


if __name__ == "__main__":
    unittest.main()
