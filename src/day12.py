"""Day 12: Passage Pathing.

The input is an undirected graph, one edge per line as `a-b`.  Caves named in
upper case are big and may be visited any number of times; lower-case caves
are small and may be visited at most once.  The answer is the number of
distinct paths from `start` to `end`.

parse_input builds an adjacency map with two edges trimmed, because the
statement makes them unusable: nothing may step back into `start` (it is a
small cave and every path has already used it), and nothing steps out of
`end` (a path finishes there).  It also refuses an edge between two big
caves: the walk could bounce between them forever, so the count would be
infinite.

Part 1 is a depth-first count: from a cave, sum the paths from each
neighbour that is not a small cave already on the current path.  The count
is memoised on (cave, visited small caves, spare): the number of ways to
finish depends only on those, not on the order the walk got there, so the
search does each distinct state once instead of once per path through it.

Part 2 lets one small cave per path be visited twice.  The same count
carries one more bit of state, `spare`: whether that second visit is still
unspent.  Stepping into a small cave already on the path is allowed only by
spending it.  `start` and `end` must be visited exactly once, and the
trimmed edges already guarantee that: there is no edge back into `start`
and none out of `end`, so neither can be the cave visited twice.
"""

from collections import defaultdict
from functools import cache
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day12.txt"

Graph = dict[str, tuple[str, ...]]

START = "start"
END = "end"


def is_small(cave: str) -> bool:
    return cave.islower()


def parse_input(raw: str) -> Graph:
    """Adjacency map with edges into `start` and out of `end` removed."""
    links: defaultdict[str, set[str]] = defaultdict(set)
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        a, sep, b = line.partition("-")
        for cave in (a, b):
            if not (cave.isascii() and cave.isalpha() and (cave.isupper() or cave.islower())):
                raise ValueError(f"bad cave name in {line!r}")
        if not sep:
            raise ValueError(f"not an a-b edge: {line!r}")
        if a == b:
            raise ValueError(f"cave linked to itself: {line!r}")
        if not is_small(a) and not is_small(b):
            raise ValueError(f"two big caves linked, so infinitely many paths: {line!r}")
        links[a].add(b)
        links[b].add(a)
    if START not in links or END not in links:
        raise ValueError("the map needs both a start and an end cave")

    graph = {cave: tuple(sorted(n for n in nbrs if n != START)) for cave, nbrs in links.items()}
    graph[END] = ()
    return graph


def count_paths(graph: Graph, spare: bool) -> int:
    """Paths from `start` to `end`; `spare` allows one small cave a second visit.

    The cache lives inside this call, so it is keyed on one graph only and is
    dropped when the count is done.
    """

    @cache
    def paths_from(cave: str, visited: frozenset[str], spare: bool) -> int:
        """Ways to finish from `cave`, given the small caves already on the path.

        Re-entering a visited small cave is allowed only while `spare` is True,
        and doing so spends it.
        """
        if cave == END:
            return 1
        total = 0
        for nxt in graph[cave]:
            if nxt in visited:
                if spare:
                    total += paths_from(nxt, visited, False)
                continue
            total += paths_from(nxt, visited | {nxt} if is_small(nxt) else visited, spare)
        return total

    return paths_from(START, frozenset({START}), spare)


def part1(parsed: Graph) -> int:
    return count_paths(parsed, spare=False)


def part2(parsed: Graph) -> int:
    return count_paths(parsed, spare=True)


def solve(raw: str) -> tuple[int, int]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    # Printed one part at a time so part 1's answer is on screen to submit
    # while part 2 is still raising NotImplementedError.
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
