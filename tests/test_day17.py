"""Day 17: Trick Shot."""

import pytest

import day17
from day17 import Target

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (3655, 1447)

EXAMPLE = "target area: x=20..30, y=-10..-5"


def simulate(vx, vy, target, steps=1000):
    """Literal reference: step the probe exactly as the statement describes; True if it is ever inside."""
    x = y = 0
    for _ in range(steps):
        x += vx
        y += vy
        vx -= (vx > 0) - (vx < 0)
        vy -= 1
        if target.x_min <= x <= target.x_max and target.y_min <= y <= target.y_max:
            return True
        if (y < target.y_min and vy < 0) or (x > target.x_max and vx >= 0) or (x < target.x_min and vx <= 0):
            return False  # moving away from the band on some axis, and never turning back
    raise AssertionError(f"({vx}, {vy}) still undecided after {steps} steps")


def brute_hits(target, pad=50):
    """Every hitting launch in a box well beyond the bounds hits() assumes, negative vx included."""
    return {
        (vx, vy)
        for vx in range(-pad, target.x_max + pad)
        for vy in range(target.y_min - pad, -target.y_min + pad)
        if simulate(vx, vy, target)
    }


def test_parse_example():
    assert day17.parse_target(EXAMPLE) == Target(20, 30, -10, -5)


@pytest.mark.parametrize(
    ("velocity", "hit"), [((7, 2), True), ((6, 3), True), ((9, 0), True), ((17, -4), False)]
)
def test_statement_trajectories(velocity, hit):
    target = day17.parse_target(EXAMPLE)
    assert (velocity in day17.hits(target)) == hit
    assert simulate(*velocity, target) == hit


def test_17_minus_4_passes_through_between_steps():
    """The statement's miss: steps land at x=17 (above the band) then x=33 (past it) -- no step inside."""
    assert day17.x_steps(17, day17.parse_target(EXAMPLE), 10) == set()


def test_part1_example():
    target = day17.parse_target(EXAMPLE)
    assert day17.part1(day17.hits(target)) == 45
    assert (6, 9) in day17.hits(target)


@pytest.mark.parametrize(
    "target",
    [
        Target(20, 30, -10, -5),
        Target(1, 1, -1, -1),
        Target(5, 5, -3, -3),  # x=5 is no triangular number: nothing can stall in it
        Target(10, 12, -4, -2),
        Target(3, 40, -20, -1),
    ],
)
def test_hits_matches_brute_force(target):
    """Same set as a literal simulation over a padded box -- which also pins the vx/vy search bounds."""
    assert set(day17.hits(target)) == brute_hits(target)


def test_hits_matches_brute_force_real(real_input):
    target = day17.parse_target(real_input(17))
    assert set(day17.hits(target)) == brute_hits(target, pad=20)


@pytest.mark.parametrize("vy", range(-5, 30))
def test_apex_matches_simulation(vy):
    y, peak = 0, 0
    for _ in range(100):
        y += vy
        vy -= 1
        peak = max(peak, y)
    assert day17.apex(vy + 100) == peak


def has_stall_in_band(target):
    """True if some vx comes to rest inside the x band, i.e. a triangular number n(n+1)/2 lies in it."""
    return any(target.x_min <= n * (n + 1) // 2 <= target.x_max for n in range(1, target.x_max + 1))


@pytest.mark.parametrize(
    "target",
    [Target(20, 30, -10, -5), Target(10, 12, -4, -2), Target(3, 40, -20, -1), Target(5, 5, -3, -3)],
)
def test_part1_closed_form(target):
    """The shortcut: if a vx can stall in the band, the answer is apex(-y_min - 1) = y_min*(y_min+1)/2.

    The fastest upward shot returns through y=0 at speed -(vy+1) and lands on y_min next step; a stalled
    vx keeps x in range however long that takes.  Without a stall the shortcut can be wrong.
    """
    closed = target.y_min * (target.y_min + 1) // 2
    if has_stall_in_band(target):
        assert day17.part1(day17.hits(target)) == closed
    else:
        assert day17.part1(day17.hits(target)) < closed


def test_part1_closed_form_real(real_input):
    target = day17.parse_target(real_input(17))
    assert has_stall_in_band(target)  # 20*21/2 = 210 is in 209..238
    assert day17.part1(day17.hits(target)) == target.y_min * (target.y_min + 1) // 2


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "target area: x=20..30",
        "target area: x=30..20, y=-10..-5",  # reversed range
        "target area: x=20..30, y=-5..-10",
        "target area: x=-30..-20, y=-10..-5",  # left of the origin
        "target area: x=0..30, y=-10..-5",
        "target area: x=20..30, y=-10..5",  # straddles y=0
        "target area: x=20..30, y=5..10",
    ],
)
def test_malformed_input_is_an_error(bad):
    with pytest.raises(ValueError):
        day17.parse_target(bad)


# The statement's 112 part 2 velocities, verbatim.
PART2_LISTING = """
23,-10  25,-9   27,-5   29,-6   22,-6   21,-7   9,0     27,-7   24,-5
25,-7   26,-6   25,-5   6,8     11,-2   20,-5   29,-10  6,3     28,-7
8,0     30,-6   29,-8   20,-10  6,7     6,4     6,1     14,-4   21,-6
26,-10  7,-1    7,7     8,-1    21,-9   6,2     20,-7   30,-10  14,-3
20,-8   13,-2   7,3     28,-8   29,-9   15,-3   22,-5   26,-8   25,-8
25,-6   15,-4   9,-2    15,-2   12,-2   28,-9   12,-3   24,-6   23,-7
25,-10  7,8     11,-3   26,-7   7,1     23,-9   6,0     22,-10  27,-6
8,1     22,-8   13,-4   7,6     28,-6   11,-4   12,-4   26,-9   7,4
24,-10  23,-8   30,-8   7,0     9,-1    10,-1   26,-5   22,-9   6,5
7,5     23,-6   28,-10  10,-2   11,-1   20,-9   14,-2   29,-7   13,-3
23,-5   24,-8   27,-9   30,-7   28,-5   21,-10  7,9     6,6     21,-5
27,-10  7,2     30,-9   21,-8   22,-7   24,-9   20,-6   6,9     29,-5
8,-2    27,-8   30,-5   24,-7
"""


def test_part2_example():
    listed = [tuple(map(int, pair.split(","))) for pair in PART2_LISTING.split()]
    assert len(listed) == len(set(listed)) == 112
    shots = day17.parse_input(EXAMPLE)
    assert day17.part2(shots) == 112
    assert set(shots) == set(listed)


def test_hits_has_no_duplicates(real_input):
    """part2 is len(), so the list must not repeat a velocity."""
    for raw in [EXAMPLE, real_input(17)]:
        shots = day17.parse_input(raw)
        assert len(shots) == len(set(shots))


def test_part2_matches_brute_force_real(real_input):
    assert day17.part2(day17.parse_input(real_input(17))) == len(
        brute_hits(day17.parse_target(real_input(17)), pad=20)
    )


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    assert day17.parse_target(EXAMPLE + "\r\n") == Target(20, 30, -10, -5)
    assert day17.part1(day17.parse_input(EXAMPLE + "\r\n")) == 45
    assert day17.part2(day17.parse_input(EXAMPLE + "\r\n")) == 112


def test_real_input_locked(check_locked):
    check_locked(day17, LOCKED)
