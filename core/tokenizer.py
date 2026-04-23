"""Tokenización con el lexer estándar de Python."""

from __future__ import annotations

import token as token_module
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


def _build_line_offsets(text: str) -> list[int]:
    offsets = [0]
    for line in text.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    if not text.endswith(("\n", "\r")):
        offsets.append(len(text))
    return offsets


def _absolute_offset(line_offsets: list[int], line: int, col: int, text_length: int) -> int:
    if line <= 0:
        return 0
    index = min(line - 1, len(line_offsets) - 1)
    return min(line_offsets[index] + col, text_length)


def tokenize_source(text: str) -> TokenizationResult:
    """Tokeniza un texto fuente conservando posiciones absolutas."""

    warnings: list[str] = []
    tokens: list[LexToken] = []
    line_offsets = _build_line_offsets(text)
    stream = BytesIO(text.encode("utf-8")).readline
    generator = tokenize.tokenize(stream)

    try:
        for token_info in generator:
            if token_info.type in SKIP_TOKEN_TYPES:
                continue

            char_start = _absolute_offset(
                line_offsets,
                token_info.start[0],
                token_info.start[1],
                len(text),
            )
            char_end = _absolute_offset(
                line_offsets,
                token_info.end[0],
                token_info.end[1],
                len(text),
            )
            tokens.append(
                LexToken(
                    original_text=token_info.string,
                    token_name=token_module.tok_name.get(token_info.type, str(token_info.type)),
                    token_type=token_info.type,
                    start_line=token_info.start[0],
                    start_col=token_info.start[1],
                    end_line=token_info.end[0],
                    end_col=token_info.end[1],
                    char_start=char_start,
                    char_end=char_end,
                    comparable_text=token_info.string,
                    generalized_text=token_info.string,
                )
            )
    except tokenize.TokenError as exc:
        warnings.append(f"TokenError: {exc}")
        return TokenizationResult(tokens=tokens, warnings=warnings, error=str(exc))
    except IndentationError as exc:
        warnings.append(f"IndentationError: {exc}")
        return TokenizationResult(tokens=tokens, warnings=warnings, error=str(exc))
    except SyntaxError as exc:
        warnings.append(f"SyntaxError: {exc}")
        return TokenizationResult(tokens=tokens, warnings=warnings, error=str(exc))

    return TokenizationResult(tokens=tokens, warnings=warnings, error=None)
