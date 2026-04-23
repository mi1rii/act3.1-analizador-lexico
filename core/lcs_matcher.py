"""Búsqueda de subcadenas comunes contiguas mediante suffix array."""

from __future__ import annotations

from models.match_models import MatchBlock

from core.suffix_array import build_lcp_array, build_suffix_array


UNIQUE_SEPARATOR_A = "\u0000<SEP_A>"
UNIQUE_SEPARATOR_B = "\u0000<SEP_B>"


def _ranges_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return not (a_end <= b_start or b_end <= a_start)


def _deduplicate_blocks(blocks: list[MatchBlock]) -> list[MatchBlock]:
    ordered = sorted(
        blocks,
        key=lambda block: (
            -(block.length),
            block.base_start,
            block.other_start,
        ),
    )
    selected: list[MatchBlock] = []
    for candidate in ordered:
        if any(
            _ranges_overlap(candidate.base_start, candidate.base_end, chosen.base_start, chosen.base_end)
            and _ranges_overlap(candidate.other_start, candidate.other_end, chosen.other_start, chosen.other_end)
            for chosen in selected
        ):
            continue
        selected.append(candidate)
    return sorted(selected, key=lambda block: (block.base_start, block.other_start))


def find_common_substrings(
    base_sequence: list[str],
    other_sequence: list[str],
    min_match_length: int,
) -> list[MatchBlock]:
    """Encuentra bloques contiguos comunes usando suffix array + LCP."""

    if not base_sequence or not other_sequence:
        return []

    combined = base_sequence + [UNIQUE_SEPARATOR_A] + other_sequence + [UNIQUE_SEPARATOR_B]
    suffix_array = build_suffix_array(combined)
    lcp = build_lcp_array(combined, suffix_array)
    split_index = len(base_sequence)
    other_offset = len(base_sequence) + 1

    candidates: list[MatchBlock] = []
    for i, common_length in enumerate(lcp):
        if common_length < min_match_length:
            continue
        left = suffix_array[i]
        right = suffix_array[i + 1]

        left_in_base = left < split_index
        right_in_base = right < split_index
        if left_in_base == right_in_base:
            continue

        if left_in_base:
            base_start = left
            other_start = right - other_offset
        else:
            base_start = right
            other_start = left - other_offset

        if other_start < 0:
            continue

        max_length = min(
            common_length,
            len(base_sequence) - base_start,
            len(other_sequence) - other_start,
        )
        if max_length < min_match_length:
            continue

        candidates.append(
            MatchBlock(
                base_start=base_start,
                base_end=base_start + max_length,
                other_start=other_start,
                other_end=other_start + max_length,
                length=max_length,
            )
        )

    return _deduplicate_blocks(candidates)
