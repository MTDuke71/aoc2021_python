"""Day 11: Dumbo Octopus."""

import pytest

import day11

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (1683, 788)

EXAMPLE = """\
5483143223
2745854711
5264556173
6141336146
6357385478
4167524645
2176841721
6882881134
4846848554
5283751526
"""

SMALL = """\
11111
19991
19191
19991
11111
"""

# The statement's snapshots of EXAMPLE, flash highlighting removed.
AFTER = {
    1: """\
6594254334
3856965822
6375667284
7252447257
7468496589
5278635756
3287952832
7993992245
5957959665
6394862637
""",
    2: """\
8807476555
5089087054
8597889608
8485769600
8700908800
6600088989
6800005943
0000007456
9000000876
8700006848
""",
    3: """\
0050900866
8500800575
9900000039
9700000041
9935080063
7712300000
7911250009
2211130000
0421125000
0021119000
""",
    10: """\
0481112976
0031112009
0041112504
0081111406
0099111306
0093511233
0442361130
5532252350
0532250600
0032240000
""",
    100: """\
0397666866
0749766918
0053976933
0004297822
0004229892
0053222877
0532222966
9322228966
7922286866
6789998766
""",
    193: "5877777777\n8877777777\n" + "7777777777\n" * 8,
    194: "6988888888\n9988888888\n" + "8888888888\n" * 8,
    195: "0000000000\n" * 10,
}


def run(raw, steps):
    """The grid after `steps` steps, and the flashes counted on the way."""
    grid = day11.parse_input(raw)
    return grid, sum(day11.step(grid) for _ in range(steps))


def test_parse_example_shape():
    grid = day11.parse_input(EXAMPLE)
    assert len(grid) == 10
    assert all(len(row) == 10 for row in grid)
    assert grid[0][0] == 5
    assert grid[9][9] == 6


def test_small_example():
    """The ring of 9s flashes and drags the 1 in the middle over with it."""
    grid = day11.parse_input(SMALL)
    assert day11.step(grid) == 9
    assert grid == day11.parse_input("34543\n40004\n50005\n40004\n34543\n")
    assert day11.step(grid) == 0
    assert grid == day11.parse_input("45654\n51115\n61116\n51115\n45654\n")


@pytest.mark.parametrize("steps", sorted(AFTER))
def test_example_snapshots(steps):
    grid, _ = run(EXAMPLE, steps)
    assert grid == day11.parse_input(AFTER[steps])


def test_example_step_1_has_no_flashes():
    assert run(EXAMPLE, 1)[1] == 0


def test_example_flashes_after_10_steps():
    assert run(EXAMPLE, 10)[1] == 204


def test_part1_example():
    assert day11.part1(day11.parse_input(EXAMPLE)) == 1656


def test_step_flash_count_matches_zeros():
    """Every flasher ends the step at 0 and nothing else can: a non-flasher gained at least 1."""
    grid = day11.parse_input(EXAMPLE)
    for _ in range(100):
        flashes = day11.step(grid)
        assert flashes == sum(row.count(0) for row in grid)


def test_octopus_flashes_once_per_step():
    """All nine go off together; the centre takes 8 more hits after flashing and is not recounted."""
    grid = day11.parse_input("999\n999\n999\n")
    assert day11.step(grid) == 9
    assert grid == [[0, 0, 0], [0, 0, 0], [0, 0, 0]]


def test_flashed_octopus_stays_at_zero():
    """The 8 is pushed over by the 9 after the 9 has flashed; the 9 must end at 0, not 1."""
    grid = day11.parse_input("98\n")
    assert day11.step(grid) == 2
    assert grid == [[0, 0]]


def test_diagonal_neighbours_count():
    grid = day11.parse_input("90\n08\n")
    assert day11.step(grid) == 2
    assert grid == [[0, 3], [3, 0]]


def test_corner_flash_stays_in_bounds():
    """A corner has three neighbours; nothing wraps to the far edge."""
    grid = day11.parse_input("900\n000\n000\n")
    assert day11.step(grid) == 1
    assert grid == [[0, 2, 1], [2, 2, 1], [1, 1, 1]]


def test_part1_does_not_mutate_parsed():
    parsed = day11.parse_input(EXAMPLE)
    day11.part1(parsed)
    assert parsed == day11.parse_input(EXAMPLE)
    assert day11.part1(parsed) == 1656


def test_part2_example():
    assert day11.part2(day11.parse_input(EXAMPLE)) == 195


def test_part2_is_the_first_full_flash():
    """No step before 195 flashes all 100; step 195 does."""
    grid = day11.parse_input(EXAMPLE)
    counts = [day11.step(grid) for _ in range(195)]
    assert counts[-1] == 100
    assert max(counts[:-1]) < 100


def test_synchronised_grid_flashes_every_10_steps():
    """All zeros is where a full flash leaves the grid: nine quiet steps, then everyone again."""
    grid = day11.parse_input(AFTER[195])
    assert day11.part2(grid) == 10
    assert [day11.step(grid) for _ in range(20)] == ([0] * 9 + [100]) * 2


def test_part2_can_answer_step_1():
    assert day11.part2(day11.parse_input("99\n99\n")) == 1


def test_part2_small_example():
    """The 5x5 ring: found by running it, not given in the statement; the cross-check is the count."""
    grid = day11.parse_input(SMALL)
    answer = day11.part2(grid)
    counts = [day11.step(grid) for _ in range(answer)]
    assert counts[-1] == 25
    assert 25 not in counts[:-1]


def test_part2_grid_that_never_synchronises_is_an_error():
    """'05' is back at '05' after 9 steps, each cell having flashed once, on different steps."""
    grid = day11.parse_input("05\n")
    assert 2 not in [day11.step(grid) for _ in range(100)]
    with pytest.raises(ValueError):
        day11.part2(day11.parse_input("05\n"))


def test_part2_empty_grid_is_an_error():
    with pytest.raises(ValueError):
        day11.part2(day11.parse_input(""))


def test_part2_does_not_mutate_parsed():
    parsed = day11.parse_input(EXAMPLE)
    day11.part2(parsed)
    assert parsed == day11.parse_input(EXAMPLE)


def test_parse_skips_blank_lines():
    assert day11.parse_input("\n12\n\n34\n\n") == [[1, 2], [3, 4]]


@pytest.mark.parametrize("bad", ["12\n3a\n", "1 2\n", "12\n345\n"])
def test_malformed_grid_is_an_error(bad):
    with pytest.raises(ValueError):
        day11.parse_input(bad)


def test_real_input_is_10_by_10(real_input):
    """'100 octopuses arranged neatly in a 10 by 10 grid.'"""
    grid = day11.parse_input(real_input(11))
    assert [len(row) for row in grid] == [10] * 10


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day11.parse_input(crlf) == day11.parse_input(EXAMPLE)
    assert day11.part1(day11.parse_input(crlf)) == 1656
    assert day11.part2(day11.parse_input(crlf)) == 195


def test_real_input_locked(check_locked):
    check_locked(day11, LOCKED)
