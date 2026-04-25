# descripcion: convierte bloques a rangos reales de texto para resaltar
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

from __future__ import annotations

from collections.abc import Sequence

from models.match_models import HighlightSpan, LexToken, MatchBlock


# proposito: convertir bloques logicos a offsets absolutos de texto
# parametros: blocks baseSource otherSource tokenMode -> datos del bloque y origen
# retorno: tupla con rangos del archivo base y del archivo comparado
def buildHighlightsFromBlocks(
    blocks: list[MatchBlock],
    baseSource: Sequence[LexToken] | str,
    otherSource: Sequence[LexToken] | str,
    tokenMode: bool,
) -> tuple[list[HighlightSpan], list[HighlightSpan]]:
    # pasamos de bloques logicos a rangos reales dentro del texto
    baseSpans: list[HighlightSpan] = []
    otherSpans: list[HighlightSpan] = []

    for blockIndex, block in enumerate(blocks):
        validTokenBlock = not tokenMode or (
            block.baseEnd > block.baseStart and block.otherEnd > block.otherStart
        )

        if validTokenBlock:
            if tokenMode:
                baseStart = baseSource[block.baseStart].charStart
                baseEnd = baseSource[block.baseEnd - 1].charEnd
                otherStart = otherSource[block.otherStart].charStart
                otherEnd = otherSource[block.otherEnd - 1].charEnd
            else:
                baseStart = block.baseStart
                baseEnd = block.baseEnd
                otherStart = block.otherStart
                otherEnd = block.otherEnd

            baseSpans.append(HighlightSpan(baseStart, baseEnd, blockIndex))
            otherSpans.append(HighlightSpan(otherStart, otherEnd, blockIndex))

    return baseSpans, otherSpans


# proposito: sumar la longitud total de rangos sin duplicar traslapes
# parametros: spans -> rangos a sumar
# retorno: longitud total cubierta
def spansTotalLength(spans: list[HighlightSpan]) -> int:
    if not spans:
        return 0

    # ordenamos y fusionamos rangos para no contar dos veces la misma zona
    orderedRanges = sorted((span.start, span.end) for span in spans)
    total = 0
    currentStart, currentEnd = orderedRanges[0]

    for start, end in orderedRanges[1:]:
        touchesCurrent = start <= currentEnd
        if touchesCurrent:
            currentEnd = max(currentEnd, end)
        else:
            total += max(0, currentEnd - currentStart)
            currentStart = start
            currentEnd = end

    total += max(0, currentEnd - currentStart)
    return total
