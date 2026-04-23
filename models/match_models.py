"""Dataclasses compartidas entre el núcleo de comparación y la interfaz."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class SourceFile:
    """Representa un archivo fuente cargado desde disco."""

    path: Path
    text: str
    load_error: str | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()

    @property
    def line_count(self) -> int:
        return len(self.text.splitlines()) or 1


@dataclass(slots=True)
class LexToken:
    """Token obtenido con el lexer estándar de Python."""

    original_text: str
    token_name: str
    token_type: int
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    char_start: int
    char_end: int
    comparable_text: str = ""
    generalized_text: str = ""


@dataclass(slots=True)
class TokenizationResult:
    """Resultado de tokenizar un archivo fuente."""

    tokens: list[LexToken]
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def comparable_sequence(self) -> list[str]:
        return [token.comparable_text for token in self.tokens]

    @property
    def generalized_sequence(self) -> list[str]:
        return [token.generalized_text for token in self.tokens]


@dataclass(slots=True)
class MatchBlock:
    """Bloque contiguo coincidente entre el archivo base y uno comparado."""

    base_start: int
    base_end: int
    other_start: int
    other_end: int
    length: int


@dataclass(slots=True)
class HighlightSpan:
    """Rango absoluto de caracteres para resaltar en pantalla."""

    start: int
    end: int
    block_index: int


@dataclass(slots=True)
class ComparisonResult:
    """Resultado de comparar el archivo base contra otro archivo."""

    base_file: SourceFile
    compared_file: SourceFile
    technique_key: str
    technique_label: str
    similarity_percent: float
    total_common_length: int
    shorter_length: int
    blocks: list[MatchBlock]
    base_highlights: list[HighlightSpan]
    compared_highlights: list[HighlightSpan]
    unit_name: str
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def block_count(self) -> int:
        return len(self.blocks)

