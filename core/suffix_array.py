"""Implementación pura en Python de suffix array y LCP."""

from __future__ import annotations


def _compress_sequence(sequence: list[str]) -> list[int]:
    mapping: dict[str, int] = {}
    compressed: list[int] = []
    next_rank = 0
    for item in sequence:
        if item not in mapping:
            mapping[item] = next_rank
            next_rank += 1
        compressed.append(mapping[item])
    return compressed


def build_suffix_array(sequence: list[str]) -> list[int]:
    """Construye un suffix array mediante rank doubling.

    Es suficiente para los tamaños del proyecto y prioriza claridad.
    """

    if not sequence:
        return []

    values = _compress_sequence(sequence)
    n = len(values)
    suffix_array = list(range(n))
    rank = values[:]
    temp_rank = [0] * n
    step = 1

    while step < n:
        suffix_array.sort(
            key=lambda index: (
                rank[index],
                rank[index + step] if index + step < n else -1,
            )
        )
        temp_rank[suffix_array[0]] = 0
        for i in range(1, n):
            prev = suffix_array[i - 1]
            curr = suffix_array[i]
            prev_key = (rank[prev], rank[prev + step] if prev + step < n else -1)
            curr_key = (rank[curr], rank[curr + step] if curr + step < n else -1)
            temp_rank[curr] = temp_rank[prev] + (1 if curr_key != prev_key else 0)
        rank = temp_rank[:]
        if rank[suffix_array[-1]] == n - 1:
            break
        step *= 2

    return suffix_array


def build_lcp_array(sequence: list[str], suffix_array: list[int]) -> list[int]:
    """Kasai para LCP entre sufijos consecutivos del suffix array."""

    n = len(sequence)
    if n == 0:
        return []

    rank = [0] * n
    for index, suffix in enumerate(suffix_array):
        rank[suffix] = index

    lcp = [0] * max(n - 1, 0)
    match_length = 0
    for i in range(n):
        position = rank[i]
        if position == n - 1:
            match_length = 0
            continue
        j = suffix_array[position + 1]
        while (
            i + match_length < n
            and j + match_length < n
            and sequence[i + match_length] == sequence[j + match_length]
        ):
            match_length += 1
        lcp[position] = match_length
        if match_length > 0:
            match_length -= 1
    return lcp
