"""Day 19: Beacon Scanner.

Each scanner reports the beacons within 1000 units of it, in its own frame:
unknown position, and one of 24 unknown orientations (axis-aligned rotations).
Two scanners that share at least 12 beacons can be locked together.  Starting
from scanner 0's frame, lock every scanner in, then

  part 1  count the distinct beacons in the assembled map
  part 2  the largest Manhattan distance between two scanner positions

Representation: a point is an (x, y, z) tuple; a rotation is a signed axis
permutation, (perm, signs), meaning  R(p)[k] = signs[k] * p[perm[k]].  The 24
of them are the 48 signed permutations with determinant +1 (the other 24 are
mirror images, which a physical scanner cannot be in).

Alignment of scanner B against an already-placed scanner A, for one rotation
R: every pairing (a in A, b in B) votes for the offset a - R(b).  If B really
is A's neighbour under R, the true scanner position gets one vote per shared
beacon, so >= 12; a wrong R or a non-neighbour scatters its votes.

Prefilter (`fingerprint`): the multiset of squared distances between every
pair of a scanner's beacons.  Distances survive any rotation and translation,
so 12 shared beacons mean at least C(12, 2) = 66 shared distances.  That makes
"shares >= 66 distances" a *necessary* condition: it never rejects a real
neighbour, it only saves running the 24-rotation vote on pairs that cannot
work.
"""

from collections import Counter, deque
from dataclasses import dataclass
from itertools import combinations, permutations
from math import comb
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day19.txt"

Point = tuple[int, int, int]
Rotation = tuple[tuple[int, int, int], tuple[int, int, int]]  # (perm, signs)

MIN_SHARED = 12  # "at least 12 beacons that both scanners detect"
MIN_SHARED_DISTANCES = comb(MIN_SHARED, 2)  # 66


def _parity(perm: tuple[int, ...]) -> int:
    """+1 for an even permutation, -1 for an odd one (count inversions)."""
    inversions = sum(1 for i, j in combinations(range(len(perm)), 2) if perm[i] > perm[j])
    return -1 if inversions % 2 else 1


def _rotations() -> list[Rotation]:
    """The 24 proper rotations: signed permutations whose determinant is +1.

    The determinant of a signed permutation matrix is parity(perm) times the
    product of the signs, so keep exactly the ones where those agree.  The
    identity is first, which is what scanner 0's frame uses.
    """
    result = []
    for perm in permutations(range(3)):
        for signs in [(sx, sy, sz) for sx in (1, -1) for sy in (1, -1) for sz in (1, -1)]:
            if _parity(perm) * signs[0] * signs[1] * signs[2] == 1:
                result.append((perm, signs))
    return result


ROTATIONS = _rotations()


def rotate(p: Point, rotation: Rotation) -> Point:
    (i, j, k), (sx, sy, sz) = rotation
    return (sx * p[i], sy * p[j], sz * p[k])


def fingerprint(beacons: list[Point]) -> Counter[int]:
    """Multiset of squared distances over every pair of beacons: rotation- and translation-invariant."""
    return Counter(
        (ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2
        for (ax, ay, az), (bx, by, bz) in combinations(beacons, 2)
    )


def could_overlap(fp_a: Counter[int], fp_b: Counter[int]) -> bool:
    """Necessary condition for 12 shared beacons: 66 shared pair distances."""
    return (fp_a & fp_b).total() >= MIN_SHARED_DISTANCES


def align(placed: list[Point], beacons: list[Point]) -> tuple[Point, list[Point]] | None:
    """Try to lock `beacons` (raw, own frame) onto `placed` (absolute frame).

    Returns (scanner position, beacons in the absolute frame), or None if no
    rotation gives an offset with >= 12 votes.
    """
    for rotation in ROTATIONS:
        turned = [rotate(b, rotation) for b in beacons]
        votes = Counter((ax - bx, ay - by, az - bz) for ax, ay, az in placed for bx, by, bz in turned)
        ((offset, count),) = votes.most_common(1)
        if count >= MIN_SHARED:
            dx, dy, dz = offset
            return offset, [(x + dx, y + dy, z + dz) for x, y, z in turned]
    return None


@dataclass(frozen=True)
class BeaconMap:
    scanners: tuple[Point, ...]  # scanner i's position in scanner 0's frame
    views: tuple[frozenset[Point], ...]  # scanner i's beacons, moved into scanner 0's frame
    beacons: frozenset[Point]  # the union of the views: every beacon, once


def parse_reports(raw: str) -> list[list[Point]]:
    """Split the input into per-scanner beacon lists, in scanner-number order."""
    reports: list[list[Point]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("---"):
            header = line.removeprefix("--- scanner ").removesuffix(" ---")
            if header != str(len(reports)):
                raise ValueError(f"expected scanner {len(reports)}, got {line!r}")
            reports.append([])
            continue
        if not reports:
            raise ValueError(f"beacon before any scanner header: {line!r}")
        coords = tuple(int(v) for v in line.split(","))
        if len(coords) != 3:
            raise ValueError(f"not an x,y,z beacon: {line!r}")
        reports[-1].append(coords)
    if not reports:
        raise ValueError("no scanners")
    for n, beacons in enumerate(reports):
        if len(set(beacons)) != len(beacons):
            raise ValueError(f"scanner {n} reports a beacon twice")
    return reports


def assemble(reports: list[list[Point]]) -> BeaconMap:
    """Lock every scanner into scanner 0's frame, breadth-first from scanner 0.

    Each newly placed scanner is tried, once, against every scanner not yet
    placed (prefiltered by fingerprint).  A scanner reachable through any
    chain of 12-beacon overlaps is found; one that isn't raises.
    """
    fingerprints = [fingerprint(beacons) for beacons in reports]
    positions: dict[int, Point] = {0: (0, 0, 0)}
    absolute: dict[int, list[Point]] = {0: reports[0]}
    frontier = deque([0])
    while frontier:
        a = frontier.popleft()
        for b in range(len(reports)):
            if b in positions or not could_overlap(fingerprints[a], fingerprints[b]):
                continue
            locked = align(absolute[a], reports[b])
            if locked is not None:
                positions[b], absolute[b] = locked
                frontier.append(b)
    if len(positions) != len(reports):
        missing = sorted(set(range(len(reports))) - positions.keys())
        raise ValueError(f"scanners {missing} never share 12 beacons with the rest")
    views = tuple(frozenset(absolute[n]) for n in range(len(reports)))
    return BeaconMap(
        scanners=tuple(positions[n] for n in range(len(reports))),
        views=views,
        beacons=frozenset().union(*views),
    )


def parse_input(raw: str) -> BeaconMap:
    return assemble(parse_reports(raw))


def part1(beacon_map: BeaconMap) -> int:
    return len(beacon_map.beacons)


def manhattan(a: Point, b: Point) -> int:
    return sum(abs(p - q) for p, q in zip(a, b, strict=True))


def part2(beacon_map: BeaconMap) -> int:
    return max((manhattan(a, b) for a, b in combinations(beacon_map.scanners, 2)), default=0)


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
