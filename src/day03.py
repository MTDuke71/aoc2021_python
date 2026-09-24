"""Day 3: Binary Diagnostic.

Input is one fixed-width binary number per line.
"""

from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day03.txt"


class Report(NamedTuple):
    """The diagnostic report: every number as an int, plus the bit width.

    The width has to be carried separately because it cannot be recovered
    from the ints: `00100` parses to 4, and nothing about 4 says it was five
    bits wide with two leading zeros.
    """

    width: int
    values: list[int]


def parse_input(raw: str) -> Report:
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not lines:
        raise ValueError("empty report")
    width = len(lines[0])
    for line in lines:
        # int(s, 2) alone is too forgiving: it accepts "1_0" as 2.
        if len(line) != width or set(line) - {"0", "1"}:
            raise ValueError(f"not a {width}-bit binary number: {line!r}")
    return Report(width, [int(line, 2) for line in lines])


def ones_in_column(values: list[int], bit: int) -> int:
    """How many values have a 1 at bit position `bit` (0 = least significant)."""
    return sum((v >> bit) & 1 for v in values)


def gamma_rate(report: Report) -> int:
    """Most common bit in each position, assembled into a number.

    A tied column has no most common bit and the statement does not say what
    to do, so it is an error rather than a guess.
    """
    n = len(report.values)
    gamma = 0
    for bit in range(report.width):
        ones = ones_in_column(report.values, bit)
        if 2 * ones == n:
            raise ValueError(f"bit {bit} is tied, {ones} ones of {n}")
        if 2 * ones > n:
            gamma |= 1 << bit
    return gamma


def part1(report: Report) -> int:
    gamma = gamma_rate(report)
    # With no ties, the least common bit is the complement of the most
    # common one in every position, so epsilon is gamma with all `width`
    # bits flipped.
    epsilon = gamma ^ ((1 << report.width) - 1)
    return gamma * epsilon


def filter_rating(report: Report, keep_majority: bool) -> int:
    """Part 2's search: filter on one bit at a time, leftmost first, until a
    single value is left.

    keep_majority=True is the oxygen generator rule (most common bit, 1 on a
    tie); False is the CO2 scrubber rule (least common bit, 0 on a tie).
    """
    candidates = report.values
    # "The first bit" is the leftmost character, which is the most
    # significant bit: position width - 1, counting down.
    for bit in reversed(range(report.width)):
        if len(candidates) == 1:
            break
        ones = ones_in_column(candidates, bit)
        zeros = len(candidates) - ones
        if keep_majority:
            wanted = 1 if ones >= zeros else 0
        else:
            wanted = 0 if zeros <= ones else 1
        candidates = [v for v in candidates if (v >> bit) & 1 == wanted]
    # Two ways to end without exactly one value: identical rows survive
    # every bit, or every survivor shares a bit and the CO2 rule asks for the
    # other one, keeping nothing.  The statement defines neither.
    if len(candidates) != 1:
        raise ValueError(f"filter ended with {len(candidates)} values, not 1")
    return candidates[0]


def part2(report: Report) -> int:
    oxygen = filter_rating(report, keep_majority=True)
    co2 = filter_rating(report, keep_majority=False)
    return oxygen * co2


def solve(raw: str) -> tuple[int, int]:
    report = parse_input(raw)
    return part1(report), part2(report)


def main() -> None:
    # Printed one part at a time so part 1's answer is on screen to submit
    # while part 2 is still raising NotImplementedError.
    report = parse_input(INPUT.read_text())
    print(f"part1={part1(report)}")
    print(f"part2={part2(report)}")


if __name__ == "__main__":
    raise SystemExit(main())
