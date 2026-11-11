"""Day 21: Dirac Dice."""

from collections import Counter

import pytest

import day21
from day21 import Start

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (853776, 301304993766094)

EXAMPLE = """\
Player 1 starting position: 4
Player 2 starting position: 8
"""


def test_parse_example():
    assert day21.parse_input(EXAMPLE) == Start(4, 8)


@pytest.mark.parametrize(
    ("pos", "steps", "want"),
    [
        (7, 5, 2),  # statement: 7 -> 8, 9, 10, 1, 2
        (4, 6, 10),  # lands exactly on 10, not 0
        (10, 1, 1),
        (1, 10, 1),  # a full lap
        (8, 15, 3),  # statement: player 2's first move
    ],
)
def test_advance(pos, steps, want):
    assert day21.advance(pos, steps) == want


def test_die_wraps_after_100():
    die = day21.deterministic_die()
    rolls = [next(die) for _ in range(202)]
    assert rolls[:3] == [1, 2, 3]
    assert rolls[99:102] == [100, 1, 2]
    assert rolls[199:202] == [100, 1, 2]


def first_turns(start, n):
    """(position, score) after each of the first n turns, alternating players."""
    die = day21.deterministic_die()
    pos, score, out = [start.p1, start.p2], [0, 0], []
    for turn in range(n):
        p = turn % 2
        pos[p] = day21.advance(pos[p], next(die) + next(die) + next(die))
        score[p] += pos[p]
        out.append((pos[p], score[p]))
    return out


def test_statement_opening_turns():
    """The eight turns the statement lists before '...after many turns...'."""
    assert first_turns(Start(4, 8), 8) == [
        (10, 10),
        (3, 3),
        (4, 14),
        (6, 9),
        (6, 20),
        (7, 16),
        (6, 26),
        (6, 22),
    ]


def test_example_game_end():
    """Statement: player 1 reaches 1000 on roll 993; player 2 has 745."""
    assert day21.play_deterministic(Start(4, 8)) == (745, 993)


def test_part1_example():
    assert day21.part1(day21.parse_input(EXAMPLE)) == 739785


def test_player2_can_win():
    """Loser index must flip when player 2 is the winner, not always report player 2."""
    loser, rolls = day21.play_deterministic(Start(1, 1), target=10)
    # P1: 1+2+3=6 -> 7 (7).  P2: 4+5+6=15 -> 6 (6).  P1: 7+8+9=24 -> 1 (8).
    # P2: 10+11+12=33 -> 9 (15): player 2 wins on roll 12 with player 1 on 8.
    assert (loser, rolls) == (8, 12)


def test_dirac_sums():
    """27 roll sequences collapse to 7 sums: the multiplicities are the coefficients of (x + x^2 + x^3)^3."""
    assert day21.DIRAC_SUMS == ((3, 1), (4, 3), (5, 6), (6, 7), (7, 6), (8, 3), (9, 1))
    assert sum(ways for _, ways in day21.DIRAC_SUMS) == 27


def test_part2_example():
    assert day21.dirac_wins(Start(4, 8)) == (444356092776315, 341960390180808)
    assert day21.part2(day21.parse_input(EXAMPLE)) == 444356092776315


def literal_dirac(start, target):
    """Reference: every single roll splits three ways, no merging of sums, no memo.

    Exponential, so only for small targets.  Returns (player 1 wins, player 2 wins).
    """
    wins = [0, 0]

    def turn(pos, score, player, rolled, steps):
        if rolled < 3:
            for face in (1, 2, 3):
                turn(pos, score, player, rolled + 1, steps + face)
            return
        pos, score = list(pos), list(score)
        pos[player] = day21.advance(pos[player], steps)
        score[player] += pos[player]
        if score[player] >= target:
            wins[player] += 1
        else:
            turn(pos, score, 1 - player, 0, 0)

    turn((start.p1, start.p2), (0, 0), 0, 0, 0)
    return tuple(wins)


def forward_dirac(start, target):
    """Reference: push universe counts forward turn by turn, splitting each roll three ways.

    A different shape from wins() (breadth-first over turns, absolute player
    roles, 27-way splits rebuilt from single rolls) that is still fast enough for target 21.
    """
    live = Counter({(start.p1, 0, start.p2, 0): 1})  # (mover pos, mover score, other pos, other score)
    wins = [0, 0]
    player = 0
    while live:
        nxt = Counter()
        for (pos, score, other_pos, other_score), n in live.items():
            for a in (1, 2, 3):
                for b in (1, 2, 3):
                    for c in (1, 2, 3):
                        new_pos = day21.advance(pos, a + b + c)
                        new_score = score + new_pos
                        if new_score >= target:
                            wins[player] += n
                        else:
                            nxt[other_pos, other_score, new_pos, new_score] += n
        live = nxt
        player = 1 - player
    return tuple(wins)


@pytest.mark.parametrize("target", [1, 2, 4, 6, 8])
@pytest.mark.parametrize("start", [Start(4, 8), Start(1, 1), Start(10, 3), Start(6, 10)])
def test_dirac_matches_literal_reference(start, target):
    assert day21.dirac_wins(start, target) == literal_dirac(start, target)


@pytest.mark.parametrize("start", [Start(4, 8), Start(1, 10), Start(7, 7)])
def test_dirac_matches_forward_reference(start):
    assert day21.dirac_wins(start) == forward_dirac(start, 21)


def test_part2_matches_forward_reference_real(real_input):
    start = day21.parse_input(real_input(21))
    wins = forward_dirac(start, 21)
    assert day21.dirac_wins(start) == wins
    assert day21.part2(start) == max(wins)


def test_state_table_is_bounded():
    """Memo keys are (pos, score < 21, pos, score < 21): at most 10 * 21 * 10 * 21 = 44,100.

    The example actually reaches 17,512 of them.
    """
    wins = day21.make_wins(21)
    wins(4, 0, 8, 0)
    assert wins.cache_info().currsize == 17512 <= 10 * 21 * 10 * 21


def test_fresh_table_per_call():
    """dirac_wins builds a new memo each call, so repeated calls (bench reps) do real work."""
    assert day21.make_wins(21) is not day21.make_wins(21)
    assert day21.dirac_wins(Start(4, 8), 10) != day21.dirac_wins(Start(4, 8), 21)


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "Player 1 starting position: 4\n",
        "Player 1 starting position: 4\nPlayer 2 starting position: 11\n",
        "Player 1 starting position: 0\nPlayer 2 starting position: 8\n",
        "Player 2 starting position: 4\nPlayer 1 starting position: 8\n",
    ],
)
def test_malformed_input_is_an_error(bad):
    with pytest.raises(ValueError):
        day21.parse_input(bad)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day21.parse_input(crlf) == Start(4, 8)
    assert day21.part1(day21.parse_input(crlf)) == 739785
    assert day21.part2(day21.parse_input(crlf)) == 444356092776315


def test_real_input_locked(check_locked):
    check_locked(day21, LOCKED)
