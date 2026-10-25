"""Day 13: Transparent Origami."""

import pytest

import day13

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (810, "HLBUBGFR")

EXAMPLE = """\
6,10
0,14
9,10
0,3
10,4
4,11
6,0
6,12
4,1
0,13
10,12
3,4
3,0
8,4
1,10
2,14
8,10
9,0

fold along y=7
fold along x=5
"""

UNFOLDED = """\
...#..#..#.
....#......
...........
#..........
...#....#.#
...........
...........
...........
...........
...........
.#....#.##.
....#......
......#...#
#..........
#.#........
"""

AFTER_Y7 = """\
#.##..#..#.
#...#......
......#...#
#...#......
.#.#..#.###
...........
...........
"""

AFTER_X5 = """\
#####
#...#
#...#
#...#
#####
.....
.....
"""


def picture_dots(picture):
    return frozenset((x, y) for y, row in enumerate(picture.split()) for x, ch in enumerate(row) if ch == "#")


def grid_fold(rows, axis, line):
    """The statement's fold done literally on a grid of booleans: flip the far half, OR it on.

    Independent of day13.fold's reflection arithmetic.  Assumes the far half is no
    longer than the kept half, as the statement's example (and the real input) is.
    """
    if axis == "x":
        rows = [list(r) for r in zip(*rows)]
    kept, far = rows[:line], rows[line + 1 :][::-1]
    offset = len(kept) - len(far)
    merged = [row[:] for row in kept]
    for k, row in enumerate(far):
        merged[offset + k] = [a or b for a, b in zip(merged[offset + k], row)]
    if axis == "x":
        merged = [list(r) for r in zip(*merged)]
    return merged


def grid_dots(rows):
    return frozenset((x, y) for y, row in enumerate(rows) for x, on in enumerate(row) if on)


def to_grid(dots, folds):
    """Size the sheet the way the fold lines imply: each first fold per axis is its midline."""
    first = {}
    for axis, line in folds:
        first.setdefault(axis, line)
    width = max(2 * first.get("x", 0) + 1, max(x for x, _ in dots) + 1)
    height = max(2 * first.get("y", 0) + 1, max(y for _, y in dots) + 1)
    rows = [[False] * width for _ in range(height)]
    for x, y in dots:
        rows[y][x] = True
    return rows


def test_parse_example():
    dots, folds = day13.parse_input(EXAMPLE)
    assert dots == picture_dots(UNFOLDED)
    assert len(dots) == 18
    assert folds == (("y", 7), ("x", 5))


def test_part1_example():
    assert day13.part1(day13.parse_input(EXAMPLE)) == 17


def test_folds_match_statement_pictures():
    dots, folds = day13.parse_input(EXAMPLE)
    once = day13.fold(dots, folds[0])
    assert once == picture_dots(AFTER_Y7)
    assert day13.fold(once, folds[1]) == picture_dots(AFTER_X5)


def test_example_makes_a_square():
    """The 5x5 square's border is 16 dots."""
    dots, folds = day13.parse_input(EXAMPLE)
    for f in folds:
        dots = day13.fold(dots, f)
    assert len(dots) == 16


@pytest.mark.parametrize("which", ["example", "real"])
def test_set_fold_matches_grid_fold(which, real_input):
    """Every fold, reflection on a set vs. flipping a literal grid, agrees step by step."""
    raw = EXAMPLE if which == "example" else real_input(13)
    dots, folds = day13.parse_input(raw)
    rows = to_grid(dots, folds)
    for axis, line in folds:
        dots = day13.fold(dots, (axis, line))
        rows = grid_fold(rows, axis, line)
        assert dots == grid_dots(rows)


def test_real_input_folds_are_well_formed(real_input):
    """No dot on a fold line and none folding past the edge, through every fold.

    fold() raises on either, so getting to the end is the check.
    """
    dots, folds = day13.parse_input(real_input(13))
    for f in folds:
        dots = day13.fold(dots, f)


def test_overlapping_dots_merge():
    """(0,0) and (0,2) folded along y=1 land on the same spot."""
    assert day13.fold(frozenset({(0, 0), (0, 2)}), ("y", 1)) == {(0, 0)}


def test_fold_left_reflects_x_only():
    assert day13.fold(frozenset({(7, 3), (1, 3)}), ("x", 5)) == {(3, 3), (1, 3)}


def test_dots_on_kept_side_do_not_move():
    dots = frozenset({(0, 0), (4, 6)})
    assert day13.fold(dots, ("y", 7)) == dots


@pytest.mark.parametrize("line", [1, 2, 7, 655])
def test_reflection_is_line_minus_distance(line):
    """The guide's branchless form: a folded coordinate is line - |c - line| for every c off the line."""
    for c in range(2 * line + 1):
        if c != line:
            ((x, _),) = day13.fold(frozenset({(c, 0)}), ("x", line))
            assert x == line - abs(c - line)


def test_dot_on_fold_line_is_an_error():
    with pytest.raises(ValueError):
        day13.fold(frozenset({(3, 7)}), ("y", 7))


def test_fold_past_the_edge_is_an_error():
    """Folding y=2 with a dot at y=5 would land it at y=-1."""
    with pytest.raises(ValueError):
        day13.fold(frozenset({(0, 5)}), ("y", 2))


def test_fold_far_edge_lands_on_zero():
    assert day13.fold(frozenset({(0, 4)}), ("y", 2)) == {(0, 0)}


def test_part1_without_folds_is_an_error():
    with pytest.raises(ValueError):
        day13.part1(day13.parse_input("1,2\n"))


@pytest.mark.parametrize(
    "bad",
    [
        "1,2\n\nfold along z=3\n",
        "1,2\n\nfold along y3\n",
        "1,2\n\nfold along y=\n",
        "1,2\n\nfold along y=-3\n",
        "1\n",
        "1,a\n",
        "-1,2\n",
        "1,2\n\nfold along y=3\n4,5\n",
    ],
)
def test_malformed_input_is_an_error(bad):
    with pytest.raises(ValueError):
        day13.parse_input(bad)


REAL_PICTURE = """\
#..#.#....###..#..#.###...##..####.###..
#..#.#....#..#.#..#.#..#.#..#.#....#..#.
####.#....###..#..#.###..#....###..#..#.
#..#.#....#..#.#..#.#..#.#.##.#....###..
#..#.#....#..#.#..#.#..#.#..#.#....#.#..
#..#.####.###...##..###...###.#....#..#.
"""


def test_example_render_matches_statement_including_blank_rows():
    """The example's last two rows are empty; sizing from the folds keeps them, as the statement shows."""
    parsed = day13.parse_input(EXAMPLE)
    assert day13.sheet_size(parsed) == (5, 7)
    assert day13.render(day13.fold_all(parsed), 5, 7) == AFTER_X5.split()


def test_real_picture(real_input):
    """The folded real input, as read by eye: HLBUBGFR."""
    parsed = day13.parse_input(real_input(13))
    assert day13.sheet_size(parsed) == (40, 6)
    assert day13.render(day13.fold_all(parsed), 40, 6) == REAL_PICTURE.split()


def test_read_real_picture():
    """Runs without the input: the glyph table decodes the pinned picture."""
    assert day13.read_letters(REAL_PICTURE.split()) == "HLBUBGFR"


def test_glyph_table_is_well_formed():
    assert len(set(day13.GLYPHS.values())) == len(day13.GLYPHS)
    for cell in day13.GLYPHS:
        assert len(cell) == day13.GLYPH_HEIGHT
        assert all(len(row) == day13.GLYPH_WIDTH and set(row) <= {"#", "."} for row in cell)


def test_glyph_table_round_trips():
    """Every known letter, laid out with blank separators, reads back in order."""
    cells = list(day13.GLYPHS)
    rows = ["".join(cell[r] + "." for cell in cells) for r in range(day13.GLYPH_HEIGHT)]
    assert day13.read_letters(rows) == "".join(day13.GLYPHS.values())


def test_unknown_letter_shows_the_picture():
    rows = REAL_PICTURE.split()
    rows[0] = "####" + rows[0][4:]  # H's top row filled in: no longer a known letter
    with pytest.raises(ValueError, match="unknown letter at x=0"):
        day13.read_letters(rows)


@pytest.mark.parametrize(
    "rows",
    [
        REAL_PICTURE.split()[:5],  # five rows, not six
        [row[:-1] for row in REAL_PICTURE.split()],  # 39 columns: not whole 5-wide cells
        [],
    ],
    ids=["short", "ragged-width", "empty"],
)
def test_not_a_letter_strip_is_an_error(rows):
    with pytest.raises(ValueError):
        day13.read_letters(rows)


def test_letters_must_be_separated_by_a_blank_column():
    rows = REAL_PICTURE.split()
    rows[2] = rows[2][:4] + "#" + rows[2][5:]
    with pytest.raises(ValueError, match="no blank column"):
        day13.read_letters(rows)


def test_sheet_size_without_folds_uses_the_dots():
    assert day13.sheet_size((frozenset({(2, 0), (0, 4)}), ())) == (3, 5)


def test_sheet_size_uses_last_fold_per_axis():
    assert day13.sheet_size((frozenset(), (("x", 9), ("y", 9), ("x", 4)))) == (4, 9)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day13.parse_input(crlf) == day13.parse_input(EXAMPLE)
    assert day13.part1(day13.parse_input(crlf)) == 17


def test_real_input_locked(check_locked):
    check_locked(day13, LOCKED)
