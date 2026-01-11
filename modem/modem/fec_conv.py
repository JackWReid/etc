"""
Convolutional FEC encoder/decoder helpers for the CSS modem.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence

ConstraintLength = 7
Generators = (0o133, 0o171)
StateMask = (1 << (ConstraintLength - 1)) - 1


def _polynomial_output(state: int, bit: int) -> tuple[int, int]:
    """Return the two encoded bits for the input bit given current state."""
    new_state = ((state << 1) | (bit & 1)) & ((1 << ConstraintLength) - 1)
    outputs = []
    for generator in Generators:
        val = new_state & generator
        parity = 0
        while val:
            parity ^= val & 1
            val >>= 1
        outputs.append(parity)
    return (new_state & StateMask, outputs[0], outputs[1])


def conv_encode(bits: Iterable[int], *, terminate: bool = True) -> list[int]:
    """
    Encode a sequence of bits using the rate-1/2 K=7 convolutional code.
    """
    state = 0
    encoded: list[int] = []
    for bit in bits:
        state, out0, out1 = _polynomial_output(state, int(bit))
        encoded.extend((out0, out1))

    if terminate:
        for _ in range(ConstraintLength - 1):
            state, out0, out1 = _polynomial_output(state, 0)
            encoded.extend((out0, out1))

    return encoded


def _branch_metric(pair: tuple[int, int], expected0: int, expected1: int) -> int:
    return (pair[0] ^ expected0) + (pair[1] ^ expected1)


def _expected_pair(next_state: int, generator: int) -> int:
    val = next_state & generator
    parity = 0
    while val:
        parity ^= val & 1
        val >>= 1
    return parity


def viterbi_decode_hard(bits: Sequence[int], *, terminate: bool = True) -> list[int]:
    """
    Decode a hard-decision bit stream that was encoded with `conv_encode`.
    """
    if len(bits) % 2 != 0:
        raise ValueError("Convolutional decoder expects an even number of bits.")

    num_symbols = len(bits) // 2
    max_state = 1 << (ConstraintLength - 1)

    path_metrics = [float("inf")] * max_state
    path_metrics[0] = 0.0
    predecessors: list[list[int]] = [[0] * num_symbols for _ in range(max_state)]

    for idx in range(num_symbols):
        next_metrics = [float("inf")] * max_state
        symbol = (int(bits[2 * idx]), int(bits[2 * idx + 1]))
        for state in range(max_state):
            metric = path_metrics[state]
            if metric == float("inf"):
                continue
            for input_bit in (0, 1):
                next_full_state = ((state << 1) | input_bit) & ((1 << ConstraintLength) - 1)
                next_state = next_full_state & StateMask
                expected0 = _expected_pair(next_full_state, Generators[0])
                expected1 = _expected_pair(next_full_state, Generators[1])
                branch_cost = _branch_metric(symbol, expected0, expected1)
                total = metric + branch_cost
                if total < next_metrics[next_state]:
                    next_metrics[next_state] = total
                    predecessors[next_state][idx] = (state << 1) | input_bit
        path_metrics = next_metrics

    if terminate:
        final_state = 0
    else:
        final_state = min(range(max_state), key=lambda s: path_metrics[s])

    decoded_bits = [0] * num_symbols
    state = final_state
    for idx in reversed(range(num_symbols)):
        pred = predecessors[state][idx]
        decoded_bits[idx] = pred & 1
        state = pred >> 1

    if terminate and len(decoded_bits) >= ConstraintLength - 1:
        decoded_bits = decoded_bits[: -(ConstraintLength - 1)]

    return decoded_bits


