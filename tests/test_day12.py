"""Day 12: Passage Pathing."""

import pytest

import day12

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (5104, 149220)

SMALL = """\
start-A
start-b
A-c
A-b
b-d
A-end
b-end
"""

MEDIUM = """\
dc-end
HN-start
start-kj
dc-start
dc-HN
LN-dc
HN-end
kj-sa
kj-HN
kj-dc
"""

LARGE = """\
fs-end
he-DX
fs-he
start-DX
pj-DX
end-zg
zg-sl
zg-pj
pj-he
RW-he
fs-DX
pj-RW
zg-RW
start-pj
he-WI
zg-he
pj-fs
start-RW
"""

SMALL_PATHS = """\
start,A,b,A,c,A,end
start,A,b,A,end
start,A,b,end
start,A,c,A,b,A,end
start,A,c,A,b,end
start,A,c,A,end
start,A,end
start,b,A,c,A,end
start,b,A,end
start,b,end
"""

MEDIUM_PATHS = """\
start,HN,dc,HN,end
start,HN,dc,HN,kj,HN,end
start,HN,dc,end
start,HN,dc,kj,HN,end
start,HN,end
start,HN,kj,HN,dc,HN,end
start,HN,kj,HN,dc,end
start,HN,kj,HN,end
start,HN,kj,dc,HN,end
start,HN,kj,dc,end
start,dc,HN,end
start,dc,HN,kj,HN,end
start,dc,end
start,dc,kj,HN,end
start,kj,HN,dc,HN,end
start,kj,HN,dc,end
start,kj,HN,end
start,kj,dc,HN,end
start,kj,dc,end
"""


SMALL_PATHS_TWICE = """start,A,b,A,b,A,c,A,end
start,A,b,A,b,A,end
start,A,b,A,b,end
start,A,b,A,c,A,b,A,end
start,A,b,A,c,A,b,end
start,A,b,A,c,A,c,A,end
start,A,b,A,c,A,end
start,A,b,A,end
start,A,b,d,b,A,c,A,end
start,A,b,d,b,A,end
start,A,b,d,b,end
start,A,b,end
start,A,c,A,b,A,b,A,end
start,A,c,A,b,A,b,end
start,A,c,A,b,A,c,A,end
start,A,c,A,b,A,end
start,A,c,A,b,d,b,A,end
start,A,c,A,b,d,b,end
start,A,c,A,b,end
start,A,c,A,c,A,b,A,end
start,A,c,A,c,A,b,end
start,A,c,A,c,A,end
start,A,c,A,end
start,A,end
start,b,A,b,A,c,A,end
start,b,A,b,A,end
start,b,A,b,end
start,b,A,c,A,b,A,end
start,b,A,c,A,b,end
start,b,A,c,A,c,A,end
start,b,A,c,A,end
start,b,A,end
start,b,d,b,A,c,A,end
start,b,d,b,A,end
start,b,d,b,end
start,b,end
"""


def brute_paths(raw, twice=False):
    """Every start-to-end path, by the statement's rules alone, on the untrimmed edge list.

    Independent of parse_input's trimming: it may try to re-enter start, which
    is refused by the rule itself (start is small and already on the path, and
    in part 2 start may appear only once), and a path stops the first time it
    reaches end.  With `twice`, one small cave per path may appear twice.
    """
    links = {}
    for line in raw.split():
        a, b = line.split("-")
        links.setdefault(a, set()).add(b)
        links.setdefault(b, set()).add(a)

    found = set()
    stack = [("start",)]
    while stack:
        path = stack.pop()
        if path[-1] == "end":
            found.add(path)
            continue
        doubled = any(path.count(c) == 2 for c in path if c.islower())
        for nxt in links[path[-1]]:
            revisit = nxt.islower() and nxt in path
            if revisit and (not twice or doubled or nxt == "start"):
                continue
            stack.append(path + (nxt,))
    return found


def as_paths(listing):
    return {tuple(line.split(",")) for line in listing.split()}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(SMALL, 10), (MEDIUM, 19), (LARGE, 226)],
    ids=["small", "medium", "large"],
)
def test_part1_examples(raw, expected):
    assert day12.part1(day12.parse_input(raw)) == expected


@pytest.mark.parametrize(
    ("raw", "listing"), [(SMALL, SMALL_PATHS), (MEDIUM, MEDIUM_PATHS)], ids=["small", "medium"]
)
def test_brute_force_matches_statement_listing(raw, listing):
    """The reference enumerator reproduces the statement's path lists exactly."""
    assert brute_paths(raw) == as_paths(listing)


@pytest.mark.parametrize("raw", [SMALL, MEDIUM, LARGE], ids=["small", "medium", "large"])
def test_trimmed_graph_count_matches_brute_force(raw):
    """Dropping edges into start and out of end loses no path."""
    assert day12.part1(day12.parse_input(raw)) == len(brute_paths(raw))


def test_real_input_count_matches_brute_force(real_input):
    raw = real_input(12)
    assert day12.part1(day12.parse_input(raw)) == len(brute_paths(raw))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(SMALL, 36), (MEDIUM, 103), (LARGE, 3509)],
    ids=["small", "medium", "large"],
)
def test_part2_examples(raw, expected):
    assert day12.part2(day12.parse_input(raw)) == expected


def test_brute_force_twice_matches_statement_listing():
    assert brute_paths(SMALL, twice=True) == as_paths(SMALL_PATHS_TWICE)


@pytest.mark.parametrize("raw", [SMALL, MEDIUM, LARGE], ids=["small", "medium", "large"])
def test_part2_trimmed_graph_count_matches_brute_force(raw):
    """The trimming is what keeps start from being the cave visited twice."""
    assert day12.part2(day12.parse_input(raw)) == len(brute_paths(raw, twice=True))


def test_part2_real_input_count_matches_brute_force(real_input):
    raw = real_input(12)
    assert day12.part2(day12.parse_input(raw)) == len(brute_paths(raw, twice=True))


@pytest.mark.parametrize("raw", ["start-A\nA-end\n", "start-a\na-end\n"])
def test_part2_start_is_not_the_double(raw):
    """The spare visit must not be spent on start: start,A,start,A,end is not a path."""
    assert day12.part2(day12.parse_input(raw)) == 1


def test_part2_only_one_cave_doubles():
    """start-A, A-x, A-y, A-end: a path is A-separated visits to x and y, i.e. a word over {x, y}.

    Part 1, each letter at most once: "", x, y, xy, yx = 5.
    Part 2, one letter may appear twice: those 5, plus xx, yy, and the six arrangements
    of xxy and yyx (3 each) = 13.  xxyy is out: only one cave may be doubled.
    """
    graph = day12.parse_input("start-A\nA-x\nA-y\nA-end\n")
    assert day12.part1(graph) == 5
    assert day12.part2(graph) == 13


def test_parse_trims_start_and_end():
    graph = day12.parse_input(SMALL)
    assert graph["start"] == ("A", "b")
    assert graph["end"] == ()
    assert all("start" not in nbrs for nbrs in graph.values())
    assert graph["A"] == ("b", "c", "end")


def test_cave_d_is_never_visited():
    """Reaching d means passing b twice, so no path in the small example uses it."""
    assert not any("d" in path for path in brute_paths(SMALL))


def test_dead_end_small_cave_adds_nothing():
    assert day12.part1(day12.parse_input(SMALL)) == day12.part1(day12.parse_input(SMALL.replace("b-d\n", "")))


def test_start_linked_straight_to_end():
    assert day12.part1(day12.parse_input("start-end\n")) == 1


def test_big_cave_can_be_revisited():
    """start-A-end, plus A-x: x can be visited once, returning through A each time."""
    assert day12.part1(day12.parse_input("start-A\nA-end\nA-x\n")) == 2


def test_no_route_to_end_is_zero():
    assert day12.part1(day12.parse_input("start-a\nb-end\n")) == 0


@pytest.mark.parametrize(
    "bad",
    [
        "start-A\nA-B\nB-end\n",  # big-big: A,B,A,B,... never has to stop
        "start-a\n",  # no end
        "a-end\n",  # no start
        "start-end-x\n",
        "start\n",
        "start-a\na-a\na-end\n",
        "start-Ab\nAb-end\n",
    ],
)
def test_malformed_map_is_an_error(bad):
    with pytest.raises(ValueError):
        day12.parse_input(bad)


def test_real_input_has_no_big_big_edge(real_input):
    """The infinite-path case the parser refuses does not occur in the real input."""
    day12.parse_input(real_input(12))


def test_parse_skips_blank_lines():
    assert day12.parse_input("\n" + SMALL + "\n\n") == day12.parse_input(SMALL)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = LARGE.replace("\n", "\r\n")
    assert day12.parse_input(crlf) == day12.parse_input(LARGE)
    assert day12.part1(day12.parse_input(crlf)) == 226
    assert day12.part2(day12.parse_input(crlf)) == 3509


def test_real_input_locked(check_locked):
    check_locked(day12, LOCKED)
