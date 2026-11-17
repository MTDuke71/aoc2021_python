"""Day 23: Amphipod."""

import heapq
import random
from collections import deque
from itertools import pairwise

import pytest

import day23
from day23 import EMPTY, Burrow

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (16244, 43226)

EXAMPLE = """\
#############
#...........#
###B#C#B#D###
  #A#D#C#A#
  #########
"""

# The statement's walk-through, state by state, with the energy it says each
# transition costs.  Some transitions are two trips in the statement's text
# ("3000 and then 30", "2003 in total"), and the Copper one is a direct
# room -> room trip, which this solver makes as two.
WALKTHROUGH = [
    (EXAMPLE, 0),
    (
        """\
#############
#...B.......#
###B#C#.#D###
  #A#D#C#A#
  #########
""",
        40,
    ),
    (
        """\
#############
#...B.......#
###B#.#C#D###
  #A#D#C#A#
  #########
""",
        400,
    ),
    (
        """\
#############
#.....D.....#
###B#.#C#D###
  #A#B#C#A#
  #########
""",
        3030,
    ),
    (
        """\
#############
#.....D.....#
###.#B#C#D###
  #A#B#C#A#
  #########
""",
        40,
    ),
    (
        """\
#############
#.....D.D.A.#
###.#B#C#.###
  #A#B#C#.#
  #########
""",
        2003,
    ),
    (
        """\
#############
#.........A.#
###.#B#C#D###
  #A#B#C#D#
  #########
""",
        7000,
    ),
    (
        """\
#############
#...........#
###A#B#C#D###
  #A#B#C#D#
  #########
""",
        8,
    ),
]

SORTED = WALKTHROUGH[-1][0]

# Part 2's example plan: the statement lists the states only, no per-step energy.
PART2_WALKTHROUGH = [
    """\
#############
#...........#
###B#C#B#D###
  #D#C#B#A#
  #D#B#A#C#
  #A#D#C#A#
  #########
""",
    """\
#############
#..........D#
###B#C#B#.###
  #D#C#B#A#
  #D#B#A#C#
  #A#D#C#A#
  #########
""",
    """\
#############
#A.........D#
###B#C#B#.###
  #D#C#B#.#
  #D#B#A#C#
  #A#D#C#A#
  #########
""",
    """\
#############
#A........BD#
###B#C#.#.###
  #D#C#B#.#
  #D#B#A#C#
  #A#D#C#A#
  #########
""",
    """\
#############
#A......B.BD#
###B#C#.#.###
  #D#C#.#.#
  #D#B#A#C#
  #A#D#C#A#
  #########
""",
    """\
#############
#AA.....B.BD#
###B#C#.#.###
  #D#C#.#.#
  #D#B#.#C#
  #A#D#C#A#
  #########
""",
    """\
#############
#AA.....B.BD#
###B#.#.#.###
  #D#C#.#.#
  #D#B#C#C#
  #A#D#C#A#
  #########
""",
    """\
#############
#AA.....B.BD#
###B#.#.#.###
  #D#.#C#.#
  #D#B#C#C#
  #A#D#C#A#
  #########
""",
    """\
#############
#AA...B.B.BD#
###B#.#.#.###
  #D#.#C#.#
  #D#.#C#C#
  #A#D#C#A#
  #########
""",
    """\
#############
#AA.D.B.B.BD#
###B#.#.#.###
  #D#.#C#.#
  #D#.#C#C#
  #A#.#C#A#
  #########
""",
    """\
#############
#AA.D...B.BD#
###B#.#.#.###
  #D#.#C#.#
  #D#.#C#C#
  #A#B#C#A#
  #########
""",
    """\
#############
#AA.D.....BD#
###B#.#.#.###
  #D#.#C#.#
  #D#B#C#C#
  #A#B#C#A#
  #########
""",
    """\
#############
#AA.D......D#
###B#.#.#.###
  #D#B#C#.#
  #D#B#C#C#
  #A#B#C#A#
  #########
""",
    """\
#############
#AA.D......D#
###B#.#C#.###
  #D#B#C#.#
  #D#B#C#.#
  #A#B#C#A#
  #########
""",
    """\
#############
#AA.D.....AD#
###B#.#C#.###
  #D#B#C#.#
  #D#B#C#.#
  #A#B#C#.#
  #########
""",
    """\
#############
#AA.......AD#
###B#.#C#.###
  #D#B#C#.#
  #D#B#C#.#
  #A#B#C#D#
  #########
""",
    """\
#############
#AA.......AD#
###.#B#C#.###
  #D#B#C#.#
  #D#B#C#.#
  #A#B#C#D#
  #########
""",
    """\
#############
#AA.......AD#
###.#B#C#.###
  #.#B#C#.#
  #D#B#C#D#
  #A#B#C#D#
  #########
""",
    """\
#############
#AA.D.....AD#
###.#B#C#.###
  #.#B#C#.#
  #.#B#C#D#
  #A#B#C#D#
  #########
""",
    """\
#############
#A..D.....AD#
###.#B#C#.###
  #.#B#C#.#
  #A#B#C#D#
  #A#B#C#D#
  #########
""",
    """\
#############
#...D.....AD#
###.#B#C#.###
  #A#B#C#.#
  #A#B#C#D#
  #A#B#C#D#
  #########
""",
    """\
#############
#.........AD#
###.#B#C#.###
  #A#B#C#D#
  #A#B#C#D#
  #A#B#C#D#
  #########
""",
    """\
#############
#..........D#
###A#B#C#.###
  #A#B#C#D#
  #A#B#C#D#
  #A#B#C#D#
  #########
""",
    """\
#############
#...........#
###A#B#C#D###
  #A#B#C#D#
  #A#B#C#D#
  #A#B#C#D#
  #########
""",
]


def diagram(hall: str, *rows: str) -> str:
    """Build a burrow diagram from an 11-char hallway and room rows like 'BACD'."""
    lines = ["#" * 13, f"#{hall}#"]
    for d, row in enumerate(rows):
        cells = "#".join(row)
        lines.append(f"###{cells}###" if d == 0 else f"  #{cells}#")
    lines.append("  " + "#" * 9)
    return "\n".join(lines) + "\n"


# --- parse / render ---------------------------------------------------------


def test_parse_example():
    b = day23.parse_input(EXAMPLE)
    assert b.hall == (EMPTY,) * 11
    assert b.rooms == (("B", "A"), ("C", "D"), ("B", "C"), ("D", "A"))


def test_diagram_helper_matches_statement():
    assert diagram("...........", "BCBD", "ADCA") == EXAMPLE


@pytest.mark.parametrize("text, _", WALKTHROUGH)
def test_render_round_trips(text, _):
    b = day23.parse_input(text)
    assert b.render() + "\n" == text
    assert day23.parse_input(b.render()) == b


def test_parse_depth_is_read_from_diagram():
    b = day23.parse_input(diagram("...........", "BACD"))
    assert b.rooms == (("B",), ("A",), ("C",), ("D",))
    b = day23.parse_input(diagram("...........", "BACD", "ABCD", "ABDC"))
    assert len(b.rooms[0]) == 3


@pytest.mark.parametrize(
    "bad",
    [
        diagram("...........", "BCBD", "ADCB"),  # three B, one A
        diagram("..A........", "BCBD", "ADC."),  # standing in a doorway
        diagram("...........", "BCBD", "ADCX"),  # unknown letter
        "#############\n#...........#\n  #########\n",
        "",
    ],
)
def test_malformed_input_is_an_error(bad):
    with pytest.raises(ValueError):
        day23.parse_input(bad)


def test_gap_under_amphipod_is_an_error():
    with pytest.raises(ValueError, match="gap"):
        # Room A holds B on top of an empty cell.
        day23.parse_input(diagram("A..........", "BCBD", ".ACD"))


# --- small hand-checked cases ------------------------------------------------


def test_already_sorted_costs_nothing():
    assert day23.part1(day23.parse_input(SORTED)) == 0


HAND_CHECKED = [
    # A at hallway 0 -> door 2 (2 steps) -> top cell (1 step): 3 * 1.
    (diagram("A..........", ".BCD", "ABCD"), 3),
    # D at 9 must go first (it blocks 10): 9 -> door 8 (1) -> bottom (2),
    # then 10 -> door 8 (2) -> top (1).  (3 + 3) * 1000.
    (diagram(".........DD", "ABC.", "ABC."), 6000),
    # Swap the tops of rooms A and B.  The obvious plan (B parks at 3,
    # A goes home) fails: B at 3 blocks A's path to door 2.  Best is
    # A out to 5 (2 steps, 2), B out to 3 (2 steps, 20), B home past
    # nobody (3 -> 4 -> top: 2 steps, 20), A home (5 -> 2 -> top:
    # 4 steps, 4).  Total 46.
    (diagram("...........", "BACD", "ABCD"), 46),
]


@pytest.mark.parametrize("text, want", HAND_CHECKED)
def test_hand_checked(text, want):
    assert day23.part1(day23.parse_input(text)) == want


def test_deadlock_raises():
    # D at 3 must pass 5 to go right; A at 5 must pass 3 to go left.
    with pytest.raises(ValueError, match="cannot"):
        day23.part1(day23.parse_input(diagram("...D.A.....", ".BC.", "ABCD")))


# --- the statement ---------------------------------------------------------


def test_part1_example():
    assert day23.part1(day23.parse_input(EXAMPLE)) == 12521


def test_walkthrough_energies_sum_to_answer():
    assert sum(e for _, e in WALKTHROUGH) == 12521


def shortest(a: Burrow, b: Burrow) -> int:
    """Least energy from a to b using day23.moves (Dijkstra to an arbitrary target)."""
    best = {a: 0}
    heap = [(0, a)]
    while heap:
        cost, s = heapq.heappop(heap)
        if s == b:
            return cost
        if cost > best[s]:
            continue
        for e, n in day23.moves(s):
            if cost + e < best.get(n, cost + e + 1):
                best[n] = cost + e
                heapq.heappush(heap, (cost + e, n))
    raise AssertionError("unreachable")


@pytest.mark.parametrize("i", range(1, len(WALKTHROUGH)))
def test_walkthrough_each_transition(i):
    """Each step of the statement's plan is reachable with exactly the stated energy."""
    a = day23.parse_input(WALKTHROUGH[i - 1][0])
    b = day23.parse_input(WALKTHROUGH[i][0])
    assert shortest(a, b) == WALKTHROUGH[i][1]


# --- literal reference ---------------------------------------------------------
#
# Works on the text grid itself: BFS through open cells for every amphipod,
# with the statement's three rules applied as written and none of the
# solver's shortcuts.  It allows direct room -> room trips, stopping at any
# free cell of a clean destination room (not just the deepest), and walking
# out of a room that is already settled.  Agreement pins all three shortcuts.

DOOR_COLS = (3, 5, 7, 9)


def literal_least_energy(text: str) -> int:
    grid = [list(line.ljust(13)) for line in text.rstrip("\n").split("\n")]
    depth = len(grid) - 3
    room_rows = range(2, 2 + depth)

    def dest_col(a):
        return DOOR_COLS["ABCD".index(a)]

    def room_clean(g, col, a):
        return all(g[r][col] in (EMPTY, a) for r in room_rows)

    def reachable(g, r0, c0):
        dist = {(r0, c0): 0}
        q = deque([(r0, c0)])
        while q:
            r, c = q.popleft()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if (nr, nc) not in dist and g[nr][nc] == EMPTY:
                    dist[nr, nc] = dist[r, c] + 1
                    q.append((nr, nc))
        del dist[r0, c0]
        return dist

    def key(g):
        return "".join("".join(row) for row in g)

    def is_goal(g):
        return "".join(g[r][col] for r in room_rows for col in DOOR_COLS) == "ABCD" * depth

    start = [row[:] for row in grid]
    best = {key(start): 0}
    heap = [(0, key(start), start)]
    while heap:
        cost, k, g = heapq.heappop(heap)
        if is_goal(g):
            return cost
        if cost > best[k]:
            continue
        for r0, row in enumerate(g):
            for c0, a in enumerate(row):
                if a not in "ABCD":
                    continue
                for (r, c), steps in reachable(g, r0, c0).items():
                    if r == 1:
                        if r0 == 1 or c in DOOR_COLS:
                            continue  # rule 3 (parked stays parked), rule 1 (no doorway stops)
                    else:
                        if c == c0:
                            continue  # shuffling within one room: never useful
                        if c != dest_col(a) or not room_clean(g, c, a):
                            continue  # rule 2
                    n = [rw[:] for rw in g]
                    n[r0][c0] = EMPTY
                    n[r][c] = a
                    nk = key(n)
                    new_cost = cost + steps * day23.ENERGY[a]
                    if new_cost < best.get(nk, new_cost + 1):
                        best[nk] = new_cost
                        heapq.heappush(heap, (new_cost, nk, n))
    raise ValueError("no solution")


@pytest.mark.parametrize("text, want", HAND_CHECKED)
def test_literal_reference_on_hand_checked(text, want):
    assert literal_least_energy(text) == want


def test_literal_reference_on_example():
    assert literal_least_energy(EXAMPLE) == 12521


def random_diagram(rng, depth):
    cells = list("ABCD" * depth)
    rng.shuffle(cells)
    rows = ["".join(cells[i : i + 4]) for i in range(0, len(cells), 4)]
    return diagram("...........", *rows)


@pytest.mark.parametrize("seed", range(20))
def test_matches_literal_reference_depth1(seed):
    text = random_diagram(random.Random(seed), 1)
    assert day23.part1(day23.parse_input(text)) == literal_least_energy(text)


@pytest.mark.parametrize("seed", range(2))  # ~10 s each
def test_matches_literal_reference_depth2(seed):
    text = random_diagram(random.Random(1000 + seed), 2)
    assert day23.part1(day23.parse_input(text)) == literal_least_energy(text)


def test_part1_matches_literal_reference_real(real_input):
    raw = real_input(23)
    assert day23.part1(day23.parse_input(raw)) == literal_least_energy(raw)


# --- part 2 ------------------------------------------------------------------


def test_unfold_example_matches_statement():
    assert day23.unfold(day23.parse_input(EXAMPLE)).render() + "\n" == PART2_WALKTHROUGH[0]


def test_unfold_refuses_other_depths():
    with pytest.raises(ValueError):
        day23.unfold(day23.parse_input(PART2_WALKTHROUGH[0]))


def test_part2_example():
    assert day23.part2(day23.parse_input(EXAMPLE)) == 44169


def test_part2_walkthrough_adds_up():
    """Every state in the statement's plan follows from the one before, and the
    cheapest way through those checkpoints costs exactly the stated optimum."""
    states = [day23.parse_input(t) for t in PART2_WALKTHROUGH]
    assert states[-1] == day23.goal_for(4)
    assert sum(shortest(a, b) for a, b in pairwise(states)) == 44169


def optimal_plan(start: Burrow) -> tuple[int, int]:
    """(energy, trip count) of the cheapest plan Dijkstra finds, by parent pointers."""
    goal = day23.goal_for(len(start.rooms[0]))
    best, parent = {start: 0}, {start: None}
    heap = [(0, start)]
    while heap:
        cost, s = heapq.heappop(heap)
        if s == goal:
            break
        if cost > best[s]:
            continue
        for e, n in day23.moves(s):
            if cost + e < best.get(n, cost + e + 1):
                best[n], parent[n] = cost + e, s
                heapq.heappush(heap, (cost + e, n))
    trips, s = 0, goal
    while parent[s] is not None:
        trips, s = trips + 1, parent[s]
    return best[goal], trips


def unsettled(b: Burrow) -> int:
    """Amphipods not already home with only their own kind beneath them."""
    return sum(
        1
        for r, room in enumerate(b.rooms)
        for d, a in enumerate(room)
        if a != EMPTY and any(c != day23.TYPES[r] for c in room[d:])
    ) + sum(1 for a in b.hall if a != EMPTY)


@pytest.mark.parametrize("unfold, energy, want_unsettled", [(False, 12521, 6), (True, 44169, 14)])
def test_trip_count_is_forced(unfold, energy, want_unsettled):
    """Guide section 9: every amphipod moves out once and home once, settled ones not at all."""
    b = day23.parse_input(EXAMPLE)
    if unfold:
        b = day23.unfold(b)
    assert unsettled(b) == want_unsettled
    assert optimal_plan(b) == (energy, 2 * want_unsettled)


# --- CRLF / locked -------------------------------------------------------------


def test_crlf_input():
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day23.parse_input(crlf) == day23.parse_input(EXAMPLE)
    assert day23.part1(day23.parse_input(crlf)) == 12521
    assert day23.part2(day23.parse_input(crlf)) == 44169


def test_real_input_locked(check_locked):
    check_locked(day23, LOCKED)
