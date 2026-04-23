from __future__ import annotations

import unittest

from core.tokenizer import tokenize_source


class TokenizerTests(unittest.TestCase):
    def test_python_tokenize_returns_positioned_tokens(self) -> None:
        source = "def hola(x):\n    return x + 1\n"
        result = tokenize_source(source)

        self.assertIsNone(result.error)
        self.assertGreaterEqual(len(result.tokens), 7)
        self.assertEqual(result.tokens[0].original_text, "def")
        self.assertEqual(result.tokens[0].start_line, 1)
        self.assertEqual(result.tokens[0].char_start, 0)
        self.assertEqual(result.tokens[-1].original_text, "1")


if __name__ == "__main__":
    unittest.main()
