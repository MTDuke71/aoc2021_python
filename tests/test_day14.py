"""Day 14: Extended Polymerization."""

from collections import Counter
from itertools import pairwise

import pytest

import day14

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (2745, 3420801168962)

EXAMPLE = """\
NNCB

CH -> B
HH -> N
CB -> H
NH -> C
HB -> C
HC -> B
HN -> C
NN -> C
BH -> H
NC -> B
NB -> B
BN -> B
BB -> N
BC -> B
CC -> N
CN -> C
"""

STEPS = [
    "NNCB",
    "NCNBCHB",
    "NBCCNBBBCBHCB",
    "NBBBCNCCNBBNBNBBCHBHHBCHB",
    "NBBNBNBBCCNBCNCCNBBNBBNBBBNBBNBBCBHCBHHNHCBBCBHCB",
]


def grow(raw, steps):
    """The statement done literally: build the whole string, step by step.

    Independent of day14's pair counting.  Returns the polymer after each step,
    starting with the template.
    """
    lines = raw.split("\n")
    polymer = lines[0].strip()
    rules = dict(line.strip().split(" -> ") for line in lines[1:] if line.strip())
    out = [polymer]
    for _ in range(steps):
        polymer = "".join(a + rules[a + b] for a, b in pairwise(polymer)) + polymer[-1]
        out.append(polymer)
    return out


def pair_counts(polymer):
    return Counter(a + b for a, b in pairwise(polymer))


def test_literal_grow_matches_statement():
    """The reference simulation reproduces the statement's strings, lengths and counts."""
    polymers = grow(EXAMPLE, 10)
    assert polymers[:5] == STEPS
    assert len(polymers[5]) == 97
    assert len(polymers[10]) == 3073
    assert Counter(polymers[10]) == {"B": 1749, "C": 298, "H": 161, "N": 865}


def test_parse_example():
    polymer = day14.parse_input(EXAMPLE)
    assert polymer.pairs == {"NN": 1, "NC": 1, "CB": 1}
    assert polymer.last == "B"
    assert len(polymer.rules) == 16
    assert polymer.rules["CH"] == ("CB", "BH")


def test_part1_example():
    assert day14.part1(day14.parse_input(EXAMPLE)) == 1588


@pytest.mark.parametrize("which", ["example", "real"])
def test_pair_counts_match_literal_string(which, real_input):
    """After each of 10 steps, the counted pairs are exactly the literal string's pairs."""
    raw = EXAMPLE if which == "example" else real_input(14)
    polymer = day14.parse_input(raw)
    pairs = polymer.pairs
    for literal in grow(raw, 10):
        assert pairs == pair_counts(literal)
        pairs = day14.step(pairs, polymer.rules)


@pytest.mark.parametrize("which", ["example", "real"])
def test_element_counts_match_literal_string(which, real_input):
    """First letter of every pair, plus the template's last letter, is the true letter count."""
    raw = EXAMPLE if which == "example" else real_input(14)
    last = day14.parse_input(raw).last
    for literal in grow(raw, 10):
        assert literal[-1] == last
        assert day14.element_counts(pair_counts(literal), last) == Counter(literal)


def test_part1_real_input_matches_literal_string(real_input):
    raw = real_input(14)
    counts = Counter(grow(raw, 10)[-1]).values()
    assert day14.part1(day14.parse_input(raw)) == max(counts) - min(counts)


def test_last_letter_comes_only_from_last():
    """Every rule inserts A: AB -> AAB -> AAAAB.  B starts no pair, so only `last` counts it."""
    polymer = day14.parse_input("AB\n\nAA -> A\nAB -> A\nBA -> A\nBB -> A\n")
    pairs = polymer.pairs
    for _ in range(2):
        pairs = day14.step(pairs, polymer.rules)
    assert pairs == {"AA": 3, "AB": 1}
    assert day14.element_counts(pairs, polymer.last) == {"A": 4, "B": 1}
    assert day14.spread(polymer, 0) == 0
    assert day14.spread(polymer, 2) == 4 - 1


def test_zero_steps_is_the_template():
    polymer = day14.parse_input(EXAMPLE)
    assert day14.element_counts(polymer.pairs, polymer.last) == Counter("NNCB")


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "N\n\nNN -> C\n",  # one letter: no pairs at all
        "nncb\n\nNN -> C\n",
        "NN\n\nNN - C\n",
        "NN\n\nNNN -> C\n",
        "NN\n\nNN -> CC\n",
        "NN\n\nNN -> c\n",
        "NN\n\nNN -> A\nNN -> A\nNA -> A\nAN -> A\nAA -> A\n",  # NN twice
        "NN\n\nNN -> C\n",  # C in play, but no rule for NC, CN, CC
    ],
)
def test_malformed_input_is_an_error(bad):
    with pytest.raises(ValueError):
        day14.parse_input(bad)


def test_part2_example():
    assert day14.part2(day14.parse_input(EXAMPLE)) == 2188189693529


def test_example_counts_after_40_steps():
    """The statement's most and least common elements after 40 steps."""
    polymer = day14.parse_input(EXAMPLE)
    pairs = polymer.pairs
    for _ in range(40):
        pairs = day14.step(pairs, polymer.rules)
    counts = day14.element_counts(pairs, polymer.last)
    assert counts.most_common()[0] == ("B", 2192039569602)
    assert counts.most_common()[-1] == ("H", 3849876073)


@pytest.mark.parametrize("which", ["example", "real"])
def test_length_doubles_less_one(which, real_input):
    """Each step turns n letters into 2n - 1, so after k steps there are (n - 1) * 2**k + 1."""
    raw = EXAMPLE if which == "example" else real_input(14)
    polymer = day14.parse_input(raw)
    n = sum(polymer.pairs.values()) + 1
    pairs = polymer.pairs
    for k in range(1, 41):
        pairs = day14.step(pairs, polymer.rules)
        assert sum(day14.element_counts(pairs, polymer.last).values()) == (n - 1) * 2**k + 1


@pytest.mark.parametrize("which", ["example", "real"])
def test_memo_recursion_matches_histogram(which, real_input):
    """The comparison version agrees with spread at every step count from 0 to 40."""
    raw = EXAMPLE if which == "example" else real_input(14)
    polymer = day14.parse_input(raw)
    for steps in range(41):
        assert day14.spread_memo(polymer, steps) == day14.spread(polymer, steps)


def test_real_input_rules_cover_every_pair(real_input):
    """10 letters, 100 rules: parse_input would raise on a gap, so parsing is the check."""
    polymer = day14.parse_input(real_input(14))
    assert len(polymer.rules) == 100


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day14.parse_input(crlf) == day14.parse_input(EXAMPLE)
    assert day14.part1(day14.parse_input(crlf)) == 1588


def test_real_input_locked(check_locked):
    check_locked(day14, LOCKED)
