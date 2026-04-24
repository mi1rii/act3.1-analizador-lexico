# descripcion: construye suffix array y lcp para comparar secuencias
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

from __future__ import annotations


# proposito: construir el suffix array de una secuencia
# parametros: sequence -> lista de simbolos a comparar
# retorno: lista con posiciones de inicio de cada sufijo ordenado
def buildSuffixArray(sequence: list[str]) -> list[int]:
    if not sequence:
        return []

    # nosotros aqui convertimos cada simbolo a un numero para ordenar mas facil
    rankByValue: dict[str, int] = {}
    rank: list[int] = []
    nextRank = 0

    for value in sequence:
        if value not in rankByValue:
            rankByValue[value] = nextRank
            nextRank += 1
        rank.append(rankByValue[value])

    suffixArray = list(range(len(sequence)))
    size = 1
    finished = False

    # en esta parte vamos aumentando el tamano del fragmento con el que comparamos
    while size < len(sequence) and not finished:
        suffixArray.sort(
            key=lambda index: (
                rank[index],
                rank[index + size] if index + size < len(sequence) else -1,
            )
        )

        # aqui recalculamos los rangos despues de ordenar
        newRank = [0] * len(sequence)
        for position in range(1, len(sequence)):
            left = suffixArray[position - 1]
            right = suffixArray[position]

            leftPair = (
                rank[left],
                rank[left + size] if left + size < len(sequence) else -1,
            )
            rightPair = (
                rank[right],
                rank[right + size] if right + size < len(sequence) else -1,
            )

            increase = 1 if leftPair != rightPair else 0
            newRank[right] = newRank[left] + increase

        rank = newRank
        finished = rank[suffixArray[-1]] == len(sequence) - 1
        size *= 2

    return suffixArray


# proposito: calcular el prefijo comun mas largo entre sufijos vecinos
# parametros: sequence -> secuencia original  suffixArray -> suffix array de la secuencia
# retorno: lista lcp con coincidencias entre sufijos consecutivos
def buildLcpArray(sequence: list[str], suffixArray: list[int]) -> list[int]:
    if not sequence:
        return []

    # nosotros aqui guardamos en que lugar quedo cada posicion dentro del suffix array
    order = [0] * len(sequence)
    for position, suffixStart in enumerate(suffixArray):
        order[suffixStart] = position

    # en esta seccion medimos cuanto coincide cada sufijo con el siguiente
    lcp = [0] * max(0, len(sequence) - 1)
    common = 0

    for start in range(len(sequence)):
        position = order[start]
        isLastSuffix = position == len(sequence) - 1

        if isLastSuffix:
            common = 0
        else:
            other = suffixArray[position + 1]
            stillMatching = True

            while stillMatching:
                leftIndex = start + common
                rightIndex = other + common
                leftInside = leftIndex < len(sequence)
                rightInside = rightIndex < len(sequence)
                sameValue = leftInside and rightInside and sequence[leftIndex] == sequence[rightIndex]

                if sameValue:
                    common += 1
                else:
                    stillMatching = False

            lcp[position] = common
            if common > 0:
                common -= 1

    return lcp
