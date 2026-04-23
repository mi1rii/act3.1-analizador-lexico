from __future__ import annotations

import unittest

from core.generalizer import apply_generalization
from core.tokenizer import tokenize_source


class GeneralizerTests(unittest.TestCase):
    def test_generalizer_replaces_ids_numbers_and_strings(self) -> None:
        source = 'if total >= 10:\n    mensaje = "hola"\n'
        result = tokenize_source(source)
        apply_generalization(result.tokens)

        generalized = result.generalized_sequence
        self.assertIn("if", generalized)
        self.assertIn("ID", generalized)
        self.assertIn("NUM", generalized)
        self.assertIn("STR", generalized)
        self.assertIn(">=", generalized)


if __name__ == "__main__":
    unittest.main()
