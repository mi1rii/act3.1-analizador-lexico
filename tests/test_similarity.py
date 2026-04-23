from __future__ import annotations

import unittest
from pathlib import Path

from core.similarity import SimilarityConfig, SimilarityEngine, TECHNIQUE_BAKER
from models.match_models import SourceFile


class SimilarityTests(unittest.TestCase):
    def test_baker_similarity_detects_renamed_code(self) -> None:
        base = SourceFile(
            path=Path("base.py"),
            text=(
                "def suma(a, b):\n"
                "    total = a + b\n"
                "    if total > 10:\n"
                "        return total\n"
                "    return total * 2\n"
            ),
        )
        other = SourceFile(
            path=Path("other.py"),
            text=(
                "def sumar(x, y):\n"
                "    resultado = x + y\n"
                "    if resultado > 10:\n"
                "        return resultado\n"
                "    return resultado * 2\n"
            ),
        )
        engine = SimilarityEngine(SimilarityConfig(min_token_match_length=4, min_text_match_length=8))

        result = engine.compare_pair(base, other, TECHNIQUE_BAKER)

        self.assertGreater(result.similarity_percent, 50.0)
        self.assertGreaterEqual(result.block_count, 1)
        self.assertGreater(result.total_common_length, 0)


if __name__ == "__main__":
    unittest.main()
