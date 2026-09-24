"""Day 4: Giant Squid."""

import random

import pytest

import day04

LOCKED = (29440, 13884)

EXAMPLE = """\
7,4,9,5,11,17,23,2,0,14,21,24,10,16,13,6,15,25,12,22,18,20,8,19,3,26,1

22 13 17 11  0
 8  2 23  4 24
21  9 14 16  7
 6 10  3 18  5
 1 12 20 15 19

 3 15  0  2 22
 9 18 13 17  5
19  8  7 25 23
20 11 10 24  4
14 21 16 12  6

14 21 17 24  4
10 16 15  9 19
18  8 23 26 20
22 11 13  6  5
 2  0 12  3  7
"""


def simulate(game):
    """The statement's procedure, literally: draw a number, mark it on every
    board, and after each draw check every row and column of every board.
    Returns {board index: (turn, score)} for the boards that win."""
    marked = [[[False] * 5 for _ in range(5)] for _ in game.boards]
    won = {}
    for turn, n in enumerate(game.draws):
        for b, board in enumerate(game.boards):
            if b in won:
                continue
            for r in range(5):
                for c in range(5):
                    if board[r][c] == n:
                        marked[b][r][c] = True
            m = marked[b]
            if any(all(row) for row in m) or any(all(m[r][c] for r in range(5)) for c in range(5)):
                unmarked = sum(board[r][c] for r in range(5) for c in range(5) if not m[r][c])
                won[b] = (turn, unmarked * n)
    return won


GRID = tuple(tuple(10 * r + c for c in range(5)) for r in range(5))  # 0..4, 10..14, ..., 40..44
GRID_SUM = sum(map(sum, GRID))


def random_game(rng):
    """Small number range so draws repeat, boards share numbers, and
    some cells are never drawn."""
    pool = rng.randint(25, 40)
    draws = [rng.randrange(pool) for _ in range(rng.randint(1, 50))]
    boards = []
    for _ in range(rng.randint(1, 6)):
        cells = rng.sample(range(pool), 25)
        boards.append(tuple(tuple(cells[r * 5 : r * 5 + 5]) for r in range(5)))
    return day04.Game(draws, boards)


def test_read_game():
    game = day04.read_game(EXAMPLE)
    assert game.draws[:5] == [7, 4, 9, 5, 11]
    assert len(game.draws) == 27
    assert len(game.boards) == 3
    assert game.boards[0][0] == (22, 13, 17, 11, 0)
    assert game.boards[2][4] == (2, 0, 12, 3, 7)


def test_example_winner():
    """Third board, top row, completed by 24 (turn 11); 188 unmarked."""
    game = day04.read_game(EXAMPLE)
    turns = day04.draw_turns(game.draws)
    win = day04.board_win(game.boards[2], game.draws, turns)
    assert win == day04.Win(11, 188 * 24)
    assert game.draws[11] == 24
    # "After the next six numbers ... there are still no winners."
    assert all(day04.board_win(b, game.draws, turns).turn >= 11 for b in game.boards)


def test_part1_example():
    assert day04.part1(day04.parse_input(EXAMPLE)) == 4512


def test_example_last_winner():
    """Second board, middle column, completed by 13 (turn 14); 148 unmarked.
    It is the last of the three to win."""
    board_wins = day04.parse_input(EXAMPLE)
    assert day04.read_game(EXAMPLE).draws[14] == 13
    assert board_wins[1] == day04.Win(14, 148 * 13)
    assert max(board_wins, key=lambda w: w.turn) is board_wins[1]


def test_part2_example():
    assert day04.part2(day04.parse_input(EXAMPLE)) == 1924


def test_example_matches_simulation():
    game = day04.read_game(EXAMPLE)
    expected = simulate(game)
    assert [tuple(w) for w in day04.parse_input(EXAMPLE)] == [expected[b] for b in range(3)]


def test_turn_arithmetic_matches_simulation():
    """The shortcut this day rests on: a board wins on min over its lines of
    max over the line of the cells' draw turns, and "marked" means drawn on
    or before that turn.  Check it against literal marking on random games
    with repeated draws and never-drawn cells."""
    rng = random.Random(2021)
    never_won = 0
    for _ in range(500):
        game = random_game(rng)
        turns = day04.draw_turns(game.draws)
        expected = simulate(game)
        for b, board in enumerate(game.boards):
            win = day04.board_win(board, game.draws, turns)
            if b in expected:
                assert tuple(win) == expected[b]
            else:
                never_won += 1
                assert win is None
    assert never_won > 0  # the never-wins path really was exercised


def test_repeat_draw_counts_once():
    """90 is drawn at turns 0 and 3.  Its first draw marks it; the board
    wins on turn 5 when 5 completes the top row."""
    board = ((90, 1, 2, 3, 5),) + GRID[1:]
    draws = [90, 1, 2, 90, 3, 5]
    win = day04.board_win(board, draws, day04.draw_turns(draws))
    assert win.turn == 5
    assert win.score == (sum(sum(row) for row in board[1:])) * 5


def test_column_win():
    draws = [0, 10, 20, 30, 40]
    win = day04.board_win(GRID, draws, day04.draw_turns(draws))
    assert win.turn == 4
    assert win.score == (GRID_SUM - sum(draws)) * 40


def test_no_board_ever_wins_is_an_error():
    lines = EXAMPLE.splitlines()
    lines[0] = "7,4,9"
    with pytest.raises(ValueError, match="no board"):
        day04.part1(day04.parse_input("\n".join(lines)))


def test_tie_for_first_with_different_scores_is_an_error():
    a = GRID
    b = ((0, 1, 2, 3, 4),) + tuple(tuple(100 + 10 * r + c for c in range(5)) for r in range(4))
    draws = [0, 1, 2, 3, 4]
    with pytest.raises(ValueError, match="tie"):
        day04.part1(day04.wins(day04.Game(draws, [a, b])))


def test_tie_for_first_with_equal_scores_is_fine():
    draws = [0, 1, 2, 3, 4]
    assert day04.part1(day04.wins(day04.Game(draws, [GRID, GRID]))) == (GRID_SUM - 10) * 4


def test_parts_match_simulation():
    """part1/part2 pick by turn from parse_input's list; the simulation
    records wins in the order they happen.  First and last recorded must be
    what the parts return, whenever the answer is well defined."""
    rng = random.Random(4)
    checked = 0
    for _ in range(500):
        game = random_game(rng)
        won = simulate(game)
        board_wins = day04.wins(game)
        if not won:
            continue
        first = min(t for t, _ in won.values())
        last = max(t for t, _ in won.values())
        if len({s for t, s in won.values() if t == first}) == 1:
            assert day04.part1(board_wins) == next(s for t, s in won.values() if t == first)
        if len(won) == len(game.boards) and len({s for t, s in won.values() if t == last}) == 1:
            assert day04.part2(board_wins) == next(s for t, s in won.values() if t == last)
            checked += 1
    assert checked > 0  # part 2 really was compared, not skipped every time


def test_part2_board_that_never_wins_is_an_error():
    """Board 1's cells are never drawn, so it never wins, and "last" has
    no score.  Part 1 is still defined."""
    other = tuple(tuple(100 + 10 * r + c for c in range(5)) for r in range(5))
    board_wins = day04.wins(day04.Game([0, 1, 2, 3, 4], [GRID, other]))
    assert day04.part1(board_wins) == (GRID_SUM - 10) * 4
    with pytest.raises(ValueError, match="never wins"):
        day04.part2(board_wins)


def test_part2_tie_for_last_with_different_scores_is_an_error():
    b = ((0, 1, 2, 3, 4),) + tuple(tuple(100 + 10 * r + c for c in range(5)) for r in range(4))
    with pytest.raises(ValueError, match="tie"):
        day04.part2(day04.wins(day04.Game([0, 1, 2, 3, 4], [GRID, b])))


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "1,2,3\n",  # no boards
        "1,2,3\n\n1 2 3 4 5\n",  # partial board
        "1,2,3\n\n" + "1 2 3 4\n" * 5,  # 5x4
        "1,2,x\n\n" + "1 2 3 4 5\n" * 5,
    ],
)
def test_malformed_input_is_an_error(raw):
    with pytest.raises(ValueError):
        day04.read_game(raw)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day04.parse_input(crlf) == day04.parse_input(EXAMPLE)
    assert day04.solve(crlf) == (4512, 1924)


def test_real_input_locked(check_locked):
    check_locked(day04, LOCKED)
