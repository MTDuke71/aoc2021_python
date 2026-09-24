"""Day 4: Giant Squid.

Input is one comma-separated line of draws, then 5x5 bingo boards separated
by blank lines.

Nothing is simulated.  Each number's draw turn is known up front, so a line
completes on the turn of its latest-drawn cell, and a board wins on the
earliest turn any of its ten lines completes.  Both parts then just pick a
board by that turn: part 1 the earliest, part 2 the latest.
"""

from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day04.txt"

SIZE = 5

Board = tuple[tuple[int, ...], ...]


class Game(NamedTuple):
    draws: list[int]
    boards: list[Board]


class Win(NamedTuple):
    """When a board wins and what it scores then."""

    turn: int  # index into draws of the number that completed a line
    score: int  # sum of unmarked cells * that number


def read_game(raw: str) -> Game:
    """The text as written: draws and boards, validated, nothing derived."""
    lines = [line.strip() for line in raw.splitlines()]
    lines = [line for line in lines if line]
    if not lines:
        raise ValueError("empty input")
    draws = [int(x) for x in lines[0].split(",")]
    rows = lines[1:]
    if not rows or len(rows) % SIZE:
        raise ValueError(f"{len(rows)} board rows is not a positive multiple of {SIZE}")
    boards = []
    for start in range(0, len(rows), SIZE):
        board = tuple(tuple(int(x) for x in row.split()) for row in rows[start : start + SIZE])
        if any(len(row) != SIZE for row in board):
            raise ValueError(f"board {len(boards)} is not {SIZE}x{SIZE}")
        boards.append(board)
    return Game(draws, boards)


def draw_turns(draws: list[int]) -> dict[int, int]:
    """Number -> index of its first draw.  A repeat draw marks nothing new,
    so only the first counts; setdefault keeps it."""
    turns: dict[int, int] = {}
    for i, n in enumerate(draws):
        turns.setdefault(n, i)
    return turns


def board_win(board: Board, draws: list[int], turns: dict[int, int]) -> Win | None:
    """The turn this board wins and its score, or None if it never does.

    A never-drawn cell gets turn len(draws), one past the end, so any line
    through it completes "after the game" and is ruled out.
    """
    never = len(draws)
    t = [[turns.get(n, never) for n in row] for row in board]
    lines = t + [list(col) for col in zip(*t)]
    turn = min(max(line) for line in lines)
    if turn == never:
        return None
    # Marked means drawn on or before the winning turn.
    unmarked = sum(n for row, trow in zip(board, t) for n, tn in zip(row, trow) if tn > turn)
    return Win(turn, unmarked * draws[turn])


def wins(game: Game) -> list[Win | None]:
    """Each board's win, in board order; None for a board that never wins."""
    turns = draw_turns(game.draws)
    return [board_win(b, game.draws, turns) for b in game.boards]


def parse_input(raw: str) -> list[Win | None]:
    return wins(read_game(raw))


def score_on_turn(board_wins: list[Win | None], turn: int) -> int:
    """The score of the board(s) winning on `turn`.  Two boards can complete
    on the same draw; if they would score differently, "the board that wins
    first (last)" is ambiguous."""
    scores = {w.score for w in board_wins if w is not None and w.turn == turn}
    if len(scores) != 1:
        raise ValueError(f"boards tie on turn {turn} with scores {sorted(scores)}")
    return scores.pop()


def part1(board_wins: list[Win | None]) -> int:
    turns = [w.turn for w in board_wins if w is not None]
    if not turns:
        raise ValueError("no board ever wins")
    return score_on_turn(board_wins, min(turns))


def part2(board_wins: list[Win | None]) -> int:
    # A board that never wins would be the true "last", and it has no score.
    if None in board_wins:
        raise ValueError(f"board {board_wins.index(None)} never wins")
    return score_on_turn(board_wins, max(w.turn for w in board_wins))


def solve(raw: str) -> tuple[int, int]:
    board_wins = parse_input(raw)
    return part1(board_wins), part2(board_wins)


def main() -> None:
    board_wins = parse_input(INPUT.read_text())
    print(f"part1={part1(board_wins)}")
    print(f"part2={part2(board_wins)}")


if __name__ == "__main__":
    raise SystemExit(main())
