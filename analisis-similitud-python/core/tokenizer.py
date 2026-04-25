# descripcion: tokeniza codigo python y conserva posiciones para resaltar
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

from __future__ import annotations

import token as tokenModule
import tokenize
from io import BytesIO

from models.match_models import LexToken, TokenizationResult


SKIP_TOKEN_TYPES = {
    tokenize.ENCODING,
    tokenize.ENDMARKER,
    tokenize.NL,
    tokenize.NEWLINE,
    tokenize.COMMENT,
    tokenize.INDENT,
    tokenize.DEDENT,
}


# proposito: tokenizar un texto y guardar offsets absolutos
# parametros: text -> codigo fuente original
# retorno: resultado de tokenizacion con lista de tokens y posibles avisos
def tokenizeSource(text: str) -> TokenizationResult:
    warnings: list[str] = []
    tokens: list[LexToken] = []

    # guardamos donde empieza cada linea para convertir linea y columna a offset
    lineStarts = [0]
    for line in text.splitlines(keepends=True):
        lineStarts.append(lineStarts[-1] + len(line))

    if not text.endswith(("\n", "\r")):
        lineStarts.append(len(text))

    # proposito: convertir una posicion linea columna a una posicion absoluta
    # parametros: line -> numero de linea  column -> numero de columna
    # retorno: offset absoluto dentro del texto
    def toOffset(line: int, column: int) -> int:
        validLine = max(0, line)
        lineIndex = min(validLine - 1, len(lineStarts) - 1)
        if validLine == 0:
            lineIndex = 0
        return min(lineStarts[lineIndex] + column, len(text))

    stream = BytesIO(text.encode("utf-8")).readline

    try:
        for tokenInfo in tokenize.tokenize(stream):
            shouldKeep = tokenInfo.type not in SKIP_TOKEN_TYPES
            if shouldKeep:
                startLine, startCol = tokenInfo.start
                endLine, endCol = tokenInfo.end

                # en esta seccion convertimos el token crudo a un objeto mas facil de usar
                tokens.append(
                    LexToken(
                        originalText=tokenInfo.string,
                        tokenName=tokenModule.tok_name.get(tokenInfo.type, str(tokenInfo.type)),
                        tokenType=tokenInfo.type,
                        startLine=startLine,
                        startCol=startCol,
                        endLine=endLine,
                        endCol=endCol,
                        charStart=toOffset(startLine, startCol),
                        charEnd=toOffset(endLine, endCol),
                        comparableText=tokenInfo.string,
                        generalizedText=tokenInfo.string,
                    )
                )
    except (tokenize.TokenError, IndentationError, SyntaxError) as error:
        warnings.append(f"{type(error).__name__}: {error}")
        return TokenizationResult(tokens=tokens, warnings=warnings, error=str(error))

    return TokenizationResult(tokens=tokens, warnings=warnings)
