"""Day 1: Sonar Sweep."""

import random
from itertools import pairwise

import pytest

import day01

LOCKED = (1791, 1822)

EXAMPLE = "199\n200\n208\n210\n200\n207\n240\n269\n260\n263\n"
DEPTHS = [199, 200, 208, 210, 200, 207, 240, 269, 260, 263]


def window_sum_increases(depths):
    """Part 2 exactly as the statement words it: build every three-wide sum,
    then count the sums larger than the one before."""
    sums = [sum(depths[i : i + 3]) for i in range(len(depths) - 2)]
    return sum(b > a for a, b in pairwise(sums))


def test_parse_input():
    assert day01.parse_input(EXAMPLE) == DEPTHS


def test_part1_example():
    assert day01.part1(DEPTHS) == 7


def test_part2_example():
    assert day01.part2(DEPTHS) == 5


def test_example_window_sums():
    """The statement lists the eight sums A..H; check the reference helper
    against them so the identity test below is anchored to the statement."""
    sums = [sum(DEPTHS[i : i + 3]) for i in range(len(DEPTHS) - 2)]
    assert sums == [607, 618, 618, 617, 647, 716, 769, 792]
    assert window_sum_increases(DEPTHS) == 5


def test_gap3_matches_window_sums():
    """The shortcut part2 leans on: sum(d[i+1:i+4]) > sum(d[i:i+3]) exactly
    when d[i+3] > d[i], because d[i+1] and d[i+2] are in both sums.

    A narrow value range forces plenty of ties, which is where a sloppy
    comparison (>= for >) would show up.
    """
    rng = random.Random(2021)
    for length in range(40):
        depths = [rng.randint(0, 9) for _ in range(length)]
        assert day01.part2(depths) == window_sum_increases(depths)


@pytest.mark.parametrize(
    ("depths", "expected"),
    [
        ([], 0),
        ([5], 0),
        ([5, 5], 0),  # no change is not an increase
        ([5, 6], 1),
        ([6, 5], 0),
    ],
)
def test_part1_edges(depths, expected):
    assert day01.part1(depths) == expected


@pytest.mark.parametrize(
    ("depths", "expected"),
    [
        ([], 0),
        ([1, 2, 3], 0),  # one window, nothing to compare it with
        ([1, 2, 3, 4], 1),
        ([1, 9, 9, 1], 0),  # equal sums: 19 vs 19
        ([4, 2, 3, 1], 0),
    ],
)
def test_part2_edges(depths, expected):
    assert day01.part2(depths) == expected


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day01.parse_input(crlf) == DEPTHS
    assert day01.solve(crlf) == (7, 5)


def test_real_input_locked(check_locked):
    check_locked(day01, LOCKED)
