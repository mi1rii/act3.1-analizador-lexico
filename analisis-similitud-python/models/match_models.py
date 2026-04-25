# descripcion: modelos de datos compartidos entre el nucleo y la interfaz
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class SourceFile:
    path: Path
    text: str
    loadError: str | None = None
    warnings: list[str] = field(default_factory=list)

    # proposito: devolver el nombre del archivo
    # parametros: ninguno
    # retorno: nombre del archivo sin la ruta
    @property
    def name(self) -> str:
        return self.path.name

    # proposito: devolver la extension del archivo
    # parametros: ninguno
    # retorno: extension en minusculas
    @property
    def extension(self) -> str:
        return self.path.suffix.lower()

    # proposito: contar cuantas lineas tiene el archivo
    # parametros: ninguno
    # retorno: total de lineas del texto
    @property
    def lineCount(self) -> int:
        return len(self.text.splitlines()) or 1


@dataclass(slots=True)
class LexToken:
    originalText: str
    tokenName: str
    tokenType: int
    startLine: int
    startCol: int
    endLine: int
    endCol: int
    charStart: int
    charEnd: int
    comparableText: str = ""
    generalizedText: str = ""


@dataclass(slots=True)
class TokenizationResult:
    tokens: list[LexToken]
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    # proposito: obtener la secuencia comparable original
    # parametros: ninguno
    # retorno: lista de textos comparables
    @property
    def comparableSequence(self) -> list[str]:
        return [token.comparableText for token in self.tokens]

    # proposito: obtener la secuencia ya generalizada
    # parametros: ninguno
    # retorno: lista de textos generalizados
    @property
    def generalizedSequence(self) -> list[str]:
        return [token.generalizedText for token in self.tokens]


@dataclass(slots=True)
class MatchBlock:
    baseStart: int
    baseEnd: int
    otherStart: int
    otherEnd: int
    length: int


@dataclass(slots=True)
class HighlightSpan:
    start: int
    end: int
    blockIndex: int


@dataclass(slots=True)
class ComparisonResult:
    baseFile: SourceFile
    comparedFile: SourceFile
    techniqueKey: str
    techniqueLabel: str
    similarityPercent: float
    totalCommonLength: int
    shorterLength: int
    blocks: list[MatchBlock]
    baseHighlights: list[HighlightSpan]
    comparedHighlights: list[HighlightSpan]
    unitName: str
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    # proposito: contar cuantos bloques trae el resultado
    # parametros: ninguno
    # retorno: cantidad de bloques encontrados
    @property
    def blockCount(self) -> int:
        return len(self.blocks)
