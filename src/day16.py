"""Day 16: Packet Decoder.

The input is one line of hex: a BITS transmission, a bit stream holding a
single outermost packet.  Every packet starts with a 3-bit version and a
3-bit type ID.  Type 4 is a literal: a number sent in 5-bit groups, each a
continue flag then 4 data bits.  Any other type is an operator holding
sub-packets, framed one of two ways by a length type bit: 0 means a 15-bit
count of sub-packet *bits* follows, 1 means an 11-bit count of *packets*.
The hex may pad the stream with a few 0 bits at the end.  Part 1 asks for
the sum of every packet's version.  Part 2 reads the tree as an expression:
operator types 0-3 are sum, product, min and max; 5-7 are greater than,
less than and equal (1 or 0, exactly two operands); evaluate the root.

parse_input turns the hex into a bit string (keeping leading zeros) and
decodes the whole tree with read_packet(), a recursive descent parser that
threads a bit position through the stream.  The tree is the parse result;
part1 walks it with version_sum(), part2 with evaluate().
"""

import math
from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day16.txt"

LITERAL = 4


class Packet(NamedTuple):
    version: int
    type_id: int
    value: int | None  # literals only
    children: tuple["Packet", ...]  # operators only


def hex_to_bits(hex_text: str) -> str:
    """Four bits per hex digit, MSB first, leading zeros kept.

    bin(int(...)) alone would drop leading zeros, and the real input starts
    with a 2 (0010), so the width is padded back to 4 * len.
    """
    return bin(int(hex_text, 16))[2:].zfill(4 * len(hex_text))


def take(bits: str, pos: int, n: int) -> tuple[int, int]:
    """Read an n-bit unsigned field at pos; returns (value, new pos)."""
    if pos + n > len(bits):
        raise ValueError(f"transmission ends inside a field: need bits {pos}..{pos + n}, have {len(bits)}")
    return int(bits[pos : pos + n], 2), pos + n


def read_packet(bits: str, pos: int = 0) -> tuple[Packet, int]:
    """Decode one packet starting at pos; returns (packet, position just past it)."""
    version, pos = take(bits, pos, 3)
    type_id, pos = take(bits, pos, 3)

    if type_id == LITERAL:
        value = 0
        more = 1
        while more:
            more, pos = take(bits, pos, 1)
            group, pos = take(bits, pos, 4)
            value = value << 4 | group
        return Packet(version, type_id, value, ()), pos

    length_type, pos = take(bits, pos, 1)
    children = []
    if length_type == 0:
        length, pos = take(bits, pos, 15)
        end = pos + length
        while pos < end:
            child, pos = read_packet(bits, pos)
            children.append(child)
        if pos != end:
            raise ValueError(f"sub-packets overrun their declared {length}-bit length")
    else:
        count, pos = take(bits, pos, 11)
        for _ in range(count):
            child, pos = read_packet(bits, pos)
            children.append(child)
    if not children:
        raise ValueError("operator packet with no sub-packets")
    return Packet(version, type_id, None, tuple(children)), pos


def parse_input(raw: str) -> Packet:
    """The outermost packet, fully decoded; anything after it must be 0 padding."""
    hex_text = raw.strip()
    if not hex_text or not all(ch in "0123456789abcdefABCDEF" for ch in hex_text):
        raise ValueError(f"transmission is not one line of hex: {raw[:40]!r}")
    bits = hex_to_bits(hex_text)
    packet, pos = read_packet(bits)
    if "1" in bits[pos:]:
        raise ValueError(f"non-zero bits after the outermost packet (from bit {pos})")
    return packet


def version_sum(packet: Packet) -> int:
    return packet.version + sum(version_sum(child) for child in packet.children)


def evaluate(packet: Packet) -> int:
    """The value of the expression rooted at packet, evaluated bottom-up.

    Comparisons yield 1 or 0 and must have exactly two operands.
    """
    if packet.type_id == LITERAL:
        return packet.value
    args = [evaluate(child) for child in packet.children]
    match packet.type_id:
        case 0:
            return sum(args)
        case 1:
            return math.prod(args)
        case 2:
            return min(args)
        case 3:
            return max(args)
    if len(args) != 2:
        raise ValueError(f"comparison packet (type {packet.type_id}) has {len(args)} operands, not 2")
    a, b = args
    match packet.type_id:
        case 5:
            return int(a > b)
        case 6:
            return int(a < b)
        case 7:
            return int(a == b)
    raise AssertionError("unreachable: type IDs are 3 bits")


def part1(parsed: Packet) -> int:
    return version_sum(parsed)


def part2(parsed: Packet) -> int:
    return evaluate(parsed)


def solve(raw: str) -> tuple[int, int]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    # Printed one part at a time so part 1's answer is on screen to submit
    # while part 2 is still raising NotImplementedError.
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
