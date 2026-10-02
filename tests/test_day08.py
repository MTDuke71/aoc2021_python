"""Day 8: Seven Segment Search."""

import itertools
import random

import pytest

import day08

LOCKED = (274, 1012089)

# The statement wraps entries across two lines; in real input each is one line.
SMALL = "acedgfb cdfbe gcdfa fbcad dab cefabd cdfgeb eafb cagedb ab | cdfeb fcadb cdfeb cdbaf\n"

EXAMPLE = """\
be cfbegad cbdgef fgaecd cgeb fdcge agebfd fecdb fabcd edb | fdgacbe cefdb cefbgd gcbe
edbfga begcd cbg gc gcadebf fbgde acbgfd abcde gfcbed gfec | fcgedb cgb dgebacf gc
fgaebd cg bdaec gdafb agbcfd gdcbef bgcad gfac gcb cdgabef | cg cg fdcagb cbg
fbegcd cbd adcefb dageb afcb bc aefdc ecdab fgdeca fcdbega | efabcd cedba gadfec cb
aecbfdg fbg gf bafeg dbefa fcge gcbea fcaegb dgceab fcbdga | gecf egdcabf bgf bfgea
fgeab ca afcebg bdacfeg cfaedg gcfdb baec bfadeg bafgc acf | gebdcfa ecba ca fadegcb
dbcfg fgd bdegcaf fgec aegbdf ecdfab fbedc dacgb gdcebf gf | cefg dcbef fcge gbcadfe
bdfegc cbegaf gecbf dfcage bdacg ed bedf ced adcbefg gebcd | ed bcgafe cdgba cbgef
egadfb cdbfeg cegd fecab cgb gbdefca cg fgcdab egfdb bfceg | gbdfcae bgc cg cgb
gcafb gcf dcaebfg ecagb gf abcdeg gaef cafbge fdbac fegbdc | fgae cfgab fg bagce
"""


def test_parse_small():
    [(patterns, outputs)] = day08.parse_input(SMALL)
    assert len(patterns) == 10
    assert patterns[0] == frozenset("acedgfb")
    assert outputs == [frozenset("cdfeb"), frozenset("fcadb"), frozenset("cdfeb"), frozenset("cdbaf")]


def test_parse_ignores_wire_order_within_a_pattern():
    """`cdfeb` and `fcdeb` are the same lit set; they must parse equal."""
    [(_, a)] = day08.parse_input(SMALL)
    [(_, b)] = day08.parse_input(SMALL.replace("cdfeb fcadb", "bcdef bacdf"))
    assert a == b


def test_parse_example_shape():
    entries = day08.parse_input(EXAMPLE)
    assert len(entries) == 10
    assert all(len(p) == 10 and len(o) == 4 for p, o in entries)


@pytest.mark.parametrize(
    "bad",
    [
        "abc def\n",  # no delimiter
        SMALL.replace(" ab |", " |"),  # nine patterns
        SMALL.replace(" cdbaf", ""),  # three outputs
    ],
)
def test_parse_malformed_is_an_error(bad):
    with pytest.raises(ValueError):
        day08.parse_input(bad)


def test_parse_skips_blank_lines():
    assert len(day08.parse_input("\n" + EXAMPLE + "\n")) == 10


def test_part1_small_has_no_easy_outputs():
    """The statement's single entry: all four outputs are 5-segment digits."""
    assert day08.part1(day08.parse_input(SMALL)) == 0


def test_part1_example():
    assert day08.part1(day08.parse_input(EXAMPLE)) == 26


def test_part1_per_line_counts():
    """The statement's highlighted outputs, line by line."""
    counts = [day08.part1([entry]) for entry in day08.parse_input(EXAMPLE)]
    assert counts == [2, 3, 3, 1, 3, 4, 3, 1, 4, 2]


@pytest.mark.parametrize(
    "length, easy", [(1, False), (2, True), (3, True), (4, True), (5, False), (6, False), (7, True)]
)
def test_part1_unique_lengths(length, easy):
    """Only 2, 3, 4 and 7 lit segments identify a digit (1, 7, 4, 8)."""
    wires = "abcdefg"[:length]
    entry = (day08.parse_input(SMALL)[0][0], [frozenset(wires)] * 4)
    assert day08.part1([entry]) == (4 if easy else 0)


def test_part1_ignores_patterns_left_of_the_bar():
    """Only outputs count; the ten patterns always contain a 1, 4, 7 and 8."""
    [(patterns, _)] = day08.parse_input(SMALL)
    assert sum(len(s) in day08.UNIQUE_LENGTHS for s in patterns) == 4
    assert day08.part1(day08.parse_input(SMALL)) == 0


# Segments lit for each digit on a correct display.
SEGMENTS = ["abcefg", "cf", "acdeg", "acdfg", "bcdf", "abdfg", "abdefg", "acf", "abcdefg", "abcdfg"]


def scramble(digit_list, wiring):
    """Show digits through `wiring`, a segment -> wire map, as parsed signals."""
    return [frozenset(wiring[seg] for seg in SEGMENTS[d]) for d in digit_list]


def solve_by_permutation(patterns, outputs):
    """Reference solver: try all 5040 wirings, keep the one that explains the ten patterns."""
    wanted = set(patterns)
    for perm in itertools.permutations("abcdefg"):
        wiring = dict(zip("abcdefg", perm, strict=True))
        if set(scramble(range(10), wiring)) == wanted:
            lookup = {sig: d for d, sig in enumerate(scramble(range(10), wiring))}
            return int("".join(str(lookup[o]) for o in outputs))
    raise AssertionError("no wiring explains the patterns")


def test_part2_small_example():
    assert day08.decode_entry(day08.parse_input(SMALL)[0]) == 5353


def test_decode_patterns_small_example():
    """The statement's ten pattern -> digit list."""
    [(patterns, _)] = day08.parse_input(SMALL)
    decoded = {"".join(sorted(sig)): d for sig, d in day08.decode_patterns(patterns).items()}
    assert decoded == {
        "abcdefg": 8,
        "bcdef": 5,
        "acdfg": 2,
        "abcdf": 3,
        "abd": 7,
        "abcdef": 9,
        "bcdefg": 6,
        "abef": 4,
        "abcdeg": 0,
        "ab": 1,
    }


def test_part2_example_per_line():
    """The statement's ten decoded output values."""
    values = [day08.decode_entry(entry) for entry in day08.parse_input(EXAMPLE)]
    assert values == [8394, 9781, 1197, 9361, 4873, 8418, 4548, 1625, 8717, 4315]


def test_part2_example():
    assert day08.part2(day08.parse_input(EXAMPLE)) == 61229


def test_leading_zero_output_is_a_number():
    """An output of 0007 decodes to 7, not an error."""
    wiring = dict(zip("abcdefg", "abcdefg", strict=True))
    entry = (scramble(range(10), wiring), scramble([0, 0, 0, 7], wiring))
    assert day08.decode_entry(entry) == 7


def test_overlap_rule_decodes_every_wiring():
    """The standing claim: segment count plus overlap with 1 and 4 identifies
    every digit under any scramble.  All 5040 wirings, every digit."""
    for perm in itertools.permutations("abcdefg"):
        wiring = dict(zip("abcdefg", perm, strict=True))
        decoded = day08.decode_patterns(scramble(range(10), wiring))
        assert sorted(decoded.values()) == list(range(10))
        assert all(decoded[sig] == d for d, sig in enumerate(scramble(range(10), wiring)))


def test_overlap_rule_matches_brute_force_on_random_displays():
    """Same claim end to end, against a solver that does not use the rule:
    random wiring, shuffled patterns, random four-digit outputs."""
    rng = random.Random(8)
    for _ in range(25):
        perm = list("abcdefg")
        rng.shuffle(perm)
        wiring = dict(zip("abcdefg", perm, strict=True))
        patterns = scramble(range(10), wiring)
        rng.shuffle(patterns)
        outputs = scramble([rng.randrange(10) for _ in range(4)], wiring)
        assert day08.decode_entry((patterns, outputs)) == solve_by_permutation(patterns, outputs)


@pytest.mark.parametrize("digit", range(10))
def test_each_digit_has_a_distinct_overlap_signature(digit):
    """Why the rule works, as a table: (length, overlap with 1, overlap with 4)
    is unique per digit on an unscrambled display."""
    one, four = set(SEGMENTS[1]), set(SEGMENTS[4])

    def sig(d):
        return len(SEGMENTS[d]), len(one & set(SEGMENTS[d])), len(four & set(SEGMENTS[d]))

    assert [sig(d) for d in range(10)].count(sig(digit)) == 1


def test_decode_rejects_incomplete_pattern_set():
    [(patterns, _)] = day08.parse_input(SMALL)
    with pytest.raises(ValueError):
        day08.decode_patterns(patterns[:9] + [patterns[0]])


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day08.parse_input(crlf) == day08.parse_input(EXAMPLE)
    assert day08.part1(day08.parse_input(crlf)) == 26
    assert day08.solve(crlf) == (26, 61229)


def test_real_input_locked(check_locked):
    check_locked(day08, LOCKED)
