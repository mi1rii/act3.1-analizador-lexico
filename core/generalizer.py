# descripcion: generaliza tokens para comparar estructura y no nombres exactos
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

from __future__ import annotations

import keyword
import tokenize

from models.match_models import LexToken


# proposito: convertir un token a su forma generalizada
# parametros: token -> token original del codigo
# retorno: texto generalizado del token
def generalizeToken(token: LexToken) -> str:
    # nosotros aqui reducimos diferencias superficiales para comparar la forma del codigo
    isName = token.tokenType == tokenize.NAME
    isKeyword = keyword.iskeyword(token.originalText)
    isNumber = token.tokenType == tokenize.NUMBER
    isString = token.tokenType == tokenize.STRING

    if isName and not isKeyword:
        return "ID"
    if isNumber:
        return "NUM"
    if isString:
        return "STR"
    return token.originalText


# proposito: aplicar la generalizacion a una lista de tokens
# parametros: tokens -> lista de tokens del archivo
# retorno: la misma lista con sus campos de comparacion actualizados
def applyGeneralization(tokens: list[LexToken]) -> list[LexToken]:
    # en esta seccion dejamos lista la forma original y la forma generalizada
    for token in tokens:
        token.comparableText = token.originalText
        token.generalizedText = generalizeToken(token)
    return tokens
