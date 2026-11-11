"""Day 21: Dirac Dice.

Two pawns on a circular 10-space track (spaces 1..10).  A turn rolls the die
three times, moves that many spaces clockwise, and adds the landing space to
the player's score.  The first player to reach the target score wins.

Part 1 uses a deterministic 100-sided die (1, 2, ..., 100, 1, ...) and a
target of 1000; the answer is losing score * total rolls.  The game is short
(a few hundred turns), so it is simulated literally.

Part 2 uses a quantum d3 and a target of 21: every roll splits the universe
three ways, and the answer is the larger of the two players' win counts.
The counts are ~10^14, so universes are counted, never enumerated.  Two
reductions make that cheap:

  * A turn's three rolls give 27 universes but only 7 distinct sums
    (3..9 with multiplicities 1, 3, 6, 7, 6, 3, 1).  What happens next
    depends only on the sum, so a turn branches 7 ways weighted by those
    multiplicities, not 27 ways.
  * The future depends only on (mover's position, mover's score, other's
    position, other's score): 10 * 21 * 10 * 21 = 44,100 states at most.
    Memoising wins(state) collapses the tree of universes into that table.

wins() is written from the mover's point of view and swaps roles on each
call, so one function serves both players.

Positions are stored 1-based, as the statement words them.  Moving is
(pos - 1 + steps) % 10 + 1: shift to 0..9, wrap, shift back.
"""

from collections import Counter
from functools import cache
from itertools import count, product
from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day21.txt"

TRACK = 10


class Start(NamedTuple):
    """Starting spaces (1..10) of player 1 and player 2."""

    p1: int
    p2: int


def parse_input(raw: str) -> Start:
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if len(lines) != 2:
        raise ValueError(f"expected 2 player lines, got {len(lines)}")
    spaces = []
    for player, line in enumerate(lines, start=1):
        prefix = f"Player {player} starting position:"
        if not line.startswith(prefix):
            raise ValueError(f"expected {prefix!r}, got {line!r}")
        space = int(line.removeprefix(prefix))
        if not 1 <= space <= TRACK:
            raise ValueError(f"player {player} starts off the track: {space}")
        spaces.append(space)
    return Start(*spaces)


def advance(pos: int, steps: int) -> int:
    """Space reached from `pos` after `steps` clockwise moves (1..10, wrapping)."""
    return (pos - 1 + steps) % TRACK + 1


def deterministic_die(sides: int = 100):
    """1, 2, ..., sides, 1, 2, ... forever."""
    for n in count():
        yield n % sides + 1


def play_deterministic(start: Start, target: int = 1000) -> tuple[int, int]:
    """Play with the deterministic d100; return (losing score, number of rolls)."""
    die = deterministic_die()
    pos = [start.p1, start.p2]
    score = [0, 0]
    rolls = 0
    player = 0
    while True:
        steps = next(die) + next(die) + next(die)
        rolls += 3
        pos[player] = advance(pos[player], steps)
        score[player] += pos[player]
        if score[player] >= target:
            return score[1 - player], rolls
        player = 1 - player


# Sum of three d3 rolls -> number of the 27 roll sequences giving it.
DIRAC_SUMS = tuple(sorted(Counter(map(sum, product((1, 2, 3), repeat=3))).items()))


def make_wins(target: int):
    """A fresh memoised wins(pos, score, other_pos, other_score) for one target.

    Built per call rather than as one module-level @cache, so repeated calls
    (bench.py runs part 2 five times) each do the real work, and different
    targets never share a table.
    """

    @cache
    def wins(pos: int, score: int, other_pos: int, other_score: int) -> tuple[int, int]:
        """Universes in which (the player about to move, the other player) win from this state."""
        mine = theirs = 0
        for steps, ways in DIRAC_SUMS:
            new_pos = advance(pos, steps)
            new_score = score + new_pos
            if new_score >= target:
                mine += ways
            else:
                # The other player moves next, so the recursive call's roles are swapped.
                their_wins, my_wins = wins(other_pos, other_score, new_pos, new_score)
                mine += ways * my_wins
                theirs += ways * their_wins
        return mine, theirs

    return wins


def dirac_wins(start: Start, target: int = 21) -> tuple[int, int]:
    """Universes won by (player 1, player 2) with the quantum d3."""
    return make_wins(target)(start.p1, 0, start.p2, 0)


def part1(start: Start) -> int:
    loser, rolls = play_deterministic(start)
    return loser * rolls


def part2(start: Start) -> int:
    return max(dirac_wins(start))


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
