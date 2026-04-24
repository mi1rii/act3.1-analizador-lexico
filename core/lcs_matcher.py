# descripcion: encuentra bloques contiguos comunes entre dos secuencias
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

from __future__ import annotations

from core.suffix_array import buildLcpArray, buildSuffixArray
from models.match_models import MatchBlock


SEPARATOR_A = "\u0000<SEP_A>"
SEPARATOR_B = "\u0000<SEP_B>"


# proposito: revisar si dos rangos se traslapan
# parametros: startA endA startB endB -> limites de dos rangos
# retorno: verdadero si hay traslape
def rangesOverlap(startA: int, endA: int, startB: int, endB: int) -> bool:
    return startA < endB and startB < endA


# proposito: encontrar subcadenas comunes largas entre dos secuencias
# parametros: baseSequence otherSequence minMatchLength -> datos para comparar
# retorno: lista de bloques comunes
def findCommonSubstrings(
    baseSequence: list[str],
    otherSequence: list[str],
    minMatchLength: int,
) -> list[MatchBlock]:
    if not baseSequence or not otherSequence:
        return []

    # nosotros aqui juntamos ambas secuencias con separadores para compararlas de una sola vez
    joined = baseSequence + [SEPARATOR_A] + otherSequence + [SEPARATOR_B]
    suffixArray = buildSuffixArray(joined)
    lcp = buildLcpArray(joined, suffixArray)

    baseSize = len(baseSequence)
    otherOffset = baseSize + 1
    candidates: list[MatchBlock] = []

    # en esta parte sacamos candidatos largos a partir del lcp
    for index, commonLength in enumerate(lcp):
        isLongEnough = commonLength >= minMatchLength
        if isLongEnough:
            left = suffixArray[index]
            right = suffixArray[index + 1]
            leftIsBase = left < baseSize
            rightIsBase = right < baseSize

            fromDifferentFiles = leftIsBase != rightIsBase
            if fromDifferentFiles:
                if leftIsBase:
                    baseStart = left
                    otherStart = right - otherOffset
                else:
                    baseStart = right
                    otherStart = left - otherOffset

                validOtherStart = otherStart >= 0
                if validOtherStart:
                    realLength = min(
                        commonLength,
                        len(baseSequence) - baseStart,
                        len(otherSequence) - otherStart,
                    )

                    if realLength >= minMatchLength:
                        candidates.append(
                            MatchBlock(
                                baseStart=baseStart,
                                baseEnd=baseStart + realLength,
                                otherStart=otherStart,
                                otherEnd=otherStart + realLength,
                                length=realLength,
                            )
                        )

    # aqui preferimos los bloques largos y evitamos repetir zonas ya cubiertas
    candidates.sort(key=lambda block: (-block.length, block.baseStart, block.otherStart))
    chosen: list[MatchBlock] = []

    for candidate in candidates:
        repeated = False

        for saved in chosen:
            sameBaseZone = rangesOverlap(
                candidate.baseStart,
                candidate.baseEnd,
                saved.baseStart,
                saved.baseEnd,
            )
            sameOtherZone = rangesOverlap(
                candidate.otherStart,
                candidate.otherEnd,
                saved.otherStart,
                saved.otherEnd,
            )
            if sameBaseZone and sameOtherZone:
                repeated = True

        if not repeated:
            chosen.append(candidate)

    chosen.sort(key=lambda block: (block.baseStart, block.otherStart))
    return chosen
