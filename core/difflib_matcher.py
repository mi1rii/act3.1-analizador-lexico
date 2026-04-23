"""Comparación basada en difflib.SequenceMatcher."""

from __future__ import annotations

from difflib import SequenceMatcher

from models.match_models import MatchBlock


def build_difflib_blocks(
    base_sequence: list[str] | str,
    other_sequence: list[str] | str,
    min_match_length: int,
) -> list[MatchBlock]:
    """Obtiene bloques coincidentes contiguos desde SequenceMatcher."""

    matcher = SequenceMatcher(a=base_sequence, b=other_sequence, autojunk=False)
    blocks: list[MatchBlock] = []
    for match in matcher.get_matching_blocks():
        if match.size < min_match_length:
            continue
        blocks.append(
            MatchBlock(
                base_start=match.a,
                base_end=match.a + match.size,
                other_start=match.b,
                other_end=match.b + match.size,
                length=match.size,
            )
        )
    return blocks
