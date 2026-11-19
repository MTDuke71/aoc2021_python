"""Day 25: Sea Cucumber."""

import pytest

import day25

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (360, 0)

EXAMPLE = """\
v...>>.vv>
.vv>>.vv..
>>.>v>...v
>>v>>.>.v.
v>v.vv.v..
>.>>..v...
.vv..>.>v.
v.v..>>v.v
....v..v.>
"""

# Snapshots of EXAMPLE from the statement, keyed by step count.
EXAMPLE_AFTER = {
    1: """\
....>.>v.>
v.v>.>v.v.
>v>>..>v..
>>v>v>.>.v
.>v.v...v.
v>>.>vvv..
..v...>>..
vv...>>vv.
>.v.v..v.v""",
    2: """\
>.v.v>>..v
v.v.>>vv..
>v>.>.>.v.
>>v>v.>v>.
.>..v....v
.>v>>.v.v.
v....v>v>.
.vv..>>v..
v>.....vv.""",
    5: """\
vv>...>v>.
v.v.v>.>v.
>.v.>.>.>v
>v>.>..v>>
..v>v.v...
..>.>>vvv.
.>...v>v..
..v.v>>v.v
v.v.>...v.""",
    10: """\
..>..>>vv.
v.....>>.v
..v.v>>>v>
v>.>v.>>>.
..v>v.vv.v
.v.>>>.v..
v.v..>v>..
..v...>v.>
.vv..v>vv.""",
    40: """\
>>v>v..v..
..>>v..vv.
..>>>v.>.v
..>>>>vvv>
v.....>...
v.v...>v>>
>vv.....v>
.>v...v.>v
vvv.v..v.>""",
    58: """\
..>>v>vv..
..v.>>vv..
..>>v>>vv.
..>>>>>vv.
v......>vv
v>v....>>v
vvv.....>>
>vv......>
.>v.vv.v..""",
}

WRAP = """\
...>...
.......
......>
v.....>
......>
.......
..vvv..
"""

WRAP_AFTER = [
    """\
..vv>..
.......
>......
v.....>
>......
.......
....v..""",
    """\
....v>.
..vv...
.>.....
......>
v>.....
.......
.......""",
    """\
......>
..v.v..
..>v...
>......
..>....
v......
.......""",
    """\
>......
..v....
..>.v..
.>.v...
...>...
.......
v......""",
]


def run(text: str, steps: int) -> str:
    floor = day25.parse_input(text)
    for _ in range(steps):
        floor = day25.step(floor)
    return day25.render(floor)


# --- statement examples ------------------------------------------------------


@pytest.mark.parametrize(
    ("steps", "expected"),
    [(1, "...>>>>.>.."), (2, "...>>>.>.>.")],
)
def test_single_row(steps, expected):
    """Only the front of a queue moves; the gap then walks back one per step."""
    assert run("...>>>>>...\n", steps) == expected


def test_east_moves_before_south():
    """Left pair: `>` is blocked by a `v` that only leaves afterwards.
    Right pair: `>` leaves first, so the `v` above it can drop in."""
    start = "..........\n.>v....v..\n.......>..\n..........\n"
    want = "..........\n.>........\n..v....v>.\n.........."
    assert run(start, 1) == want


@pytest.mark.parametrize("steps", range(1, 5))
def test_wraparound_example(steps):
    assert run(WRAP, steps) == WRAP_AFTER[steps - 1]


@pytest.mark.parametrize("steps", sorted(EXAMPLE_AFTER))
def test_example_snapshots(steps):
    assert run(EXAMPLE, steps) == EXAMPLE_AFTER[steps]


def test_example_steps_57_and_58_are_identical():
    assert run(EXAMPLE, 57) == run(EXAMPLE, 58)
    assert run(EXAMPLE, 56) != run(EXAMPLE, 57)


def test_part1_example():
    assert day25.part1(day25.parse_input(EXAMPLE)) == 58


def test_part2_is_the_free_star():
    assert day25.part2(day25.parse_input(EXAMPLE)) == 0


# --- edge cases --------------------------------------------------------------


def test_full_row_never_moves():
    """No gap anywhere ahead: every cucumber is blocked, so step 1 is still."""
    assert day25.part1(day25.parse_input(">>>>\n")) == 1


def test_lone_cucumber_on_a_ring_never_stops_moving():
    """The puzzle promises a jam; a lone cucumber on a 1x3 ring never jams.
    Not something part1 can detect, so just show the cycle: back home after 3."""
    floor = day25.parse_input(">..\n")
    assert day25.step(day25.step(day25.step(floor))) == floor
    assert day25.step(floor) != floor


def test_one_wide_column_cucumber_blocks_itself():
    """A 1-wide map: an east cucumber's cell ahead is its own cell (c+1 mod 1),
    which is occupied, so it never moves."""
    floor = day25.parse_input(">\n.\n")
    assert day25.step(floor) == floor


def naive_in_place_east(row: str, left_to_right: bool) -> str:
    """The wrong way: edit the row while scanning it (guide section 2)."""
    g, w = list(row), len(row)
    for c in range(w) if left_to_right else range(w - 1, -1, -1):
        if g[c] == ">" and g[(c + 1) % w] == ".":
            g[c], g[(c + 1) % w] = ".", ">"
    return "".join(g)


@pytest.mark.parametrize(
    ("row", "correct", "l2r", "r2l"),
    [(".>.", "..>", ">..", "..>"), (">>.", ">.>", ">.>", ".>>")],
)
def test_in_place_scan_is_wrong_both_ways(row, correct, l2r, r2l):
    """Pins the guide's table: an in-place scan fails in either direction,
    and `step` (which reads the old set) gets both right."""
    assert day25.render(day25.step(day25.parse_input(row))) == correct
    assert naive_in_place_east(row, left_to_right=True) == l2r
    assert naive_in_place_east(row, left_to_right=False) == r2l


def test_render_round_trips_parse():
    assert day25.render(day25.parse_input(EXAMPLE)) == EXAMPLE.rstrip("\n")


@pytest.mark.parametrize("bad", ["", "..\n.\n", ".x.\n"])
def test_parse_rejects_bad_maps(bad):
    with pytest.raises(ValueError):
        day25.parse_input(bad)


def test_crlf_input():
    assert day25.parse_input(EXAMPLE.replace("\n", "\r\n")) == day25.parse_input(EXAMPLE)


# --- pinned identities -------------------------------------------------------


def literal_step(grid: list[list[str]]) -> tuple[list[list[str]], int]:
    """The statement read literally on a char grid: scan, then copy-and-move.
    Returns the new grid and how many cucumbers moved."""
    h, w = len(grid), len(grid[0])
    moved = 0
    for herd, dr, dc in ((">", 0, 1), ("v", 1, 0)):
        movers = [
            (r, c)
            for r in range(h)
            for c in range(w)
            if grid[r][c] == herd and grid[(r + dr) % h][(c + dc) % w] == "."
        ]
        grid = [row[:] for row in grid]
        for r, c in movers:
            grid[r][c] = "."
            grid[(r + dr) % h][(c + dc) % w] = herd
        moved += len(movers)
    return grid, moved


def literal_part1(text: str) -> int:
    grid = [list(line.strip()) for line in text.splitlines() if line.strip()]
    steps = 0
    while True:
        steps += 1
        grid, moved = literal_step(grid)
        if moved == 0:
            return steps


def test_unchanged_state_means_nobody_moved(real_input):
    """part1 stops on `step(floor) == floor`, not on a move count.  That is
    sound because a cucumber that moves lands on a cell its herd did not hold
    before, so any move changes the set.  Pinned by checking, every step of
    the real run, that the literal simulator's move count is zero exactly when
    the set-based state is unchanged."""
    text = real_input(25)
    floor = day25.parse_input(text)
    grid = [list(line.strip()) for line in text.splitlines() if line.strip()]
    while True:
        nxt = day25.step(floor)
        grid, moved = literal_step(grid)
        assert day25.render(nxt) == "\n".join("".join(row) for row in grid)
        assert (moved == 0) == (nxt == floor)
        if moved == 0:
            break
        floor = nxt


def test_part1_matches_literal_simulator(real_input):
    text = real_input(25)
    assert day25.part1(day25.parse_input(text)) == literal_part1(text)


def bitboard_part1(text: str) -> int:
    """The guide's row-bitmask sidebar (section 7).  Each row is a w-bit int,
    bit c = column c.  East: `ahead` lines bit c+1 up under bit c (a rotate
    right on the ring), so `E & ~ahead(E | S)` is the movers and `fwd`
    rotates them one column on.  South: row r's movers are `S[r]` minus row
    r+1's occupancy, and they arrive in row r+1."""
    rows = [line.strip() for line in text.splitlines() if line.strip()]
    h, w = len(rows), len(rows[0])
    mask = (1 << w) - 1
    east = [sum(1 << c for c, ch in enumerate(row) if ch == ">") for row in rows]
    south = [sum(1 << c for c, ch in enumerate(row) if ch == "v") for row in rows]

    def ahead(x):  # bit c <- bit c+1, wrapping
        return (x >> 1) | ((x & 1) << (w - 1))

    def fwd(x):  # bit c -> bit c+1, wrapping
        return ((x << 1) & mask) | (x >> (w - 1))

    steps = 0
    while True:
        steps += 1
        mv_e = [e & ~ahead(e | s) for e, s in zip(east, south, strict=True)]
        east = [(e & ~m) | fwd(m) for e, m in zip(east, mv_e, strict=True)]
        occ = [e | s for e, s in zip(east, south, strict=True)]
        mv_s = [south[r] & ~occ[(r + 1) % h] for r in range(h)]
        south = [(south[r] & ~mv_s[r]) | mv_s[r - 1] for r in range(h)]
        if not any(mv_e) and not any(mv_s):
            return steps


# Only maps that jam: a map that cycles forever (a lone `>` on a ring) would
# hang both part1 and the sidebar.
@pytest.mark.parametrize("text", [EXAMPLE, ">>>>\n", "v\nv\n", ">v\nv>\n"])
def test_bitboard_sidebar_matches_on_small_maps(text):
    assert bitboard_part1(text) == day25.part1(day25.parse_input(text))


def test_bitboard_sidebar_matches_real(real_input):
    text = real_input(25)
    assert bitboard_part1(text) == day25.part1(day25.parse_input(text))


def test_real_input_locked(check_locked):
    check_locked(day25, LOCKED)
