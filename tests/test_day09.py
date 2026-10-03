"""Day 9: Smoke Basin."""

import pytest

import day09

LOCKED = (423, 1198704)

EXAMPLE = """\
2199943210
3987894921
9856789892
8767896789
9899965678
"""


def test_parse_example():
    grid = day09.parse_input(EXAMPLE)
    assert len(grid) == 5
    assert grid[0] == [2, 1, 9, 9, 9, 4, 3, 2, 1, 0]
    assert grid[4] == [9, 8, 9, 9, 9, 6, 5, 6, 7, 8]


def test_parse_skips_blank_lines():
    assert day09.parse_input("\n12\n34\n\n") == [[1, 2], [3, 4]]


@pytest.mark.parametrize("bad", ["12\n3\n", "1a\n22\n", "1 2\n34\n", "-1\n22\n", "١٢\n34\n"])
def test_parse_malformed_is_an_error(bad):
    with pytest.raises(ValueError):
        day09.parse_input(bad)


def test_low_points_example():
    """The statement's four highlighted cells: 1 and 0 in row 0, 5 in row 2, 5 in row 4."""
    grid = day09.parse_input(EXAMPLE)
    assert day09.low_points(grid) == [(0, 1), (0, 9), (2, 2), (4, 6)]
    assert [grid[r][c] for r, c in day09.low_points(grid)] == [1, 0, 5, 5]


def test_part1_example():
    """Risk levels 2, 1, 6, 6."""
    assert day09.part1(day09.parse_input(EXAMPLE)) == 15


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("5\n", 6),  # single cell: no neighbours, vacuously low
        ("0\n", 1),
        ("12\n", 2),  # row: only the 1 is low
        ("1\n2\n", 2),  # column
        ("11\n11\n", 0),  # plateau: equal is not lower
        ("00\n", 0),
        ("101\n", 1),  # only the 0 is low; each 1 has a lower neighbour
        ("010\n", 2),  # both ends of a row can be low
        ("909\n010\n909\n", 4),  # the four 0s are low; the centre 1 is not
    ],
)
def test_part1_edges(raw, expected):
    assert day09.part1(day09.parse_input(raw)) == expected


def test_diagonals_do_not_count():
    """The centre 5 has diagonal neighbours of 0 but orthogonal neighbours of 9, so it is low."""
    grid = day09.parse_input("090\n959\n090\n")
    assert (1, 1) in day09.low_points(grid)


def test_corner_has_two_neighbours():
    assert sorted(day09.neighbours([[0] * 3 for _ in range(3)], 0, 0)) == [(0, 1), (1, 0)]
    assert len(list(day09.neighbours([[0] * 3 for _ in range(3)], 1, 1))) == 4


def test_basin_sizes_example():
    """Top-left 3, top-right 9, middle 14, bottom-right 9."""
    assert day09.basin_sizes(day09.parse_input(EXAMPLE)) == [3, 9, 14, 9]


def test_part2_example():
    assert day09.part2(day09.parse_input(EXAMPLE)) == 1134


def test_nines_belong_to_no_basin():
    """A 9 wall splits two basins; the 9s themselves are in neither."""
    assert day09.basin_sizes(day09.parse_input("01910\n")) == [2, 2]


def test_basin_does_not_leak_diagonally():
    """Cells touching only at a corner are different basins."""
    assert day09.basin_sizes(day09.parse_input("09\n90\n")) == [1, 1]


def test_part2_needs_three_basins():
    with pytest.raises(ValueError):
        day09.part2(day09.parse_input("191\n"))


def test_two_low_points_in_one_region_is_an_error():
    """The puzzle promises one low point per region; a grid that breaks it must raise, not miscount."""
    with pytest.raises(ValueError):
        day09.basin_sizes(day09.parse_input("0101\n"))


def test_part2_takes_the_three_largest_of_many():
    """Four basins of sizes 2, 3, 4, 5 on one row; the smallest is ignored."""
    grid = day09.parse_input("01" + "9" + "012" + "9" + "0123" + "9" + "01234" + "\n")
    assert day09.basin_sizes(grid) == [2, 3, 4, 5]
    assert day09.part2(grid) == 3 * 4 * 5


def test_real_input_one_low_point_per_region(real_input):
    """The shortcut part 2 leans on, checked directly: regions of non-9 cells
    are in one-to-one correspondence with low points, and together cover
    every non-9 cell."""
    grid = day09.parse_input(real_input(9))
    sizes = day09.basin_sizes(grid)  # raises if two low points share a region
    assert len(sizes) == len(day09.low_points(grid))
    assert sum(sizes) == sum(h != 9 for row in grid for h in row)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day09.parse_input(crlf) == day09.parse_input(EXAMPLE)
    assert day09.part1(day09.parse_input(crlf)) == 15


def test_real_input_locked(check_locked):
    check_locked(day09, LOCKED)
