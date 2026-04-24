# descripcion: reexporta el motor principal de comparacion
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

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
