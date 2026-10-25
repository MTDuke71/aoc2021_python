"""Day 14: Extended Polymerization.

The input is a polymer template (a string of element letters), then rules
`AB -> C`: wherever A and B are adjacent, C is inserted between them.  Every
pair is rewritten at once, so a polymer of length n becomes 2n - 1 long each
step.

The polymer is never built.  Only counts are kept: how many times each
adjacent pair occurs.  Rule AB -> C turns every AB into an AC and a CB, and
which AB it was, or where it sat, makes no difference to what it becomes.
So a step is one pass over the pair counts, whatever the polymer's length.

Element counts come back out of the pair counts by counting each pair's
first letter.  That counts every element once except the last one, which is
the first letter of no pair.  Insertions only ever go between two elements,
so the last element is the template's last letter for good; it is added on
separately.

parse_input reads the template and rules, refuses a rule set that leaves any
pair of the letters in play without a rule (the statement does not say what
an unmatched pair does), and builds the starting pair counts.

Part 1 is the most common element's count minus the least common's after 10
steps.  Part 2 is the same after 40 steps, when the polymer would be about
2 * 10**13 letters long: the case pair counting is for.
"""

from collections import Counter
from functools import cache
from itertools import pairwise
from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day14.txt"

Pair = str
# Each pair maps to the two pairs it becomes: AB -> C gives AB: (AC, CB).
Rules = dict[Pair, tuple[Pair, Pair]]


class Polymer(NamedTuple):
    """The template's pair counts and last letter, plus the rewrite for every pair."""

    pairs: Counter[Pair]
    last: str
    rules: Rules


def parse_input(raw: str) -> Polymer:
    lines = [line.strip() for line in raw.splitlines()]
    lines = [line for line in lines if line]
    if not lines:
        raise ValueError("empty input")
    template, rule_lines = lines[0], lines[1:]
    if len(template) < 2 or not template.isalpha() or not template.isupper():
        raise ValueError(f"bad template: {template!r}")

    rules: Rules = {}
    for line in rule_lines:
        pair, sep, insert = line.partition(" -> ")
        chars = pair + insert
        if not (sep and len(pair) == 2 and len(insert) == 1 and chars.isalpha() and chars.isupper()):
            raise ValueError(f"not an AB -> C rule: {line!r}")
        if pair in rules:
            raise ValueError(f"two rules for {pair}: {line!r}")
        rules[pair] = (pair[0] + insert, insert + pair[1])

    letters = set(template) | {c for pair, (left, _) in rules.items() for c in pair + left}
    missing = sorted(a + b for a in letters for b in letters if a + b not in rules)
    if missing:
        raise ValueError(f"no rule for {len(missing)} pairs, e.g. {missing[:5]}")

    pairs = Counter(a + b for a, b in pairwise(template))
    return Polymer(pairs, template[-1], rules)


def step(pairs: Counter[Pair], rules: Rules) -> Counter[Pair]:
    """One round of insertions: every AB, all at once, becomes an AC and a CB."""
    nxt: Counter[Pair] = Counter()
    for pair, n in pairs.items():
        left, right = rules[pair]
        nxt[left] += n
        nxt[right] += n
    return nxt


def element_counts(pairs: Counter[Pair], last: str) -> Counter[str]:
    """Each pair's first letter, plus the polymer's last letter, which starts no pair."""
    counts: Counter[str] = Counter()
    for pair, n in pairs.items():
        counts[pair[0]] += n
    counts[last] += 1
    return counts


def spread(polymer: Polymer, steps: int) -> int:
    """Most common element's count minus the least common's after `steps` steps."""
    pairs = polymer.pairs
    for _ in range(steps):
        pairs = step(pairs, polymer.rules)
    counts = element_counts(pairs, polymer.last).values()
    return max(counts) - min(counts)


def spread_memo(polymer: Polymer, steps: int) -> int:
    """`spread` by memoised recursion, kept for comparison; part1 and part2 use `spread`.

    inside(AB, d) is the letters that d steps of insertion put between A and B.
    After one step AB is A C B, so inside(AB, d) is the C itself plus whatever
    grows inside AC and inside CB in the remaining d - 1 steps.  The total is the
    template's own letters plus inside() of each template pair.  The cache lives
    inside this call, so it is keyed on one rule set only.
    """

    @cache
    def inside(pair: Pair, depth: int) -> Counter[str]:
        if depth == 0:
            return Counter()
        left, right = polymer.rules[pair]
        return inside(left, depth - 1) + inside(right, depth - 1) + Counter(left[1])

    counts = element_counts(polymer.pairs, polymer.last)
    for pair, n in polymer.pairs.items():
        for letter, k in inside(pair, steps).items():
            counts[letter] += n * k
    values = counts.values()
    return max(values) - min(values)


def part1(parsed: Polymer) -> int:
    return spread(parsed, 10)


def part2(parsed: Polymer) -> int:
    return spread(parsed, 40)


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
