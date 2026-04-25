# descripcion: analizador lexico de c basado en ply para reconocer un subconjunto didactico del lenguaje
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

from __future__ import annotations

import re
import sys

import ply.lex as lex


class Token:
    # proposito: guardar la informacion basica de un token reconocido por el lexer
    # parametros: tokenType -> tipo del token  value -> texto original  line -> linea donde aparece
    # retorno: instancia inicializada del token
    def __init__(self, tokenType: str, value: str, line: int):
        self.type = tokenType
        self.value = value
        self.line = line

    # proposito: mostrar una representacion util para depuracion
    # parametros: ninguno
    # retorno: cadena con el contenido del token
    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value!r})"

    # proposito: mostrar el token en el formato esperado por la practica
    # parametros: ninguno
    # retorno: cadena con tipo y valor del token
    def __str__(self) -> str:
        return f"[{self.type}] {self.value}"


class Lexer:
    KEYWORDS = {
        "auto",
        "break",
        "case",
        "char",
        "const",
        "continue",
        "default",
        "do",
        "double",
        "else",
        "enum",
        "extern",
        "float",
        "for",
        "goto",
        "if",
        "inline",
        "int",
        "long",
        "register",
        "restrict",
        "return",
        "short",
        "signed",
        "sizeof",
        "static",
        "struct",
        "switch",
        "typedef",
        "union",
        "unsigned",
        "void",
        "volatile",
        "while",
        "_Bool",
        "_Complex",
        "_Imaginary",
    }

    PUNCTUATORS = (
        "%:%:",
        "<<=",
        ">>=",
        "...",
        "##",
        "->",
        "++",
        "--",
        "<<",
        ">>",
        "<=",
        ">=",
        "==",
        "!=",
        "&&",
        "||",
        "*=",
        "/=",
        "%=",
        "+=",
        "-=",
        "&=",
        "^=",
        "|=",
        "<:",
        ":>",
        "<%",
        "%>",
        "%:",
        "[",
        "]",
        "(",
        ")",
        "{",
        "}",
        ".",
        "&",
        "*",
        "+",
        "-",
        "~",
        "!",
        "/",
        "%",
        "<",
        ">",
        "^",
        "|",
        "?",
        ":",
        ";",
        "=",
        ",",
        "#",
    )

    INTEGER_SUFFIX = r"(?:[uU](?:ll|LL|[lL])?|(?:ll|LL|[lL])(?:[uU])?)?"
    FLOAT_SUFFIX = r"[fFlL]?"
    UCN_FRAGMENT = r"(?:\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})"

    HEX_FLOAT_RE = re.compile(
        rf"0[xX](?:[0-9A-Fa-f]+\.[0-9A-Fa-f]*|\.[0-9A-Fa-f]+|[0-9A-Fa-f]+)"
        rf"[pP][+-]?[0-9]+{FLOAT_SUFFIX}"
    )
    DECIMAL_FLOAT_RE = re.compile(
        rf"(?:"
        rf"(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
        rf"|"
        rf"[0-9]+[eE][+-]?[0-9]+"
        rf"){FLOAT_SUFFIX}"
    )
    HEX_INT_RE = re.compile(rf"0[xX][0-9A-Fa-f]+{INTEGER_SUFFIX}")
    OCTAL_INT_RE = re.compile(rf"0[0-7]*{INTEGER_SUFFIX}")
    DECIMAL_INT_RE = re.compile(rf"(?:0|[1-9][0-9]*){INTEGER_SUFFIX}")

    # esta variable debe llamarse asi porque ply la usa para construir el lexer
    tokens = (
        "COMMENT",
        "STRING_LITERAL",
        "CHARACTER_CONSTANT",
        "NUMBER_LIKE",
        "IDENTIFIER",
        "PUNCTUATOR",
        "PP_OTHER",
    )

    # esta variable tambien sigue el nombre que espera ply
    t_ignore = " \t\r\v\f"

    # proposito: preparar el lexer con el codigo fuente que se va a analizar
    # parametros: sourceText -> texto completo del archivo c
    # retorno: instancia inicializada del lexer
    def __init__(self, sourceText: str):
        self.sourceText = sourceText
        self.lastMode = "token"
        self.savedTokens: list[Token] = []
        self.plyLexer = lex.lex(module=self, debug=False, optimize=False)

    # proposito: limpiar el cache interno de tokens antes de una nueva corrida
    # parametros: ninguno
    # retorno: ninguno
    def reset(self) -> None:
        self.savedTokens = []

    # proposito: validar si un lexema numerico coincide con las constantes que aceptamos como token normal
    # parametros: value -> texto numerico encontrado
    # retorno: true si la cadena coincide con alguna constante soportada
    def matchConstantText(self, value: str) -> bool:
        return any(
            pattern.fullmatch(value)
            for pattern in (
                self.HEX_FLOAT_RE,
                self.DECIMAL_FLOAT_RE,
                self.HEX_INT_RE,
                self.OCTAL_INT_RE,
                self.DECIMAL_INT_RE,
            )
        )

    # proposito: convertir el token crudo de ply al formato final usado por la practica
    # parametros: lexToken -> token generado por ply  preprocessing -> indica si trabajamos en modo de preprocesamiento
    # retorno: token convertido al formato final
    def convertLexToken(self, lexToken, preprocessing: bool) -> Token:
        line = lexToken.lineno
        value = lexToken.value
        tokenType = "PP_OTHER"

        if lexToken.type == "COMMENT":
            tokenType = "COMMENT"
        elif lexToken.type == "STRING_LITERAL":
            tokenType = "STRING_LITERAL"
        elif lexToken.type == "CHARACTER_CONSTANT":
            tokenType = "CHARACTER_CONSTANT" if preprocessing else "CONSTANT"
        elif lexToken.type == "NUMBER_LIKE":
            if preprocessing:
                tokenType = "PP_NUMBER"
            else:
                tokenType = "CONSTANT" if self.matchConstantText(value) else "PP_NUMBER"
        elif lexToken.type == "IDENTIFIER":
            if preprocessing:
                tokenType = "IDENTIFIER"
            else:
                tokenType = "KEYWORD" if value in self.KEYWORDS else "IDENTIFIER"
        elif lexToken.type == "PUNCTUATOR":
            tokenType = "PUNCTUATOR"

        return Token(tokenType, value, line)

    # proposito: unir tokens simples para reconocer header names en includes sencillos
    # parametros: tokenList -> lista de tokens del modo de preprocesamiento
    # retorno: lista de tokens con header names combinados
    def combineHeaderNames(self, tokenList: list[Token]) -> list[Token]:
        combinedTokens: list[Token] = []
        index = 0
        atLineStart = True
        directiveActive = False
        expectHeaderName = False
        previousLine = 1

        while index < len(tokenList):
            currentToken = tokenList[index]

            if currentToken.line > previousLine:
                atLineStart = True
                directiveActive = False
                expectHeaderName = False
            previousLine = currentToken.line

            tokenHandled = False
            nextIndex = index + 1

            if expectHeaderName and currentToken.type == "STRING_LITERAL":
                # nosotros aqui tratamos un include del tipo #include "archivo.h"
                combinedTokens.append(Token("HEADER_NAME", currentToken.value, currentToken.line))
                expectHeaderName = False
                atLineStart = False
                tokenHandled = True

            if (
                not tokenHandled
                and expectHeaderName
                and currentToken.type == "PUNCTUATOR"
                and currentToken.value == "<"
            ):
                # en esta parte armamos un header name del tipo <stdio.h> sin usar un preprocesador completo
                headerText = currentToken.value
                closingIndex = index + 1
                foundClosing = False

                while (
                    closingIndex < len(tokenList)
                    and tokenList[closingIndex].line == currentToken.line
                    and not foundClosing
                ):
                    nextToken = tokenList[closingIndex]
                    headerText += nextToken.value
                    if nextToken.type == "PUNCTUATOR" and nextToken.value == ">":
                        combinedTokens.append(Token("HEADER_NAME", headerText, currentToken.line))
                        expectHeaderName = False
                        atLineStart = False
                        nextIndex = closingIndex + 1
                        foundClosing = True
                        tokenHandled = True
                    closingIndex += 1

                if not foundClosing:
                    expectHeaderName = False

            if not tokenHandled:
                combinedTokens.append(currentToken)

                if directiveActive and currentToken.type == "IDENTIFIER" and currentToken.value == "include":
                    expectHeaderName = True
                elif expectHeaderName:
                    expectHeaderName = False

                if atLineStart and currentToken.type == "PUNCTUATOR" and currentToken.value in {"#", "%:"}:
                    directiveActive = True
                elif currentToken.type != "COMMENT":
                    atLineStart = False

            index = nextIndex

        return combinedTokens

    # proposito: ejecutar el lexer en modo normal o en modo de preprocesamiento
    # parametros: preprocessing -> indica el modo de trabajo
    # retorno: lista final de tokens incluyendo eof
    def tokenizeImpl(self, preprocessing: bool) -> list[Token]:
        self.reset()
        self.lastMode = "preprocessing" if preprocessing else "token"
        self.plyLexer.lineno = 1
        self.plyLexer.input(self.sourceText)

        tokenList: list[Token] = []
        currentLexToken = self.plyLexer.token()

        while currentLexToken is not None:
            tokenList.append(self.convertLexToken(currentLexToken, preprocessing))
            currentLexToken = self.plyLexer.token()

        if preprocessing:
            tokenList = self.combineHeaderNames(tokenList)

        eofLine = self.plyLexer.lineno
        tokenList.append(Token("EOF", "", eofLine))

        self.savedTokens = tokenList
        return self.savedTokens

    # proposito: obtener tokens del analisis lexico normal
    # parametros: ninguno
    # retorno: lista de tokens del codigo fuente
    def tokenize(self) -> list[Token]:
        return self.tokenizeImpl(preprocessing=False)

    # proposito: obtener tokens desde una vista mas cercana al preprocesamiento
    # parametros: ninguno
    # retorno: lista de preprocessing tokens
    def preprocessTokenize(self) -> list[Token]:
        return self.tokenizeImpl(preprocessing=True)

    # proposito: unir literales de cadena contiguos para reflejar mejor el comportamiento de c
    # parametros: tokenList -> lista de tokens ya generados
    # retorno: lista con literales adyacentes combinados
    def mergeAdjacentStringLiterals(self, tokenList: list[Token]) -> list[Token]:
        mergedTokens: list[Token] = []

        for currentToken in tokenList:
            shouldMerge = (
                len(mergedTokens) > 0
                and currentToken.type == "STRING_LITERAL"
                and mergedTokens[-1].type == "STRING_LITERAL"
            )

            if shouldMerge:
                mergedTokens[-1] = self.concatenateStringLiteralTokens(mergedTokens[-1], currentToken)
            else:
                mergedTokens.append(currentToken)

        return mergedTokens

    # proposito: concatenar dos tokens de cadena ya reconocidos
    # parametros: leftToken -> primer literal  rightToken -> segundo literal
    # retorno: nuevo token con ambos literales unidos
    def concatenateStringLiteralTokens(self, leftToken: Token, rightToken: Token) -> Token:
        leftIsWide = leftToken.value.startswith('L"')
        rightIsWide = rightToken.value.startswith('L"')
        prefix = "L" if leftIsWide or rightIsWide else ""
        leftContent = self.stringLiteralContent(leftToken.value)
        rightContent = self.stringLiteralContent(rightToken.value)
        combinedValue = f'{prefix}"{leftContent}{rightContent}"'
        return Token("STRING_LITERAL", combinedValue, leftToken.line)

    # proposito: quitar las comillas externas para trabajar solo con el contenido de un literal
    # parametros: literalText -> literal original de cadena
    # retorno: contenido interno del literal
    def stringLiteralContent(self, literalText: str) -> str:
        content = literalText

        if literalText.startswith('L"') and literalText.endswith('"'):
            content = literalText[2:-1]
        elif literalText.startswith('"') and literalText.endswith('"'):
            content = literalText[1:-1]

        return content

    # proposito: regresar los tokens del modo normal y permitir omitir comentarios
    # parametros: skipComments -> indica si se filtran comentarios
    # retorno: lista final de tokens del modo normal
    def getTokens(self, skipComments: bool = True) -> list[Token]:
        if self.lastMode != "token" or not self.savedTokens:
            self.tokenize()

        filteredTokens = [
            token
            for token in self.savedTokens
            if not (skipComments and token.type == "COMMENT")
        ]

        return self.mergeAdjacentStringLiterals(filteredTokens)

    # proposito: regresar los tokens del modo de preprocesamiento y permitir omitir comentarios
    # parametros: skipComments -> indica si se filtran comentarios
    # retorno: lista final de preprocessing tokens
    def getPreprocessingTokens(self, skipComments: bool = True) -> list[Token]:
        if self.lastMode != "preprocessing" or not self.savedTokens:
            self.preprocessTokenize()

        return [
            token
            for token in self.savedTokens
            if not (skipComments and token.type == "COMMENT")
        ]

    # proposito: reconocer comentarios de linea y de bloque
    # parametros: token -> token crudo de ply
    # retorno: token de comentario con linea actualizada
    @lex.TOKEN(r"//[^\n]*|/\*[\s\S]*?\*/")
    def t_COMMENT(self, token):
        token.lexer.lineno += token.value.count("\n")
        return token

    # proposito: reconocer literales de cadena simples y anchos
    # parametros: token -> token crudo de ply
    # retorno: token de cadena
    @lex.TOKEN(r'L?"([^\\\n]|(\\.))*?"')
    def t_STRING_LITERAL(self, token):
        return token

    # proposito: reconocer constantes de caracter simples y anchas
    # parametros: token -> token crudo de ply
    # retorno: token de caracter
    @lex.TOKEN(r"L?'([^\\\n]|(\\.))*?'")
    def t_CHARACTER_CONSTANT(self, token):
        return token

    # proposito: reconocer cadenas que pueden ser constantes o pp numbers segun el modo
    # parametros: token -> token crudo de ply
    # retorno: token numerico preliminar
    @lex.TOKEN(r"(?:\d|\.\d)(?:[eEpP][+-]|[A-Za-z0-9_]|\.)*")
    def t_NUMBER_LIKE(self, token):
        return token

    # proposito: reconocer identificadores y nombres con universal character names
    # parametros: token -> token crudo de ply
    # retorno: token identificador
    @lex.TOKEN(rf"(?:[A-Za-z_]|{UCN_FRAGMENT})(?:[A-Za-z0-9_]|{UCN_FRAGMENT})*")
    def t_IDENTIFIER(self, token):
        return token

    # proposito: reconocer operadores y signos de puntuacion del fragmento elegido
    # parametros: token -> token crudo de ply
    # retorno: token puntuador
    @lex.TOKEN("|".join(re.escape(punctuator) for punctuator in PUNCTUATORS))
    def t_PUNCTUATOR(self, token):
        return token

    # proposito: contar saltos de linea para conservar numeracion correcta
    # parametros: token -> token de salto de linea
    # retorno: ninguno porque solo actualiza estado interno
    @lex.TOKEN(r"\n+")
    def t_newline(self, token):
        token.lexer.lineno += len(token.value)

    # proposito: capturar caracteres no blancos que no encajan en otra categoria
    # parametros: token -> token crudo de ply
    # retorno: token pp_other
    @lex.TOKEN(r".")
    def t_PP_OTHER(self, token):
        return token

    # proposito: avanzar el lexer cuando aparece un caracter no reconocido
    # parametros: token -> token problematico
    # retorno: ninguno porque solo descarta un caracter
    def t_error(self, token):
        token.lexer.skip(1)


# proposito: leer un archivo y devolver sus tokens en modo normal o de preprocesamiento
# parametros: fileName -> ruta del archivo  preprocessing -> indica el modo de analisis
# retorno: lista de tokens o lista vacia si el archivo no existe
def analyzeFile(fileName: str, preprocessing: bool = False) -> list[Token]:
    try:
        with open(fileName, "r", encoding="utf-8") as sourceFile:
            sourceText = sourceFile.read()
    except FileNotFoundError:
        print(f"Error: archivo '{fileName}' no encontrado.")
        return []

    lexer = Lexer(sourceText)
    if preprocessing:
        return lexer.getPreprocessingTokens()
    return lexer.getTokens()


# proposito: imprimir una lista de tokens en el formato visible de la practica
# parametros: tokenList -> lista de tokens a mostrar
# retorno: ninguno
def printTokens(tokenList: list[Token]) -> None:
    for currentToken in tokenList:
        print(currentToken)


# proposito: mantener compatibilidad con el nombre anterior usado por el proyecto
# parametros: fileName -> ruta del archivo  preprocessing -> indica el modo de analisis
# retorno: lista de tokens generados por el lexer
def analyze_file(fileName: str, preprocessing: bool = False) -> list[Token]:
    return analyzeFile(fileName, preprocessing)


# proposito: mantener compatibilidad con el nombre anterior usado por el proyecto
# parametros: tokenList -> lista de tokens a mostrar
# retorno: ninguno
def print_tokens(tokenList: list[Token]) -> None:
    printTokens(tokenList)


if __name__ == "__main__":
    tokenList = analyzeFile(sys.argv[1])
    if not tokenList:
        raise SystemExit(1)
    printTokens(tokenList)
