"""Day 3: Binary Diagnostic."""

import random
from collections import Counter

import pytest

import day03

LOCKED = (2648450, 2845944)

EXAMPLE_LINES = [
    "00100",
    "11110",
    "10110",
    "10111",
    "10101",
    "01111",
    "00111",
    "11100",
    "10000",
    "11001",
    "00010",
    "01010",
]
EXAMPLE = "\n".join(EXAMPLE_LINES) + "\n"


def rates_by_the_statement(lines):
    """Part 1 exactly as the statement words it, on the strings: the most
    common character in each column, then the least common, left to right.

    Both digits are counted explicitly, so a column where every row agrees
    has a least common bit that appears zero times."""
    gamma = epsilon = ""
    for column in zip(*lines):
        counts = Counter(column)
        most, least = ("1", "0") if counts["1"] > counts["0"] else ("0", "1")
        gamma += most
        epsilon += least
    return int(gamma, 2), int(epsilon, 2)


def rating_by_the_statement(lines, keep_majority):
    """Part 2 exactly as the statement words it, on the strings: walk the
    characters left to right, keep the lines matching the bit criteria, stop
    at one.  Returns (rating, survivors after each step), or None where the
    statement does not define an answer -- the filter kept nothing, or ran
    out of bits with more than one line left."""
    survivors = list(lines)
    steps = []
    for i in range(len(lines[0])):
        if len(survivors) == 1:
            break
        counts = Counter(line[i] for line in survivors)
        if counts["1"] == counts["0"]:
            keep = "1" if keep_majority else "0"
        elif keep_majority:
            keep = "1" if counts["1"] > counts["0"] else "0"
        else:
            keep = "1" if counts["1"] < counts["0"] else "0"
        survivors = [line for line in survivors if line[i] == keep]
        steps.append(survivors)
    if len(survivors) != 1:
        return None
    return int(survivors[0], 2), steps


def test_parse_input():
    report = day03.parse_input(EXAMPLE)
    assert report.width == 5
    assert report.values[:3] == [0b00100, 0b11110, 0b10110]
    assert len(report.values) == 12


def test_width_comes_from_the_text_not_the_values():
    """Every line starting with 0 must not shrink the width: 00100 is five
    bits, and its epsilon bit in the top position is 1."""
    report = day03.parse_input("00100\n00110\n00101\n")
    assert report.width == 5
    assert day03.gamma_rate(report) == 0b00100
    assert day03.part1(report) == 0b00100 * 0b11011


def test_example_rates():
    report = day03.parse_input(EXAMPLE)
    assert day03.gamma_rate(report) == 22
    assert rates_by_the_statement(EXAMPLE_LINES) == (22, 9)


def test_part1_example():
    assert day03.part1(day03.parse_input(EXAMPLE)) == 198


def test_epsilon_is_gamma_with_every_bit_flipped():
    """part1 never counts least-common bits; it takes gamma XOR all-ones.
    Check that against the literal string version on random reports.  An odd
    row count guarantees no tied column, the precondition for the identity."""
    rng = random.Random(2021)
    for _ in range(200):
        width = rng.randint(1, 12)
        rows = rng.randrange(1, 40, 2)
        lines = ["".join(rng.choice("01") for _ in range(width)) for _ in range(rows)]
        gamma, epsilon = rates_by_the_statement(lines)
        assert day03.part1(day03.parse_input("\n".join(lines))) == gamma * epsilon


def test_tied_column_is_an_error():
    """The statement never says which bit wins a tie, so part 1 refuses."""
    report = day03.parse_input("10\n01\n11\n00\n")
    with pytest.raises(ValueError, match="tied"):
        day03.part1(report)


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "101\n10\n",  # ragged width
        "1_0\n",  # int("1_0", 2) would say 2
        "+101\n",  # int("+101", 2) would say 5
        "102\n",
    ],
)
def test_malformed_input_is_an_error(raw):
    with pytest.raises(ValueError):
        day03.parse_input(raw)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day03.parse_input(crlf) == day03.parse_input(EXAMPLE)
    assert day03.solve(crlf) == (198, 230)


def test_part2_example_narration():
    """Anchor the reference to the survivor lists the statement narrates."""
    oxygen, oxygen_steps = rating_by_the_statement(EXAMPLE_LINES, keep_majority=True)
    assert oxygen == 23
    assert oxygen_steps == [
        ["11110", "10110", "10111", "10101", "11100", "10000", "11001"],
        ["10110", "10111", "10101", "10000"],
        ["10110", "10111", "10101"],
        ["10110", "10111"],
        ["10111"],
    ]
    co2, co2_steps = rating_by_the_statement(EXAMPLE_LINES, keep_majority=False)
    assert co2 == 10
    assert co2_steps == [
        ["00100", "01111", "00111", "00010", "01010"],
        ["01111", "01010"],
        ["01010"],
    ]


def test_part2_example():
    report = day03.parse_input(EXAMPLE)
    assert day03.filter_rating(report, keep_majority=True) == 23
    assert day03.filter_rating(report, keep_majority=False) == 10
    assert day03.part2(report) == 230


def test_filter_rating_matches_the_statement():
    """filter_rating works on ints, most significant bit first; the
    reference works on characters, left to right.  Check they agree on
    random reports, including the ones where the statement has no answer:
    there filter_rating must raise.  Narrow widths make duplicate rows and
    emptied lists common, so both failure paths get exercised."""
    rng = random.Random(2021)
    undefined = 0
    for _ in range(500):
        width = rng.randint(1, 6)
        rows = rng.randint(1, 20)
        lines = ["".join(rng.choice("01") for _ in range(width)) for _ in range(rows)]
        report = day03.parse_input("\n".join(lines))
        for keep_majority in (True, False):
            expected = rating_by_the_statement(lines, keep_majority)
            if expected is None:
                undefined += 1
                with pytest.raises(ValueError, match="ended with"):
                    day03.filter_rating(report, keep_majority)
            else:
                assert day03.filter_rating(report, keep_majority) == expected[0]
    assert undefined > 0  # the failure path really was exercised


def test_ratings_split_on_the_first_bit():
    """At the first bit the two rules always keep opposite groups -- oxygen
    keeps 1s exactly when ones >= zeros, CO2 keeps 0s exactly then -- so with
    two or more rows the two ratings differ in their top bit."""
    rng = random.Random(1202)
    for _ in range(200):
        width = rng.randint(2, 12)
        lines = list({"".join(rng.choice("01") for _ in range(width)) for _ in range(rng.randint(2, 30))})
        if len(lines) < 2:
            continue
        report = day03.parse_input("\n".join(lines))
        try:
            oxygen = day03.filter_rating(report, keep_majority=True)
            co2 = day03.filter_rating(report, keep_majority=False)
        except ValueError:
            continue
        top = 1 << (width - 1)
        assert (oxygen & top) != (co2 & top)


@pytest.mark.parametrize(
    ("raw", "keep_majority"),
    [
        ("101\n101\n", True),  # duplicates survive every bit
        ("110\n111\n", False),  # both share bit 2; least common is the absent 0
    ],
)
def test_filter_with_no_single_survivor_is_an_error(raw, keep_majority):
    with pytest.raises(ValueError, match="ended with"):
        day03.filter_rating(day03.parse_input(raw), keep_majority)


def test_real_input_locked(check_locked):
    check_locked(day03, LOCKED)
