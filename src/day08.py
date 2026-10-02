"""Day 8: Seven Segment Search.

Each input line is one display: ten scrambled signal patterns, a `|`, and
four scrambled output digits.  A pattern is a *set* of wires (order within
it means nothing), so parse_input stores each as a frozenset of letters.

Part 1 needs no decoding.  Digits 1, 4, 7 and 8 are the only ones lit with
2, 3, 4 and 7 segments, and the wire/segment scramble preserves how many
wires are on, so an output pattern of that length is one of those digits.
Part 1 counts them.

Part 2 decodes every digit without ever recovering the wire/segment map.
Length gives 1, 7, 4, 8.  The rest are told apart by how many wires they
share with the known 1 and 4:

    len 5:  3 contains all of 1; 5 shares 3 wires with 4; 2 shares only 2
    len 6:  9 contains all of 4; 0 contains all of 1; 6 is neither

Overlap sizes survive the scramble because they are set intersections, and
a relabelling of wires cannot change the size of an intersection.  The tests
pin the rule against a brute-force solver over every wire permutation.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day08.txt"

# Segment counts that identify a digit uniquely: 1, 7, 4, 8.
UNIQUE_LENGTHS = frozenset({2, 3, 4, 7})

Signal = frozenset[str]
Entry = tuple[list[Signal], list[Signal]]


def parse_input(raw: str) -> list[Entry]:
    """One (ten patterns, four outputs) pair per line, each pattern a frozenset of wires."""
    entries = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        left, bar, right = line.partition("|")
        patterns = [frozenset(word) for word in left.split()]
        outputs = [frozenset(word) for word in right.split()]
        if not bar or len(patterns) != 10 or len(outputs) != 4:
            raise ValueError(f"malformed entry: {line!r}")
        entries.append((patterns, outputs))
    return entries


def part1(entries: list[Entry]) -> int:
    return sum(len(signal) in UNIQUE_LENGTHS for _, outputs in entries for signal in outputs)


def decode_patterns(patterns: list[Signal]) -> dict[Signal, int]:
    """Map each of the ten scrambled patterns to the digit it displays."""
    by_length = {}
    for signal in patterns:
        by_length.setdefault(len(signal), []).append(signal)
    if any(len(by_length.get(n, ())) != 1 for n in (2, 3, 4, 7)):
        raise ValueError("patterns are not a full set of ten distinct digits")
    one, seven, four, eight = (by_length[n][0] for n in (2, 3, 4, 7))

    digits = {one: 1, seven: 7, four: 4, eight: 8}
    for signal in by_length[5]:
        if one <= signal:
            digits[signal] = 3
        elif len(signal & four) == 3:
            digits[signal] = 5
        else:
            digits[signal] = 2
    for signal in by_length[6]:
        if four <= signal:
            digits[signal] = 9
        elif one <= signal:
            digits[signal] = 0
        else:
            digits[signal] = 6
    if len(digits) != 10:
        raise ValueError("patterns are not a full set of ten distinct digits")
    return digits


def decode_entry(entry: Entry) -> int:
    """The four-digit output value of one display."""
    patterns, outputs = entry
    digits = decode_patterns(patterns)
    value = 0
    for signal in outputs:
        value = value * 10 + digits[signal]
    return value


def part2(entries: list[Entry]) -> int:
    return sum(decode_entry(entry) for entry in entries)


def solve(raw: str) -> tuple[int, int]:
    entries = parse_input(raw)
    return part1(entries), part2(entries)


def main() -> None:
    # Printed one part at a time so part 1's answer is on screen to submit
    # while part 2 is still raising NotImplementedError.
    entries = parse_input(INPUT.read_text())
    print(f"part1={part1(entries)}")
    print(f"part2={part2(entries)}")


if __name__ == "__main__":
    raise SystemExit(main())
