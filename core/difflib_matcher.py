# descripcion: genera bloques contiguos con difflib
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

from __future__ import annotations

from difflib import SequenceMatcher

from models.match_models import MatchBlock


# proposito: construir bloques coincidentes usando difflib
# parametros: baseSequence otherSequence minMatchLength -> datos para comparar
# retorno: lista de bloques contiguos
def buildDifflibBlocks(
    baseSequence: list[str] | str,
    otherSequence: list[str] | str,
    minMatchLength: int,
) -> list[MatchBlock]:
    # nosotros aqui dejamos que difflib encuentre bloques contiguos ya iguales
    matcher = SequenceMatcher(None, baseSequence, otherSequence, autojunk=False)
    blocks: list[MatchBlock] = []

    # en esta parte revisamos cada bloque que encuentra difflib
    for match in matcher.get_matching_blocks():
        isLongEnough = match.size >= minMatchLength
        if isLongEnough:
            # aca agregamos solo los bloques que si pasan el umbral minimo
            blocks.append(
                MatchBlock(
                    baseStart=match.a,
                    baseEnd=match.a + match.size,
                    otherStart=match.b,
                    otherEnd=match.b + match.size,
                    length=match.size,
                )
            )

    return blocks
