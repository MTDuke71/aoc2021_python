"""Day 5: Hydrothermal Venture."""

import random
from collections import Counter

import pytest

import day05

LOCKED = (5167, 17604)

EXAMPLE = """\
0,9 -> 5,9
8,0 -> 0,8
9,4 -> 3,4
2,2 -> 2,1
7,0 -> 7,4
6,4 -> 2,0
0,9 -> 2,9
3,4 -> 1,4
0,0 -> 8,8
5,5 -> 8,2
"""

# The statement's picture of the horizontal and vertical lines only.
DIAGRAM_AXIS = """\
.......1..
..1....1..
..1....1..
.......1..
.112111211
..........
..........
..........
..........
222111....
"""

# ...and of every line.
DIAGRAM_ALL = """\
1.1....11.
.111...2..
..2.1.111.
...1.2.2..
.112313211
...1.2....
..1...1...
.1.....1..
1.......1.
222111....
"""


def render(segments, size=10):
    cover = Counter(p for s in segments for p in day05.points(s))
    return "".join(
        "".join(str(cover[x, y]) if cover[x, y] else "." for x in range(size)) + "\n" for y in range(size)
    )


def test_parse():
    segs = day05.parse_input(EXAMPLE)
    assert len(segs) == 10
    assert segs[0] == day05.Segment(0, 9, 5, 9)
    assert segs[5] == day05.Segment(6, 4, 2, 0)
    assert [s.axis_aligned for s in segs] == [True, False, True, True, True, False, True, True, False, False]


@pytest.mark.parametrize(
    "seg, expected",
    [
        ((1, 1, 1, 3), [(1, 1), (1, 2), (1, 3)]),  # statement's examples
        ((9, 7, 7, 7), [(9, 7), (8, 7), (7, 7)]),
        ((4, 4, 4, 4), [(4, 4)]),  # zero length: one point, not zero
        ((1, 1, 3, 3), [(1, 1), (2, 2), (3, 3)]),
        ((9, 7, 7, 9), [(9, 7), (8, 8), (7, 9)]),
    ],
)
def test_points(seg, expected):
    assert list(day05.points(day05.Segment(*seg))) == expected


def test_points_refuses_other_angles():
    with pytest.raises(ValueError, match="45"):
        list(day05.points(day05.Segment(0, 0, 2, 1)))


def test_unit_step_walk_is_exactly_the_lattice_points():
    """The walk steps (sign dx, sign dy) max(|dx|,|dy|) times.  For an
    axis-aligned or 45-degree segment that must be every integer point on
    the segment and nothing else: check against a brute-force collinearity
    and between-ness test over the bounding box."""
    rng = random.Random(5)
    for _ in range(300):
        x1, y1 = rng.randrange(12), rng.randrange(12)
        n = rng.randrange(8)
        dx, dy = rng.choice([(n, 0), (0, n), (n, n), (n, -n)])
        if rng.random() < 0.5:
            dx, dy = -dx, -dy
        seg = day05.Segment(x1, y1, x1 + dx, y1 + dy)
        walked = list(day05.points(seg))
        assert len(walked) == len(set(walked))
        lattice = {
            (x, y)
            for x in range(min(seg.x1, seg.x2), max(seg.x1, seg.x2) + 1)
            for y in range(min(seg.y1, seg.y2), max(seg.y1, seg.y2) + 1)
            if (x - seg.x1) * (seg.y2 - seg.y1) == (y - seg.y1) * (seg.x2 - seg.x1)
        }
        assert set(walked) == lattice
        assert walked[0] == (seg.x1, seg.y1) and walked[-1] == (seg.x2, seg.y2)


def test_example_axis_diagram():
    segs = [s for s in day05.parse_input(EXAMPLE) if s.axis_aligned]
    assert render(segs) == DIAGRAM_AXIS


def test_part1_example():
    assert day05.part1(day05.parse_input(EXAMPLE)) == 5


def test_example_full_diagram():
    assert render(day05.parse_input(EXAMPLE)) == DIAGRAM_ALL


def test_part2_example():
    assert day05.part2(day05.parse_input(EXAMPLE)) == 12


def test_part2_counts_diagonals():
    """The X from test_part1_ignores_diagonals: part 2 sees the crossing."""
    assert day05.part2(day05.parse_input("0,0 -> 2,2\n0,2 -> 2,0\n")) == 1


def test_diagonals_crossing_between_lattice_points_do_not_overlap():
    """0,0 -> 1,1 and 0,1 -> 1,0 cross at (0.5, 0.5), which is not a
    point of either walk.  Only integer points count."""
    assert day05.part2(day05.parse_input("0,0 -> 1,1\n0,1 -> 1,0\n")) == 0


def test_part2_refuses_other_angles():
    """The statement promises only 0/45/90 degrees; a line that breaks the
    promise is refused, not silently mis-walked."""
    with pytest.raises(ValueError, match="45"):
        day05.part2(day05.parse_input("0,0 -> 5,1\n"))


def test_part1_ignores_diagonals():
    """Two diagonals crossing at (1,1) would overlap, but part 1 skips them;
    a non-45 line is skipped too, not walked."""
    segs = day05.parse_input("0,0 -> 2,2\n0,2 -> 2,0\n0,0 -> 5,1\n")
    assert day05.part1(segs) == 0


def test_overlap_counts_points_not_pairs():
    """Three segments through one point is still one point."""
    segs = day05.parse_input("0,1 -> 2,1\n1,0 -> 1,2\n0,1 -> 1,1\n")
    assert day05.part1(segs) == 2  # (0,1) and (1,1)


def test_collinear_overlap():
    """Overlapping runs on the same row count every shared point."""
    segs = day05.parse_input("0,0 -> 5,0\n7,0 -> 3,0\n")
    assert day05.part1(segs) == 3  # x = 3, 4, 5


@pytest.mark.parametrize("raw", ["0,9 -> 5\n", "0,9 => 5,9\n", "a,9 -> 5,9\n", "0,9 -> 5,9 -> 1,1\n"])
def test_malformed_input_is_an_error(raw):
    with pytest.raises(ValueError, match="bad segment"):
        day05.parse_input(raw)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day05.parse_input(crlf) == day05.parse_input(EXAMPLE)
    assert day05.solve(crlf) == (5, 12)


def test_real_input_locked(check_locked):
    check_locked(day05, LOCKED)
