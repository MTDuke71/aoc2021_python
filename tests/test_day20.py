"""Day 20: Trench Map."""

import random

import pytest

import day20
from day20 import Image

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (4964, 13202)

EXAMPLE = """\
..#.#..#####.#.#.#.###.##.....###.##.#..###.####..#####..#....#..#..##..##
#..######.###...####..#..#####..##..#.#####...##.#.#..#.##..#.#......#.###
.######.###.####...#.##.##..#..#..#####.....#.#....###..#.##......#.....#.
.#..#..##..#...##.######.####.####.#.#...#.......#..#.#.#...####.##.#.....
.#..#...##.#.##..#...##.#.##..###.#......#.#.......#.#.#.####.###.##...#..
...####.#..#..#.##.#....##..#.####....##...##..#...#......#.#.......#.....
..##..####..#...#.#.#...##..#.#..###..#####........#..####......#..#

#..#.
#....
##..#
..#..
..###
"""

# The statement's 15x15 views; the input image's top-left pixel is at (5, 5).
STEP1 = """\
...............
...............
...............
...............
.....##.##.....
....#..#.#.....
....##.#..#....
....####..#....
.....#..##.....
......##..#....
.......#.#.....
...............
...............
...............
..............."""

STEP2 = """\
...............
...............
...............
..........#....
....#..#.#.....
...#.#...###...
...#...##.#....
...#.....#.#...
....#.#####....
.....#.#####...
......##.##....
.......###.....
...............
...............
..............."""


def pixel(image, steps, r, c):
    """Pixel at input-image coordinates (r, c); after `steps` enhancements the grid starts at (-steps, -steps)."""
    rr, cc = r + steps, c + steps
    if 0 <= rr < len(image.rows) and 0 <= cc < len(image.rows[0]):
        return image.rows[rr][cc]
    return image.background


def view(image, steps, top=-5, size=15):
    return "\n".join(
        "".join(".#"[pixel(image, steps, r, c)] for c in range(top, top + size))
        for r in range(top, top + size)
    )


def literal_lit(puzzle, steps):
    """Reference: simulate a window big enough that its edge effects never reach the middle.

    Every pixel is computed with nine dict lookups exactly as the statement words it.  The window is
    the image plus 3*steps of margin; pixels within `steps` of the window edge are wrong (they see
    missing neighbours as dark), creeping in one pixel per step.  The region within `steps` of the
    image -- every pixel that can differ from the background -- stays 2*steps clear of the edge, so it
    is exact.  Returns (lit inside that region, the background read from a sample pixel outside it).
    """
    alg, rows = puzzle.algorithm, puzzle.image.rows
    h, w = len(rows), len(rows[0])
    m = 3 * steps
    grid = {(r, c): 0 for r in range(-m, h + m) for c in range(-m, w + m)}
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            grid[r, c] = v
    for _ in range(steps):
        new = {}
        for r, c in grid:
            n = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    n = n << 1 | grid.get((r + dr, c + dc), 0)
            new[r, c] = alg[n]
        grid = new
    region = [(r, c) for r in range(-steps, h + steps) for c in range(-steps, w + steps)]
    return sum(grid[p] for p in region), grid[-m + steps, -m + steps]


def test_parse_example():
    puzzle = day20.parse_input(EXAMPLE)
    assert len(puzzle.algorithm) == 512
    assert puzzle.algorithm[:10] == (0, 0, 1, 0, 1, 0, 0, 1, 1, 1)
    assert puzzle.image == Image(
        ((1, 0, 0, 1, 0), (1, 0, 0, 0, 0), (1, 1, 0, 0, 1), (0, 0, 1, 0, 0), (0, 0, 1, 1, 1))
    )


def test_statement_index_34():
    """The centre pixel's window reads ...#...#. = 0b000100010 = 34, and algorithm[34] is '#'."""
    puzzle = day20.parse_input(EXAMPLE)
    rows = puzzle.image.rows
    n = 0
    for r in (1, 2, 3):
        for c in (1, 2, 3):
            n = n << 1 | rows[r][c]
    assert n == 34
    assert puzzle.algorithm[34] == 1
    assert (
        day20.enhance(puzzle.image, puzzle.algorithm).rows[3][3] == 1
    )  # (2,2) shifted by the 1-pixel growth


def test_triples():
    assert day20.triples([0, 1, 1, 0, 1]) == [0b011, 0b110, 0b101]


@pytest.mark.parametrize(("steps", "picture"), [(1, STEP1), (2, STEP2)])
def test_statement_pictures(steps, picture):
    puzzle = day20.parse_input(EXAMPLE)
    assert view(day20.enhance_n(puzzle.image, puzzle.algorithm, steps), steps) == picture


def test_part1_example():
    assert day20.part1(day20.parse_input(EXAMPLE)) == 35


def test_part2_example():
    assert day20.part2(day20.parse_input(EXAMPLE)) == 3351


def test_grid_grows_one_per_side():
    puzzle = day20.parse_input(EXAMPLE)
    image = day20.enhance_n(puzzle.image, puzzle.algorithm, 3)
    assert (len(image.rows), len(image.rows[0])) == (11, 11)


def flipping(seed):
    """Random puzzle whose algorithm has [0] = '#' and [511] = '.', like the real input."""
    rng = random.Random(seed)
    alg = [rng.randint(0, 1) for _ in range(512)]
    alg[0], alg[511] = 1, 0
    h, w = rng.randint(1, 8), rng.randint(1, 8)
    rows = tuple(tuple(rng.randint(0, 1) for _ in range(w)) for _ in range(h))
    return day20.Puzzle(tuple(alg), Image(rows))


def test_real_input_background_flips(real_input):
    """The real algorithm lights the all-dark window: the outside is lit after odd steps, dark after even."""
    puzzle = day20.parse_input(real_input(20))
    assert (puzzle.algorithm[0], puzzle.algorithm[511]) == (1, 0)
    image = puzzle.image
    for step in range(1, 5):
        image = day20.enhance(image, puzzle.algorithm)
        assert image.background == step % 2


def test_lit_refuses_lit_background():
    with pytest.raises(ValueError):
        day20.lit(Image(((0,),), background=1))


@pytest.mark.parametrize("seed", range(20))
@pytest.mark.parametrize("steps", [1, 2, 3, 4])
def test_matches_literal_reference(seed, steps):
    """Row codes, padding and background tracking agree with nine-lookup simulation, flipping background included."""
    puzzle = flipping(seed) if seed % 2 else day20.parse_input(EXAMPLE)._replace(image=flipping(seed).image)
    image = day20.enhance_n(puzzle.image, puzzle.algorithm, steps)
    assert (sum(map(sum, image.rows)), image.background) == literal_lit(puzzle, steps)


def test_part1_matches_literal_reference_real(real_input):
    puzzle = day20.parse_input(real_input(20))
    assert literal_lit(puzzle, 2) == (day20.part1(puzzle), 0)


def test_matches_literal_reference_real_more_steps(real_input):
    """Ten steps on the real image (the literal reference is too slow for 50)."""
    puzzle = day20.parse_input(real_input(20))
    image = day20.enhance_n(puzzle.image, puzzle.algorithm, 10)
    assert (sum(map(sum, image.rows)), image.background) == literal_lit(puzzle, 10)


@pytest.mark.parametrize(
    "bad",
    [
        "",
        EXAMPLE.replace("\n\n", "\n"),  # no blank line
        EXAMPLE.replace("..#.#..", "..#.#.", 1),  # 511 entries
        EXAMPLE.replace("#..#.\n", "#..#\n"),  # ragged image
        EXAMPLE.replace("#..#.\n", "#..x.\n"),  # bad character
        EXAMPLE.split("\n\n")[0] + "\n\n",  # no image
    ],
)
def test_malformed_input_is_an_error(bad):
    with pytest.raises(ValueError):
        day20.parse_input(bad)


def test_permanently_lit_background_is_an_error():
    """[0] = '#' and [511] = '#': the outside lights on step 1 and never goes dark, so no count is finite."""
    lines = EXAMPLE.split("\n")
    lines[0] = "#" + lines[0][1:]
    lines[6] = lines[6][:-1] + "#"
    assert len("".join(lines[:7])) == 512
    with pytest.raises(ValueError, match="both"):
        day20.parse_input("\n".join(lines))


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day20.parse_input(crlf) == day20.parse_input(EXAMPLE)
    assert day20.part1(day20.parse_input(crlf)) == 35


def test_real_input_locked(check_locked):
    check_locked(day20, LOCKED)
