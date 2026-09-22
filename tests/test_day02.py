"""Day 2: Dive!."""

import random

import pytest

import day02

LOCKED = (2070300, 2078985210)

EXAMPLE = "forward 5\ndown 5\nforward 8\nup 3\ndown 8\nforward 2\n"
MOVES = [(5, 0), (0, 5), (8, 0), (0, -3), (0, 8), (2, 0)]


def follow_course(moves):
    """Part 1 exactly as the statement walks it: one command at a time,
    yielding (horizontal, depth) after each."""
    horizontal = depth = 0
    for forward, dive in moves:
        horizontal += forward
        depth += dive
        yield horizontal, depth


def steer_by_the_manual(raw):
    """Part 2 exactly as the statement words it, straight from the command
    text: three separate branches, yielding (horizontal, depth, aim) after
    each command."""
    horizontal = depth = aim = 0
    for line in raw.splitlines():
        command, amount = line.split()
        x = int(amount)
        if command == "down":
            aim += x
        elif command == "up":
            aim -= x
        else:
            horizontal += x
            depth += aim * x
        yield horizontal, depth, aim


def random_course(rng, length):
    commands = ["forward", "down", "up"]
    return "".join(f"{rng.choice(commands)} {rng.randint(1, 9)}\n" for _ in range(length))


def test_parse_input():
    assert day02.parse_input(EXAMPLE) == MOVES


def test_part1_example():
    assert day02.part1(MOVES) == 150


def test_part2_example():
    assert day02.steer(MOVES) == (15, 60, 10)
    assert day02.part2(MOVES) == 900


def test_part2_example_running_totals():
    """Anchor the by-the-manual reference to the statement's narration:
    aim 5, depth +40, aim 2, aim 10, depth +20 to 60."""
    assert list(steer_by_the_manual(EXAMPLE)) == [
        (5, 0, 0),
        (5, 0, 5),
        (13, 40, 5),
        (13, 40, 2),
        (13, 40, 10),
        (15, 60, 10),
    ]


def test_steer_matches_the_manual():
    """steer runs both updates on every move instead of branching, relying on
    each (forward, dive) pair having a zero in it.  Check it against the
    three-branch version, aim going negative included."""
    rng = random.Random(2021)
    for length in range(1, 40):
        raw = random_course(rng, length)
        *_, expected = steer_by_the_manual(raw)
        assert day02.steer(day02.parse_input(raw)) == expected


def test_part2_aim_is_part1_depth():
    """down/up do to part 2's aim exactly what they did to part 1's depth, so
    the two finish equal -- and horizontal is the same in both readings."""
    rng = random.Random(1202)
    for length in range(1, 40):
        moves = day02.parse_input(random_course(rng, length))
        horizontal, _, aim = day02.steer(moves)
        assert horizontal * aim == day02.part1(moves)


def test_part2_depends_on_order():
    """Unlike part 1, part 2 cannot be column sums: the same commands in a
    different order land somewhere else."""
    aim_first = day02.parse_input("down 5\nforward 8\n")
    forward_first = day02.parse_input("forward 8\ndown 5\n")
    assert day02.part1(aim_first) == day02.part1(forward_first) == 40
    assert day02.part2(aim_first) == 8 * 40
    assert day02.part2(forward_first) == 0


def test_example_running_totals():
    """The statement narrates the position after every command; check the
    step-by-step reference against that so the test below is anchored."""
    assert list(follow_course(MOVES)) == [(5, 0), (5, 5), (13, 5), (13, 2), (13, 10), (15, 10)]


def test_column_sums_match_step_by_step():
    """part1 never walks the course: it sums each column.  That is only
    valid because part 1's commands are independent additions, so check it
    against the literal walk, including courses that surface above depth 0."""
    rng = random.Random(2021)
    for length in range(1, 40):
        amounts = [rng.randint(1, 9) for _ in range(length)]
        moves = [rng.choice([(x, 0), (0, x), (0, -x)]) for x in amounts]
        *_, (horizontal, depth) = follow_course(moves)
        assert day02.part1(moves) == horizontal * depth


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("", 0),
        ("forward 7\n", 0),  # moved, never dived: 7 * 0
        ("down 7\n", 0),  # dived, never moved: 0 * 7
        ("forward 3\ndown 4\n", 12),
        ("forward 3\ndown 4\nup 4\n", 0),  # back at the surface
        ("forward 3\nup 4\n", -12),  # the statement does not forbid depth < 0
    ],
)
def test_part1_edges(raw, expected):
    assert day02.part1(day02.parse_input(raw)) == expected


def test_unknown_command_is_an_error():
    with pytest.raises(ValueError, match="unknown command"):
        day02.parse_input("forward 1\nsideways 2\n")


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day02.parse_input(crlf) == MOVES
    assert day02.solve(crlf) == (150, 900)


def test_real_input_locked(check_locked):
    check_locked(day02, LOCKED)
