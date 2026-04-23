"""Mapeo de coincidencias a rangos absolutos de texto."""

from __future__ import annotations

from collections.abc import Sequence

from models.match_models import HighlightSpan, LexToken, MatchBlock


def _merge_spans(spans: list[HighlightSpan]) -> list[HighlightSpan]:
    if not spans:
        return []

    ordered = sorted(spans, key=lambda span: (span.start, span.end))
    merged = [ordered[0]]
    for span in ordered[1:]:
        current = merged[-1]
        if span.start <= current.end:
            current.end = max(current.end, span.end)
            continue
        merged.append(span)
    return merged


def build_highlights_from_blocks(
    blocks: list[MatchBlock],
    base_source: Sequence[LexToken] | str,
    other_source: Sequence[LexToken] | str,
    token_mode: bool,
) -> tuple[list[HighlightSpan], list[HighlightSpan]]:
    """Convierte bloques en rangos absolutos de caracteres."""

    base_spans: list[HighlightSpan] = []
    other_spans: list[HighlightSpan] = []
    for index, block in enumerate(blocks):
        if token_mode:
            if block.base_end <= block.base_start or block.other_end <= block.other_start:
                continue
            base_start = base_source[block.base_start].char_start
            base_end = base_source[block.base_end - 1].char_end
            other_start = other_source[block.other_start].char_start
            other_end = other_source[block.other_end - 1].char_end
        else:
            base_start = block.base_start
            base_end = block.base_end
            other_start = block.other_start
            other_end = block.other_end

        base_spans.append(HighlightSpan(start=base_start, end=base_end, block_index=index))
        other_spans.append(HighlightSpan(start=other_start, end=other_end, block_index=index))

    return base_spans, other_spans


def spans_total_length(spans: list[HighlightSpan]) -> int:
    """Suma la longitud de rangos ya fusionados para evitar doble conteo."""

    return sum(max(0, span.end - span.start) for span in _merge_spans(spans))
