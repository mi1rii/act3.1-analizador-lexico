"""Reexporta el motor principal de comparación."""

from core.similarity import (
    SimilarityConfig,
    SimilarityEngine,
    TECHNIQUE_BAKER,
    TECHNIQUE_DIFF_TEXT,
    TECHNIQUE_DIFF_TOKEN,
    TECHNIQUE_LABELS,
    TECHNIQUE_LCS_TEXT,
)

__all__ = [
    "SimilarityConfig",
    "SimilarityEngine",
    "TECHNIQUE_BAKER",
    "TECHNIQUE_DIFF_TEXT",
    "TECHNIQUE_DIFF_TOKEN",
    "TECHNIQUE_LABELS",
    "TECHNIQUE_LCS_TEXT",
]
