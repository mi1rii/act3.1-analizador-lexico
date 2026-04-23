"""Motor de similitud y cálculo de porcentajes."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from core.difflib_matcher import build_difflib_blocks
from core.generalizer import apply_generalization
from core.highlight_mapper import build_highlights_from_blocks
from core.lcs_matcher import find_common_substrings
from core.tokenizer import tokenize_source
from models.match_models import ComparisonResult, MatchBlock, SourceFile, TokenizationResult


TECHNIQUE_BAKER = "baker"
TECHNIQUE_LCS_TEXT = "lcs_text"
TECHNIQUE_DIFF_TOKEN = "difflib_token"
TECHNIQUE_DIFF_TEXT = "difflib_text"


TECHNIQUE_LABELS = {
    TECHNIQUE_BAKER: "Baker tokenizado + generalizacion + suffix array + LCS",
    TECHNIQUE_LCS_TEXT: "LCS texto plano",
    TECHNIQUE_DIFF_TOKEN: "difflib tokenizado",
    TECHNIQUE_DIFF_TEXT: "difflib texto plano",
}


@dataclass(slots=True)
class SimilarityConfig:
    """Parámetros configurables para filtrar coincidencias triviales."""

    min_token_match_length: int = 8
    min_text_match_length: int = 30


class SimilarityEngine:
    """Orquesta las cuatro técnicas de comparación."""

    def __init__(self, config: SimilarityConfig | None = None) -> None:
        self.config = config or SimilarityConfig()

    @lru_cache(maxsize=256)
    def _tokenize_cached(self, path_key: str, text: str) -> TokenizationResult:
        result = tokenize_source(text)
        apply_generalization(result.tokens)
        return result

    def tokenize_file(self, source_file: SourceFile) -> TokenizationResult:
        return self._tokenize_cached(str(source_file.path.resolve()), source_file.text)

    def compare_all(
        self,
        base_file: SourceFile,
        source_files: list[SourceFile],
        technique_key: str,
    ) -> list[ComparisonResult]:
        results = [
            self.compare_pair(base_file, other_file, technique_key)
            for other_file in source_files
            if other_file.path != base_file.path
        ]
        results.sort(key=lambda result: result.similarity_percent, reverse=True)
        return results

    def compare_pair(
        self,
        base_file: SourceFile,
        other_file: SourceFile,
        technique_key: str,
    ) -> ComparisonResult:
        warnings: list[str] = [*base_file.warnings, *other_file.warnings]
        error: str | None = None
        unit_name = "tokens" if technique_key in {TECHNIQUE_BAKER, TECHNIQUE_DIFF_TOKEN} else "caracteres"
        blocks: list[MatchBlock] = []
        base_highlights = []
        other_highlights = []
        total_common_length = 0
        shorter_length = 0

        if technique_key == TECHNIQUE_BAKER:
            base_tokens = self.tokenize_file(base_file)
            other_tokens = self.tokenize_file(other_file)
            warnings.extend(base_tokens.warnings)
            warnings.extend(other_tokens.warnings)
            blocks = find_common_substrings(
                base_tokens.generalized_sequence,
                other_tokens.generalized_sequence,
                self.config.min_token_match_length,
            )
            base_highlights, other_highlights = build_highlights_from_blocks(
                blocks,
                base_tokens.tokens,
                other_tokens.tokens,
                token_mode=True,
            )
            shorter_length = min(
                len(base_tokens.generalized_sequence),
                len(other_tokens.generalized_sequence),
            )
        elif technique_key == TECHNIQUE_LCS_TEXT:
            blocks = find_common_substrings(
                list(base_file.text),
                list(other_file.text),
                self.config.min_text_match_length,
            )
            base_highlights, other_highlights = build_highlights_from_blocks(
                blocks,
                base_file.text,
                other_file.text,
                token_mode=False,
            )
            shorter_length = min(len(base_file.text), len(other_file.text))
        elif technique_key == TECHNIQUE_DIFF_TOKEN:
            base_tokens = self.tokenize_file(base_file)
            other_tokens = self.tokenize_file(other_file)
            warnings.extend(base_tokens.warnings)
            warnings.extend(other_tokens.warnings)
            blocks = build_difflib_blocks(
                base_tokens.comparable_sequence,
                other_tokens.comparable_sequence,
                self.config.min_token_match_length,
            )
            base_highlights, other_highlights = build_highlights_from_blocks(
                blocks,
                base_tokens.tokens,
                other_tokens.tokens,
                token_mode=True,
            )
            shorter_length = min(
                len(base_tokens.comparable_sequence),
                len(other_tokens.comparable_sequence),
            )
        elif technique_key == TECHNIQUE_DIFF_TEXT:
            blocks = build_difflib_blocks(
                base_file.text,
                other_file.text,
                self.config.min_text_match_length,
            )
            base_highlights, other_highlights = build_highlights_from_blocks(
                blocks,
                base_file.text,
                other_file.text,
                token_mode=False,
            )
            shorter_length = min(len(base_file.text), len(other_file.text))
        else:
            error = f"Tecnica no soportada: {technique_key}"

        total_common_length = min(
            _total_block_length(blocks, "base"),
            _total_block_length(blocks, "other"),
        )
        similarity_percent = (
            (total_common_length / shorter_length) * 100.0 if shorter_length else 0.0
        )

        if not blocks and technique_key in {TECHNIQUE_BAKER, TECHNIQUE_DIFF_TOKEN} and not error:
            warnings.append(
                "No se detectaron bloques tokenizados con el umbral actual."
            )

        return ComparisonResult(
            base_file=base_file,
            compared_file=other_file,
            technique_key=technique_key,
            technique_label=TECHNIQUE_LABELS.get(technique_key, technique_key),
            similarity_percent=similarity_percent,
            total_common_length=total_common_length,
            shorter_length=shorter_length,
            blocks=blocks,
            base_highlights=base_highlights,
            compared_highlights=other_highlights,
            unit_name=unit_name,
            warnings=warnings,
            error=error,
        )


def _merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not ranges:
        return []

    ordered = sorted(ranges)
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        current_start, current_end = merged[-1]
        if start <= current_end:
            merged[-1] = (current_start, max(current_end, end))
            continue
        merged.append((start, end))
    return merged


def _total_block_length(blocks: list[MatchBlock], side: str) -> int:
    if side == "base":
        ranges = [(block.base_start, block.base_end) for block in blocks]
    else:
        ranges = [(block.other_start, block.other_end) for block in blocks]
    return sum(max(0, end - start) for start, end in _merge_ranges(ranges))
