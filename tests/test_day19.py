"""Day 19: Beacon Scanner."""

import re
from collections import Counter
from itertools import combinations
from pathlib import Path

import pytest

import day19

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (465, 12149)

STATEMENT = (Path(__file__).resolve().parents[1] / "Problem_Statements" / "days" / "day19.md").read_text()
BLOCKS = re.findall(r"```text\n(.*?)```", STATEMENT, re.DOTALL)


def block(*needles):
    """The statement's code block containing every needle (there must be exactly one)."""
    (found,) = [b for b in BLOCKS if all(n in b for n in needles)]
    return found


def listing(first, second):
    """A bare coordinate listing (no scanner header) that opens with these two lines."""
    (found,) = [b for b in BLOCKS if b.startswith(f"{first}\n{second}\n")]
    return found


def points(text):
    return [tuple(map(int, line.split(","))) for line in text.split()]


EXAMPLE = block("--- scanner 4 ---")
EXAMPLE_SCANNERS = [(0, 0, 0), (68, -1246, -43), (1105, -1205, 1229), (-92, -2380, -20), (-20, -1133, 1061)]
EXAMPLE_BEACONS = points(listing("-892,524,684", "-876,649,763"))
SHARED_0_1_IN_0 = points(listing("-618,-824,-621", "-537,-823,-458"))  # 0/1 overlap, scanner 0's frame
SHARED_0_1_IN_1 = points(listing("686,422,578", "605,423,415"))  # same 12, same order, scanner 1's frame
SHARED_1_4_IN_0 = points(listing("459,-707,401", "-739,-1745,668"))


# --- rotations -------------------------------------------------------------


def matrix(rotation):
    """3x3 matrix of a rotation, built by rotating the unit vectors (columns)."""
    cols = [day19.rotate(e, rotation) for e in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]]
    return tuple(tuple(cols[c][r] for c in range(3)) for r in range(3))


def det(m):
    (a, b, c), (d, e, f), (g, h, i) = m
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def matmul(m, n):
    return tuple(tuple(sum(m[r][k] * n[k][c] for k in range(3)) for c in range(3)) for r in range(3))


def test_24_distinct_proper_rotations():
    mats = [matrix(r) for r in day19.ROTATIONS]
    assert len(mats) == len(set(mats)) == 24
    assert all(det(m) == 1 for m in mats)
    assert mats[0] == ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def test_rotations_are_what_quarter_turns_generate():
    """Independent derivation: close {90-degree turn about x, y, z} under composition -> the same 24."""
    turns = [
        ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
        ((0, 0, 1), (0, 1, 0), (-1, 0, 0)),
        ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
    ]
    group = {((1, 0, 0), (0, 1, 0), (0, 0, 1))}
    while True:
        grown = group | {matmul(t, g) for t in turns for g in group}
        if grown == group:
            break
        group = grown
    assert group == {matrix(r) for r in day19.ROTATIONS}


def test_statement_orientations_are_all_rotations_of_each_other():
    """The statement's five views of one scanner: each is some rotation of the first, point for point."""
    chunks = block("8,0,7", "0,7,-8").split("--- scanner 0 ---")
    views = [points(chunk) for chunk in chunks if chunk.strip()]
    assert len(views) == 5
    for view in views:
        assert any([day19.rotate(p, r) for p in views[0]] == view for r in day19.ROTATIONS)


# --- the example -----------------------------------------------------------


def test_example_scanner_positions():
    assert day19.parse_input(EXAMPLE).scanners == tuple(EXAMPLE_SCANNERS)


def test_example_beacon_map():
    beacon_map = day19.parse_input(EXAMPLE)
    assert len(EXAMPLE_BEACONS) == 79
    assert beacon_map.beacons == set(EXAMPLE_BEACONS)
    assert day19.part1(beacon_map) == 79


def test_example_shared_beacons():
    """The statement's two 12-beacon overlap listings, in scanner 0's frame."""
    beacon_map = day19.parse_input(EXAMPLE)
    assert beacon_map.views[0] & beacon_map.views[1] == set(SHARED_0_1_IN_0)
    assert beacon_map.views[1] & beacon_map.views[4] == set(SHARED_1_4_IN_0)


def test_align_scanner_1_onto_scanner_0():
    """The listed 12 beacons from 1's frame land on the listed 12 from 0's, in order, after align."""
    reports = day19.parse_reports(EXAMPLE)
    position, moved = day19.align(reports[0], reports[1])
    assert position == (68, -1246, -43)
    lookup = dict(zip(reports[1], moved, strict=True))
    assert [lookup[p] for p in SHARED_0_1_IN_1] == SHARED_0_1_IN_0


def test_two_dimensional_example_in_the_plane():
    """The statement's 2-D warm-up as z=0 points with 3 shared: scanner 1 sits at (5, 2)."""
    s0 = [(0, 2, 0), (4, 1, 0), (3, 3, 0)]
    s1 = [(-1, -1, 0), (-5, 0, 0), (-2, 1, 0)]
    votes = Counter((a[0] - b[0], a[1] - b[1]) for a in s0 for b in s1)
    assert votes.most_common(1) == [((5, 2), 3)]


def test_part2_example():
    """Scanners 2 and 3: 1197 + 1175 + 1249 = 3621, and no other pair is as far apart."""
    beacon_map = day19.parse_input(EXAMPLE)
    s = beacon_map.scanners
    assert [abs(p - q) for p, q in zip(s[2], s[3])] == [1197, 1175, 1249]
    assert day19.part2(beacon_map) == day19.manhattan(s[2], s[3]) == 3621
    others = [day19.manhattan(s[i], s[j]) for i, j in combinations(range(5), 2) if (i, j) != (2, 3)]
    assert max(others) < 3621


# --- correctness properties --------------------------------------------------


def check_consistent(beacon_map):
    """Each scanner's view is exactly the map's beacons inside its +-1000 cube: nothing missing, nothing extra.

    This is what a wrong alignment would break: a mislocked scanner would claim beacons that a correctly
    placed neighbour, whose cube covers them, does not see (or vice versa).
    """
    for position, view in zip(beacon_map.scanners, beacon_map.views, strict=True):
        inside = {p for p in beacon_map.beacons if all(abs(p[k] - position[k]) <= 1000 for k in range(3))}
        assert inside == view


def test_example_is_consistent():
    check_consistent(day19.parse_input(EXAMPLE))


def test_real_is_consistent(real_input):
    check_consistent(day19.parse_input(real_input(19)))


@pytest.mark.parametrize("source", ["example", "real"])
def test_fingerprint_never_rejects_a_real_overlap(source, real_input):
    """The prefilter shortcut: >= 12 shared beacons implies >= C(12,2) = 66 shared pair distances.

    On the real input it is also exact -- it passes the 53 true neighbour pairs and nothing else: true
    pairs share 66 distances (51 pairs) or 67 (2 pairs, one coincidental match), non-pairs at most 16.
    """
    raw = EXAMPLE if source == "example" else real_input(19)
    reports = day19.parse_reports(raw)
    beacon_map = day19.assemble(reports)
    fps = [day19.fingerprint(r) for r in reports]
    true_shared, other_shared = Counter(), []
    for a, b in combinations(range(len(reports)), 2):
        overlapping = len(beacon_map.views[a] & beacon_map.views[b]) >= day19.MIN_SHARED
        assert day19.could_overlap(fps[a], fps[b]) or not overlapping
        shared = (fps[a] & fps[b]).total()
        if overlapping:
            true_shared[shared] += 1
        else:
            other_shared.append(shared)
    if source == "real":
        assert true_shared == {66: 51, 67: 2}
        assert max(other_shared) == 16


def test_prefilter_does_not_change_the_map(monkeypatch, real_input):
    """Assembling with the fingerprint check switched off (every pair gets the full vote) gives the same map."""
    reports = day19.parse_reports(real_input(19))
    filtered = day19.assemble(reports)
    monkeypatch.setattr(day19, "could_overlap", lambda a, b: True)
    assert day19.assemble(reports) == filtered


def test_real_overlaps_are_0_3_6_or_12(real_input):
    """How the real input was built: any two scanners share 0, 3, 6 or exactly 12 beacons, never 7-11 or 13+.

    So the 12 threshold has no near misses to get wrong in either direction.
    """
    beacon_map = day19.parse_input(real_input(19))
    sizes = {len(a & b) for a, b in combinations(beacon_map.views, 2)}
    assert sizes == {0, 3, 6, 12}


def test_scrambled_example_reassembles(real_input):
    """Re-express every scanner but 0 in a different random-ish rotation: the same map comes back."""
    reports = day19.parse_reports(EXAMPLE)
    scrambled = [reports[0]] + [
        [day19.rotate(p, day19.ROTATIONS[(7 * n + 5) % 24]) for p in r] for n, r in enumerate(reports[1:], 1)
    ]
    assert day19.assemble(scrambled).beacons == day19.parse_input(EXAMPLE).beacons


# --- malformed input -------------------------------------------------------


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "1,2,3",  # beacon before any header
        "--- scanner 1 ---\n1,2,3",  # numbering must start at 0
        "--- scanner 0 ---\n1,2,3\n\n--- scanner 2 ---\n4,5,6",  # skipped a number
        "--- scanner 0 ---\n1,2",  # 2-D point
        "--- scanner 0 ---\n1,2,3\n1,2,3",  # duplicate beacon
    ],
)
def test_malformed_input_is_an_error(bad):
    with pytest.raises(ValueError):
        day19.parse_reports(bad)


def test_unreachable_scanner_is_an_error():
    lonely = EXAMPLE + "\n--- scanner 5 ---\n1,2,3\n4,5,6\n"
    with pytest.raises(ValueError, match=r"\[5\]"):
        day19.parse_input(lonely)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    beacon_map = day19.parse_input(EXAMPLE.replace("\n", "\r\n"))
    assert (day19.part1(beacon_map), day19.part2(beacon_map)) == (79, 3621)


def test_real_input_locked(check_locked):
    check_locked(day19, LOCKED)
