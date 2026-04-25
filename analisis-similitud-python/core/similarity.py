# descripcion: aplica las cuatro tecnicas de similitud del proyecto
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from core.difflib_matcher import buildDifflibBlocks
from core.generalizer import applyGeneralization
from core.highlight_mapper import buildHighlightsFromBlocks
from core.lcs_matcher import findCommonSubstrings
from core.tokenizer import tokenizeSource
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
    minTokenMatchLength: int = 8
    minTextMatchLength: int = 30


class SimilarityEngine:
    # proposito: crear el motor con sus umbrales de comparacion
    # parametros: config -> configuracion opcional
    # retorno: ninguno
    def __init__(self, config: SimilarityConfig | None = None) -> None:
        self.config = config or SimilarityConfig()

    # proposito: tokenizar y generalizar un archivo usando cache
    # parametros: pathKey -> identificador del archivo  text -> contenido del archivo
    # retorno: resultado de tokenizacion y generalizacion
    @lru_cache(maxsize=256)
    def tokenizeCached(self, pathKey: str, text: str) -> TokenizationResult:
        # guardamos tokenizaciones repetidas para no recalcularlas siempre
        result = tokenizeSource(text)
        applyGeneralization(result.tokens)
        return result

    # proposito: tokenizar un archivo fuente del proyecto
    # parametros: sourceFile -> archivo a tokenizar
    # retorno: resultado de tokenizacion
    def tokenizeFile(self, sourceFile: SourceFile) -> TokenizationResult:
        return self.tokenizeCached(str(sourceFile.path.resolve()), sourceFile.text)

    # proposito: comparar un archivo base contra todos los demas
    # parametros: baseFile sourceFiles techniqueKey -> datos para comparar
    # retorno: lista de resultados ordenados por similitud
    def compareAll(
        self,
        baseFile: SourceFile,
        sourceFiles: list[SourceFile],
        techniqueKey: str,
    ) -> list[ComparisonResult]:
        results: list[ComparisonResult] = []

        for otherFile in sourceFiles:
            isDifferentFile = otherFile.path != baseFile.path
            if isDifferentFile:
                results.append(self.comparePair(baseFile, otherFile, techniqueKey))

        results.sort(key=lambda result: result.similarityPercent, reverse=True)
        return results

    # proposito: comparar dos archivos con una tecnica especifica
    # parametros: baseFile otherFile techniqueKey -> archivos y tecnica a usar
    # retorno: resultado completo de la comparacion
    def comparePair(
        self,
        baseFile: SourceFile,
        otherFile: SourceFile,
        techniqueKey: str,
    ) -> ComparisonResult:
        warnings = [*baseFile.warnings, *otherFile.warnings]
        error: str | None = None
        blocks: list[MatchBlock] = []
        baseHighlights: list = []
        otherHighlights: list = []
        tokenTechnique = techniqueKey in {TECHNIQUE_BAKER, TECHNIQUE_DIFF_TOKEN}
        unitName = "tokens" if tokenTechnique else "caracteres"

        baseTokens = None
        otherTokens = None
        if tokenTechnique:
            # en esta parte preparamos tokens una sola vez para las tecnicas lexicas
            baseTokens = self.tokenizeFile(baseFile)
            otherTokens = self.tokenizeFile(otherFile)
            warnings.extend(baseTokens.warnings)
            warnings.extend(otherTokens.warnings)

        if techniqueKey == TECHNIQUE_BAKER:
            # aqui comparamos la secuencia generalizada y no el texto crudo
            blocks = findCommonSubstrings(
                baseTokens.generalizedSequence,
                otherTokens.generalizedSequence,
                self.config.minTokenMatchLength,
            )
            baseHighlights, otherHighlights = buildHighlightsFromBlocks(
                blocks,
                baseTokens.tokens,
                otherTokens.tokens,
                True,
            )
            shorterLength = min(
                len(baseTokens.generalizedSequence),
                len(otherTokens.generalizedSequence),
            )
        elif techniqueKey == TECHNIQUE_LCS_TEXT:
            # nosotros aqui comparamos el texto plano caracter por caracter
            blocks = findCommonSubstrings(
                list(baseFile.text),
                list(otherFile.text),
                self.config.minTextMatchLength,
            )
            baseHighlights, otherHighlights = buildHighlightsFromBlocks(
                blocks,
                baseFile.text,
                otherFile.text,
                False,
            )
            shorterLength = min(len(baseFile.text), len(otherFile.text))
        elif techniqueKey == TECHNIQUE_DIFF_TOKEN:
            # en esta tecnica usamos difflib pero sobre tokens
            blocks = buildDifflibBlocks(
                baseTokens.comparableSequence,
                otherTokens.comparableSequence,
                self.config.minTokenMatchLength,
            )
            baseHighlights, otherHighlights = buildHighlightsFromBlocks(
                blocks,
                baseTokens.tokens,
                otherTokens.tokens,
                True,
            )
            shorterLength = min(
                len(baseTokens.comparableSequence),
                len(otherTokens.comparableSequence),
            )
        elif techniqueKey == TECHNIQUE_DIFF_TEXT:
            # en esta tecnica usamos difflib directamente sobre texto plano
            blocks = buildDifflibBlocks(
                baseFile.text,
                otherFile.text,
                self.config.minTextMatchLength,
            )
            baseHighlights, otherHighlights = buildHighlightsFromBlocks(
                blocks,
                baseFile.text,
                otherFile.text,
                False,
            )
            shorterLength = min(len(baseFile.text), len(otherFile.text))
        else:
            shorterLength = 0
            error = f"tecnica no soportada: {techniqueKey}"

        # aqui calculamos cuanto contenido comun existe sin duplicar zonas traslapadas
        totalCommonLength = min(
            countCoveredLength(blocks, True),
            countCoveredLength(blocks, False),
        )
        similarityPercent = (totalCommonLength / shorterLength * 100.0) if shorterLength else 0.0

        noBlocks = not blocks
        tokenWarning = tokenTechnique and not error and noBlocks
        if tokenWarning:
            warnings.append("no se detectaron bloques tokenizados con el umbral actual")

        return ComparisonResult(
            baseFile=baseFile,
            comparedFile=otherFile,
            techniqueKey=techniqueKey,
            techniqueLabel=TECHNIQUE_LABELS.get(techniqueKey, techniqueKey),
            similarityPercent=similarityPercent,
            totalCommonLength=totalCommonLength,
            shorterLength=shorterLength,
            blocks=blocks,
            baseHighlights=baseHighlights,
            comparedHighlights=otherHighlights,
            unitName=unitName,
            warnings=warnings,
            error=error,
        )


# proposito: sumar bloques sin contar dos veces las zonas traslapadas
# parametros: blocks -> bloques encontrados  useBaseSide -> lado del bloque a sumar
# retorno: longitud total cubierta
def countCoveredLength(blocks: list[MatchBlock], useBaseSide: bool) -> int:
    # juntamos rangos del lado base o del lado comparado
    ranges: list[tuple[int, int]] = []
    for block in blocks:
        if useBaseSide:
            ranges.append((block.baseStart, block.baseEnd))
        else:
            ranges.append((block.otherStart, block.otherEnd))

    if not ranges:
        return 0

    # en esta seccion fusionamos rangos antes de sumarlos
    ranges.sort()
    total = 0
    currentStart, currentEnd = ranges[0]

    for start, end in ranges[1:]:
        touchesCurrent = start <= currentEnd
        if touchesCurrent:
            currentEnd = max(currentEnd, end)
        else:
            total += max(0, currentEnd - currentStart)
            currentStart = start
            currentEnd = end

    total += max(0, currentEnd - currentStart)
    return total
