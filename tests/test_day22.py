"""Day 22: Reactor Reboot."""

import random

import pytest

import day22
from day22 import Cuboid, Step

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (587097, 1359673068597669)

SMALL = """\
on x=10..12,y=10..12,z=10..12
on x=11..13,y=11..13,z=11..13
off x=9..11,y=9..11,z=9..11
on x=10..10,y=10..10,z=10..10
"""

LARGER = """\
on x=-20..26,y=-36..17,z=-47..7
on x=-20..33,y=-21..23,z=-26..28
on x=-22..28,y=-29..23,z=-38..16
on x=-46..7,y=-6..46,z=-50..-1
on x=-49..1,y=-3..46,z=-24..28
on x=2..47,y=-22..22,z=-23..27
on x=-27..23,y=-28..26,z=-21..29
on x=-39..5,y=-6..47,z=-3..44
on x=-30..21,y=-8..43,z=-13..34
on x=-22..26,y=-27..20,z=-29..19
off x=-48..-32,y=26..41,z=-47..-37
on x=-12..35,y=6..50,z=-50..-2
off x=-48..-32,y=-32..-16,z=-15..-5
on x=-18..26,y=-33..15,z=-7..46
off x=-40..-22,y=-38..-28,z=23..41
on x=-16..35,y=-41..10,z=-47..6
off x=-32..-23,y=11..30,z=-14..3
on x=-49..-5,y=-3..45,z=-29..18
off x=18..30,y=-20..-8,z=-3..13
on x=-41..9,y=-7..43,z=-33..15
on x=-54112..-39298,y=-85059..-49293,z=-27449..7877
on x=967..23432,y=45373..81175,z=27513..53682
"""

PART2 = """\
on x=-5..47,y=-31..22,z=-19..33
on x=-44..5,y=-27..21,z=-14..35
on x=-49..-1,y=-11..42,z=-10..38
on x=-20..34,y=-40..6,z=-44..1
off x=26..39,y=40..50,z=-2..11
on x=-41..5,y=-41..6,z=-36..8
off x=-43..-33,y=-45..-28,z=7..25
on x=-33..15,y=-32..19,z=-34..11
off x=35..47,y=-46..-34,z=-11..5
on x=-14..36,y=-6..44,z=-16..29
on x=-57795..-6158,y=29564..72030,z=20435..90618
on x=36731..105352,y=-21140..28532,z=16094..90401
on x=30999..107136,y=-53464..15513,z=8553..71215
on x=13528..83982,y=-99403..-27377,z=-24141..23996
on x=-72682..-12347,y=18159..111354,z=7391..80950
on x=-1060..80757,y=-65301..-20884,z=-103788..-16709
on x=-83015..-9461,y=-72160..-8347,z=-81239..-26856
on x=-52752..22273,y=-49450..9096,z=54442..119054
on x=-29982..40483,y=-108474..-28371,z=-24328..38471
on x=-4958..62750,y=40422..118853,z=-7672..65583
on x=55694..108686,y=-43367..46958,z=-26781..48729
on x=-98497..-18186,y=-63569..3412,z=1232..88485
on x=-726..56291,y=-62629..13224,z=18033..85226
on x=-110886..-34664,y=-81338..-8658,z=8914..63723
on x=-55829..24974,y=-16897..54165,z=-121762..-28058
on x=-65152..-11147,y=22489..91432,z=-58782..1780
on x=-120100..-32970,y=-46592..27473,z=-11695..61039
on x=-18631..37533,y=-124565..-50804,z=-35667..28308
on x=-57817..18248,y=49321..117703,z=5745..55881
on x=14781..98692,y=-1341..70827,z=15753..70151
on x=-34419..55919,y=-19626..40991,z=39015..114138
on x=-60785..11593,y=-56135..2999,z=-95368..-26915
on x=-32178..58085,y=17647..101866,z=-91405..-8878
on x=-53655..12091,y=50097..105568,z=-75335..-4862
on x=-111166..-40997,y=-71714..2688,z=5609..50954
on x=-16602..70118,y=-98693..-44401,z=5197..76897
on x=16383..101554,y=4615..83635,z=-44907..18747
off x=-95822..-15171,y=-19987..48940,z=10804..104439
on x=-89813..-14614,y=16069..88491,z=-3297..45228
on x=41075..99376,y=-20427..49978,z=-52012..13762
on x=-21330..50085,y=-17944..62733,z=-112280..-30197
on x=-16478..35915,y=36008..118594,z=-7885..47086
off x=-98156..-27851,y=-49952..43171,z=-99005..-8456
off x=2032..69770,y=-71013..4824,z=7471..94418
on x=43670..120875,y=-42068..12382,z=-24787..38892
off x=37514..111226,y=-45862..25743,z=-16714..54663
off x=25699..97951,y=-30668..59918,z=-15349..69697
off x=-44271..17935,y=-9516..60759,z=49131..112598
on x=-61695..-5813,y=40978..94975,z=8655..80240
off x=-101086..-9439,y=-7088..67543,z=33935..83858
off x=18020..114017,y=-48931..32606,z=21474..89843
off x=-77139..10506,y=-89994..-18797,z=-80..59318
off x=8476..79288,y=-75520..11602,z=-96624..-24783
on x=-47488..-1262,y=24338..100707,z=16292..72967
off x=-84341..13987,y=2429..92914,z=-90671..-1318
off x=-37810..49457,y=-71013..-7894,z=-105357..-13188
off x=-27365..46395,y=31009..98017,z=15428..76570
off x=-70369..-16548,y=22648..78696,z=-1892..86821
on x=-53470..21291,y=-120233..-33476,z=-44150..38147
off x=-93533..-4276,y=-16170..68771,z=-104985..-24507
"""


def test_parse_small():
    assert day22.parse_input(SMALL) == [
        Step(True, Cuboid(10, 12, 10, 12, 10, 12)),
        Step(True, Cuboid(11, 13, 11, 13, 11, 13)),
        Step(False, Cuboid(9, 11, 9, 11, 9, 11)),
        Step(True, Cuboid(10, 10, 10, 10, 10, 10)),
    ]


def test_parse_negative_ranges():
    (step,) = day22.parse_input("off x=-48..-32,y=26..41,z=-47..-37\n")
    assert step == Step(False, Cuboid(-48, -32, 26, 41, -47, -37))


@pytest.mark.parametrize(
    ("k", "want"),
    [
        (1, 27),  # statement: a 3x3x3 cuboid
        (2, 27 + 19),  # statement: "only 19 additional cubes turn on"
        (3, 27 + 19 - 8),  # statement: "ultimately turning off 8 cubes"
        (4, 39),  # statement: one cube back on
    ],
)
def test_small_example_step_by_step(k, want):
    assert day22.count_on(day22.parse_input(SMALL)[:k]) == want


def test_part1_small_example():
    assert day22.part1(day22.parse_input(SMALL)) == 39


def test_part1_larger_example():
    assert day22.part1(day22.parse_input(LARGER)) == 590784


def test_larger_example_last_two_steps_are_outside_region():
    """Statement: the last two steps lie fully outside -50..50; all others fully inside."""
    steps = day22.parse_input(LARGER)
    for step in steps[:-2]:
        assert step.box.intersect(day22.INIT_REGION) == step.box
    for step in steps[-2:]:
        assert step.box.intersect(day22.INIT_REGION) is None


@pytest.mark.parametrize(
    ("a", "b", "want"),
    [
        (Cuboid(0, 2, 0, 2, 0, 2), Cuboid(1, 3, 1, 3, 1, 3), Cuboid(1, 2, 1, 2, 1, 2)),
        (Cuboid(0, 2, 0, 2, 0, 2), Cuboid(2, 5, 2, 5, 2, 5), Cuboid(2, 2, 2, 2, 2, 2)),  # one shared cube
        (Cuboid(0, 2, 0, 2, 0, 2), Cuboid(3, 5, 0, 2, 0, 2), None),  # adjacent on x, no overlap
        (Cuboid(0, 9, 0, 9, 0, 9), Cuboid(3, 4, 5, 6, 7, 8), Cuboid(3, 4, 5, 6, 7, 8)),  # containment
        (Cuboid(0, 9, 0, 9, 0, 9), Cuboid(0, 9, 0, 9, 10, 12), None),  # disjoint on z only
    ],
)
def test_intersect(a, b, want):
    assert a.intersect(b) == want
    assert b.intersect(a) == want


def test_volume_is_inclusive():
    assert Cuboid(10, 10, 10, 10, 10, 10).volume() == 1
    assert Cuboid(10, 12, 10, 12, 10, 12).volume() == 27
    assert Cuboid(-50, 50, -50, 50, -50, 50).volume() == 101**3


def test_part2_example():
    assert day22.part2(day22.parse_input(PART2)) == 2758514936282235


def test_part2_example_in_region():
    """Statement: 474140 of the part 2 example's on cubes lie in the initialisation region."""
    assert day22.part1(day22.parse_input(PART2)) == 474140


def test_part2_on_part1_examples():
    """The larger part 1 example has two huge steps outside the region; part 2 must count them."""
    steps = day22.parse_input(LARGER)
    outside = sum(s.box.volume() for s in steps[-2:])
    assert day22.part2(steps) == 590784 + outside
    assert day22.part2(day22.parse_input(SMALL)) == 39


def disjoint_count(steps):
    """Reference: keep the on-set as disjoint cuboids, carving each new step's box out of them.

    A different shape from count_on's signed inclusion-exclusion: nothing
    ever carries a negative sign, and every cube on is in exactly one box.
    """

    def carve(a, c):
        """Pieces of a not in c (up to six), as disjoint cuboids."""
        if a.intersect(c) is None:
            return [a]
        pieces = []
        x0, x1, y0, y1, z0, z1 = a
        if x0 < c.x0:
            pieces.append(Cuboid(x0, c.x0 - 1, y0, y1, z0, z1))
            x0 = c.x0
        if x1 > c.x1:
            pieces.append(Cuboid(c.x1 + 1, x1, y0, y1, z0, z1))
            x1 = c.x1
        if y0 < c.y0:
            pieces.append(Cuboid(x0, x1, y0, c.y0 - 1, z0, z1))
            y0 = c.y0
        if y1 > c.y1:
            pieces.append(Cuboid(x0, x1, c.y1 + 1, y1, z0, z1))
            y1 = c.y1
        if z0 < c.z0:
            pieces.append(Cuboid(x0, x1, y0, y1, z0, c.z0 - 1))
        if z1 > c.z1:
            pieces.append(Cuboid(x0, x1, y0, y1, c.z1 + 1, z1))
        return pieces

    boxes = []
    for step in steps:
        boxes = [piece for b in boxes for piece in carve(b, step.box)]
        if step.on:
            boxes.append(step.box)
    return sum(b.volume() for b in boxes)


def test_disjoint_reference_agrees_on_examples():
    assert disjoint_count(day22.parse_input(PART2)) == 2758514936282235
    assert disjoint_count(day22.parse_input(SMALL)) == 39


@pytest.mark.parametrize("seed", range(30))
def test_disjoint_reference_matches_literal(seed):
    rng = random.Random(2000 + seed)
    steps = random_steps(rng, 12, -6, 6)
    assert disjoint_count(steps) == literal_count(steps, Cuboid(-6, 6, -6, 6, -6, 6))


def test_part2_matches_disjoint_reference_real(real_input):
    steps = day22.parse_input(real_input(22))
    assert day22.part2(steps) == disjoint_count(steps)


def literal_count(steps, region):
    """Reference: a set of every on cube, step by step, restricted to `region`."""
    on = set()
    for step in steps:
        box = step.box.intersect(region)
        if box is None:
            continue
        cubes = {
            (x, y, z)
            for x in range(box.x0, box.x1 + 1)
            for y in range(box.y0, box.y1 + 1)
            for z in range(box.z0, box.z1 + 1)
        }
        if step.on:
            on |= cubes
        else:
            on -= cubes
    return len(on)


def random_steps(rng, n, lo, hi):
    steps = []
    for _ in range(n):
        ranges = []
        for _ in range(3):
            a, b = sorted(rng.randint(lo, hi) for _ in range(2))
            ranges += [a, b]
        steps.append(Step(rng.random() < 0.6, Cuboid(*ranges)))
    return steps


@pytest.mark.parametrize("seed", range(30))
def test_count_on_matches_literal_reference(seed):
    """Unclipped count, on random overlapping steps small enough to enumerate."""
    rng = random.Random(seed)
    steps = random_steps(rng, 12, -6, 6)
    everywhere = Cuboid(-6, 6, -6, 6, -6, 6)
    assert day22.count_on(steps) == literal_count(steps, everywhere)


@pytest.mark.parametrize("seed", range(30))
def test_clipping_matches_literal_reference(seed):
    """Steps straddle the region boundary; clipping each step first must give the same in-region count."""
    rng = random.Random(1000 + seed)
    steps = random_steps(rng, 12, -10, 10)
    region = Cuboid(-4, 3, -2, 5, -5, 1)
    assert day22.count_on(steps, region) == literal_count(steps, region)


def test_repeated_steps_do_not_blow_up():
    """Equal boxes merge in the Counter: re-applying one step leaves a single entry, not 2^n."""
    box = Cuboid(0, 4, 0, 4, 0, 4)
    steps = [Step(True, box)] * 50
    assert day22.count_on(steps) == 125


def grid_count(steps, limit):
    """Reference for the real input: a bytearray per (x, y) column, z ranges set by slice."""
    width = 2 * limit + 1
    columns = [[bytearray(width) for _ in range(width)] for _ in range(width)]
    region = Cuboid(-limit, limit, -limit, limit, -limit, limit)
    for step in steps:
        box = step.box.intersect(region)
        if box is None:
            continue
        fill = bytes([1 if step.on else 0]) * (box.z1 - box.z0 + 1)
        for x in range(box.x0, box.x1 + 1):
            plane = columns[x + limit]
            for y in range(box.y0, box.y1 + 1):
                plane[y + limit][box.z0 + limit : box.z1 + limit + 1] = fill
    return sum(sum(col) for plane in columns for col in plane)


def test_grid_reference_agrees_on_larger_example():
    assert grid_count(day22.parse_input(LARGER), 50) == 590784


def test_part1_matches_grid_reference_real(real_input):
    steps = day22.parse_input(real_input(22))
    assert day22.part1(steps) == grid_count(steps, day22.INIT_LIMIT)


@pytest.mark.parametrize(
    "bad",
    [
        "toggle x=1..2,y=1..2,z=1..2",
        "on x=1..2,y=1..2",
        "on x=1..2,y=1..2,z=1..2,w=1..2",
        "on x=3..2,y=1..2,z=1..2",  # lo > hi
        "on x=1..2,y=1..2,z=a..2",
    ],
)
def test_malformed_input_is_an_error(bad):
    with pytest.raises(ValueError):
        day22.parse_input(bad)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = LARGER.replace("\n", "\r\n")
    assert day22.parse_input(crlf) == day22.parse_input(LARGER)
    assert day22.part1(day22.parse_input(crlf)) == 590784
    crlf2 = PART2.replace("\n", "\r\n")
    assert day22.part2(day22.parse_input(crlf2)) == 2758514936282235


def test_real_input_locked(check_locked):
    check_locked(day22, LOCKED)
