"""Generalización léxica inspirada en el enfoque de Baker."""

from __future__ import annotations

import keyword
import tokenize

from models.match_models import LexToken


def generalize_token(token: LexToken) -> str:
    """Generaliza identificadores y literales, preservando estructura sintáctica.

    Esta abstracción sigue el espíritu de Baker porque reduce diferencias
    superficiales de renombrado o cambio de constantes, pero conserva keywords,
    operadores y signos estructurales para comparar la forma del programa.
    """

    if token.token_type == tokenize.NAME:
        return token.original_text if keyword.iskeyword(token.original_text) else "ID"
    if token.token_type == tokenize.NUMBER:
        return "NUM"
    if token.token_type == tokenize.STRING:
        return "STR"
    return token.original_text


def apply_generalization(tokens: list[LexToken]) -> list[LexToken]:
    """Actualiza cada token con su representación generalizada."""

    for token in tokens:
        token.generalized_text = generalize_token(token)
        token.comparable_text = token.original_text
    return tokens
