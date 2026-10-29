"""Day 15: Chiton."""

from itertools import pairwise

import pytest

import day15

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (508, 2872)

EXAMPLE = """\
1163751742
1381373672
2136511328
3694931569
7463417111
1319128137
1359912421
3125421639
1293138521
2311944581
"""

# Part 2's full map of the example, from the statement.
FULL_EXAMPLE = """\n11637517422274862853338597396444961841755517295286
13813736722492484783351359589446246169155735727126
21365113283247622439435873354154698446526571955763
36949315694715142671582625378269373648937148475914
74634171118574528222968563933317967414442817852555
13191281372421239248353234135946434524615754563572
13599124212461123532357223464346833457545794456865
31254216394236532741534764385264587549637569865174
12931385212314249632342535174345364628545647573965
23119445813422155692453326671356443778246755488935
22748628533385973964449618417555172952866628316397
24924847833513595894462461691557357271266846838237
32476224394358733541546984465265719557637682166874
47151426715826253782693736489371484759148259586125
85745282229685639333179674144428178525553928963666
24212392483532341359464345246157545635726865674683
24611235323572234643468334575457944568656815567976
42365327415347643852645875496375698651748671976285
23142496323425351743453646285456475739656758684176
34221556924533266713564437782467554889357866599146
33859739644496184175551729528666283163977739427418
35135958944624616915573572712668468382377957949348
43587335415469844652657195576376821668748793277985
58262537826937364893714847591482595861259361697236
96856393331796741444281785255539289636664139174777
35323413594643452461575456357268656746837976785794
35722346434683345754579445686568155679767926678187
53476438526458754963756986517486719762859782187396
34253517434536462854564757396567586841767869795287
45332667135644377824675548893578665991468977611257
44961841755517295286662831639777394274188841538529
46246169155735727126684683823779579493488168151459
54698446526571955763768216687487932779859814388196
69373648937148475914825958612593616972361472718347
17967414442817852555392896366641391747775241285888
46434524615754563572686567468379767857948187896815
46833457545794456865681556797679266781878137789298
64587549637569865174867197628597821873961893298417
45364628545647573965675868417678697952878971816398
56443778246755488935786659914689776112579188722368
55172952866628316397773942741888415385299952649631
57357271266846838237795794934881681514599279262561
65719557637682166874879327798598143881961925499217
71484759148259586125936169723614727183472583829458
28178525553928963666413917477752412858886352396999
57545635726865674683797678579481878968159298917926
57944568656815567976792667818781377892989248891319
75698651748671976285978218739618932984172914319528
56475739656758684176786979528789718163989182927419
67554889357866599146897761125791887223681299833479
"""

# The statement's highlighted path, as (row, col) cells after the start.
EXAMPLE_PATH = [
    (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, 6), (3, 7),
    (4, 7), (5, 7), (5, 8), (6, 8), (7, 8), (8, 8), (8, 9), (9, 9),
]  # fmt: skip

# The cheap route snakes right, down, LEFT, down, right for 18.  A path that only
# moves right and down has to cross one of the two-deep walls of 9s.
SNAKE = """\
11111
99991
99991
11111
19999
19999
11111
"""


def relax_to_fixpoint(grid):
    """Bellman-Ford style reference, independent of day15's Dijkstra.

    Start every cell at infinity except the origin, then sweep all cells,
    lowering each to (cheapest neighbour + own risk), until a sweep changes
    nothing.  Slow but obviously correct.
    """
    height, width = len(grid), len(grid[0])
    inf = float("inf")
    dist = [[inf] * width for _ in range(height)]
    dist[0][0] = 0
    changed = True
    while changed:
        changed = False
        for r in range(height):
            for c in range(width):
                if (r, c) == (0, 0):
                    continue
                around = [
                    dist[nr][nc]
                    for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                    if 0 <= nr < height and 0 <= nc < width
                ]
                cand = min(around) + grid[r][c]
                if cand < dist[r][c]:
                    dist[r][c] = cand
                    changed = True
    return dist[-1][-1]


def right_down_dp(grid):
    """The tempting shortcut: each cell reached only from above or from the left."""
    height, width = len(grid), len(grid[0])
    dist = [[0] * width for _ in range(height)]
    for r in range(height):
        for c in range(width):
            if (r, c) == (0, 0):
                continue
            prev = [dist[pr][pc] for pr, pc in ((r - 1, c), (r, c - 1)) if pr >= 0 and pc >= 0]
            dist[r][c] = min(prev) + grid[r][c]
    return dist[-1][-1]


def test_parse_example():
    grid = day15.parse_input(EXAMPLE)
    assert len(grid) == 10
    assert all(len(row) == 10 for row in grid)
    assert grid[0] == (1, 1, 6, 3, 7, 5, 1, 7, 4, 2)
    assert grid[9][9] == 1


def test_statement_path_sums_to_40():
    """The highlighted path is a legal walk and its entered cells total 40."""
    grid = day15.parse_input(EXAMPLE)
    cells = [(0, 0), *EXAMPLE_PATH]
    for (r0, c0), (r1, c1) in pairwise(cells):
        assert abs(r1 - r0) + abs(c1 - c0) == 1
    assert sum(grid[r][c] for r, c in EXAMPLE_PATH) == 40


def test_part1_example():
    assert day15.part1(day15.parse_input(EXAMPLE)) == 40


@pytest.mark.parametrize(
    ("raw", "want"),
    [
        ("7\n", 0),  # start is the target; nothing is entered
        ("19\n", 9),
        ("1\n9\n", 9),
        ("123\n", 5),
        ("99\n11\n", 2),  # down then right beats right then down
        (SNAKE, 18),
    ],
)
def test_small_grids(raw, want):
    assert day15.lowest_risk(day15.parse_input(raw)) == want


def test_start_risk_is_never_counted():
    """Changing only the start cell's risk leaves the answer alone."""
    grid = day15.parse_input(EXAMPLE)
    for start in range(10):
        bumped = ((start, *grid[0][1:]), *grid[1:])
        assert day15.lowest_risk(bumped) == 40


def test_right_down_dp_is_not_enough():
    """The snake grid needs a leftward move; a right/down-only DP overpays."""
    grid = day15.parse_input(SNAKE)
    assert day15.lowest_risk(grid) == 18
    assert right_down_dp(grid) == 26


@pytest.mark.parametrize("which", ["example", "snake", "real"])
def test_matches_reference(which, real_input):
    raw = {"example": EXAMPLE, "snake": SNAKE}.get(which) or real_input(15)
    grid = day15.parse_input(raw)
    assert day15.lowest_risk(grid) == relax_to_fixpoint(grid)


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "\n\n",
        "123\n12\n",  # ragged
        "12a\n",
        "1 2\n",
        "10\n",  # risk 0: part 2's wrap rule only covers 1-9
        "١٢\n",  # Arabic-Indic digits: isdigit() but not ASCII
    ],
)
def test_malformed_input_is_an_error(bad):
    with pytest.raises(ValueError):
        day15.parse_input(bad)


@pytest.mark.parametrize("v", range(1, 10))
@pytest.mark.parametrize("k", range(9))
def test_wrap_formula_matches_literal_rule(v, k):
    """(v + k - 1) % 9 + 1 is "add 1, k times, and wrap anything above 9 back to 1"."""
    literal = v
    for _ in range(k):
        literal = 1 if literal == 9 else literal + 1
    tiled = day15.tile(((v,),), 9)
    assert tiled[0][k] == tiled[k][0] == literal


def test_tile_of_8_matches_statement():
    assert day15.tile(((8,),), 5) == (
        (8, 9, 1, 2, 3),
        (9, 1, 2, 3, 4),
        (1, 2, 3, 4, 5),
        (2, 3, 4, 5, 6),
        (3, 4, 5, 6, 7),
    )


def test_tile_example_matches_statement():
    assert day15.tile(day15.parse_input(EXAMPLE), 5) == day15.parse_input(FULL_EXAMPLE)


def test_tile_once_is_identity():
    grid = day15.parse_input(EXAMPLE)
    assert day15.tile(grid, 1) == grid


def test_part2_example():
    assert day15.part2(day15.parse_input(EXAMPLE)) == 315


def test_part2_example_matches_reference():
    full = day15.tile(day15.parse_input(EXAMPLE), 5)
    assert relax_to_fixpoint(full) == 315


@pytest.mark.parametrize("which", ["example", "snake", "real1", "real2"])
def test_every_cell_is_pushed_once(which, real_input, monkeypatch):
    """The first push of a cell already carries its final risk, so the heap never holds a stale entry.

    Entering a cell costs the same from every neighbour, and neighbours are
    popped in order of their own risk, so whichever reaches a cell first
    offers the lowest risk it will ever be offered.
    """
    raw = {"example": EXAMPLE, "snake": SNAKE}.get(which) or real_input(15)
    grid = day15.parse_input(raw)
    if which == "real2":
        grid = day15.tile(grid, 5)
    pushed = []
    real_push = day15.heapq.heappush
    monkeypatch.setattr(
        day15.heapq, "heappush", lambda heap, item: (pushed.append(item[1:]), real_push(heap, item))
    )
    day15.lowest_risk(grid)
    assert len(pushed) == len(set(pushed))


def test_right_down_dp_fails_on_real_input(real_input):
    """Not just a contrived grid: the real cave's best paths both need an up or left move."""
    grid = day15.parse_input(real_input(15))
    assert (day15.lowest_risk(grid), right_down_dp(grid)) == (508, 510)
    full = day15.tile(grid, 5)
    assert right_down_dp(full) > day15.lowest_risk(full)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day15.parse_input(crlf) == day15.parse_input(EXAMPLE)
    assert day15.part1(day15.parse_input(crlf)) == 40
    assert day15.part2(day15.parse_input(crlf)) == 315


def test_real_input_locked(check_locked):
    check_locked(day15, LOCKED)
