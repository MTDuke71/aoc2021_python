# Day 04 Function Guide — Giant Squid

Source: [`src/day04.py`](../../src/day04.py) ·
Tests: [`tests/test_day04.py`](../../tests/test_day04.py) ·
Statement: [`day04.md`](day04.md)

Answers (accepted): **29440** / **13884**.

## 1. The problem

The input is a draw order (one comma-separated line) followed by a set of
5x5 bingo boards. A drawn number is marked on every board that has it. A
board wins when any full row or column is marked; diagonals do not count. A
board's score is the sum of its unmarked cells times the number that just
completed the line.

- **Part 1:** the score of the board that wins first.
- **Part 2:** the score of the board that wins last.

The statement describes this as a simulation: draw, mark, check every
board, repeat. The solution does not simulate. It asks a different
question that gives the same answer: *on which turn does each cell get
marked?*

Trace on the statement's third board. Replace every number by the index at
which it is drawn (the draws start `7,4,9,5,11,17,23,2,0,14,21,24,...`,
so 7 is turn 0, 4 is turn 1, 24 is turn 11):

```text
board                        draw turn of each cell     row max
14 21 17 24  4                9 10  5 11  1              11   <- min
10 16 15  9 19               12 13 16  2 23              23
18  8 23 26 20               20 22  6 25 21              25
22 11 13  6  5               19  4 14 15  3              19
 2  0 12  3  7                7  8 18 24  0              24

column max                   20 22 18 25 23
```

A line is complete on the turn of its **latest** cell, so each line's
completion turn is its max. The board wins on its **earliest** line, the
min of those ten maxes: 11, the top row. Turn 11 is the draw of 24.
Marked cells are the ones with turn <= 11. The unmarked cells are the rest,
summing to 188, so the score is 188 * 24 = 4512.

The same arithmetic on all three example boards:

```text
board   row maxes            column maxes         wins on   score
  0     19 22 13 24 26       26 18 24 20 23         13      2192
  1     24 20 23 21 18       24 22 14 18 19         14      1924   <- last
  2     11 23 25 19 24       20 22 18 25 23         11      4512   <- first
```

Board 2 wins first (part 1's 4512). Board 1 wins last, on its middle
column at turn 14, the draw of 13, with 148 unmarked (part 2's 1924). Board
0's 2192 is never asked for.

## 2. Representation

`read_game` returns a `Game(draws, boards)`: the draws as a `list[int]` and
each board as a 5-tuple of 5-tuples. That is the text and nothing more.

`parse_input` goes one step further and returns `list[Win | None]`: for
each board, in board order, a `Win(turn, score)` or `None` if the board
never wins. Both parts need exactly this list and neither needs anything
else, so it is built once in parse rather than re-derived per part. After
parse, the parts are one-liners over 100 small tuples.

The real input is 100 draws, a permutation of 0..99, and 100 boards. No
board repeats a number, and every cell's number is eventually drawn, so
every board wins at some point. The 100 win turns fall on 42 distinct turns
between 22 and 84; up to 7 boards finish on the same draw. The first and
last turns belong to one board each.

## 3. Function walkthrough

### `read_game(raw) -> Game`

Strips every line (which removes CRLF's `\r`) and drops blanks. The first
line is the draws. The rest must be a positive multiple of 5 rows, each of
exactly 5 numbers. Anything else raises `ValueError`
(`test_malformed_input_is_an_error`).

Dropping blank lines means board boundaries come from counting rows, not
from the blank separators. That tolerates a stray or missing blank line.
The cost is that a board with an extra row is caught only indirectly: it
shifts every later board by one row, and the total stops being a multiple
of 5.

### `draw_turns(draws) -> dict[int, int]`

Number to the index of its **first** draw. `setdefault` keeps the first:
a number drawn again marks nothing new. The real input never repeats a
draw, but the random tests do (`test_repeat_draw_counts_once`).

### `board_win(board, draws, turns) -> Win | None`

The trace from section 1, in code:

1. Map the board to a grid of turns. A number never drawn gets
   `len(draws)`, one past the last turn.
2. Build the ten lines (five rows, five columns via `zip(*t)`), take each
   line's max, take the min of those.
3. If that min is `len(draws)`, every line has a never-drawn cell: `None`.
4. Otherwise sum the cells whose turn is **after** the winning turn and
   multiply by `draws[turn]`.

The one-past-the-end sentinel makes "never drawn" fall out of the same
min/max arithmetic with no special case: such a cell can only raise a
line's max, and a line containing one can only win "after the game".

### `wins(game)` and `parse_input(raw)`

`wins` builds the turn map once and applies `board_win` to every board.
`parse_input` is `wins(read_game(raw))`.

### `score_on_turn(board_wins, turn) -> int`

The score of whichever board wins on `turn`. Several boards can complete on
the same draw. If they score the same, it doesn't matter which one "won".
If they score differently, "the board that wins first" (or last) does not
say which, and this raises rather than picking one. On the real input the
first and last turns each have a single board, so neither part hits this.

### `part1` and `part2`

`part1` is `score_on_turn` at the minimum win turn: board 79, turn 22,
drawn number 46, winning on column 1 (`60 71 75 46 16`), 640 unmarked,
640 * 46 = 29440.

`part2` is the same at the maximum: board 32, turn 84, drawn number 52,
winning on row 0 (`52 35 43 77 79`), 267 unmarked, 267 * 52 = 13884.

`part2` first rejects a board that never wins. Such a board would be the
true "last", and it has no score. Part 1 is still defined in that case,
since some other board won first (`test_part2_board_that_never_wins_is_an_error`).

## 4. Why it is correct

Marking only ever adds marks; nothing gets unmarked. So a cell is marked
after turn T exactly when its first draw is at or before T. A line is
complete after turn T exactly when *every* cell's turn is <= T, which is
when the line's **max** is <= T. The board has won by turn T when *some*
line is complete, and the first such T is the **min** over lines of the
max. The unmarked cells at that moment are the ones with turn > T.

Part 2's "keep playing until this point" doesn't change a board's own
history: a board's marks depend only on the draws, never on other boards.
So each board's win turn is the same whether or not the game is imagined
to stop at the first winner, and the last winner is the max.

The standing rule says a shortcut gets pinned by a test, and this whole
day is a shortcut. Two tests compare against `simulate`, a literal
implementation of the statement: draw, mark every board, check every row
and column, record `(turn, score)` the first time a board wins.

- `test_turn_arithmetic_matches_simulation` compares `board_win` board by
  board on 500 seeded random games. The number pools are small (25 to 40
  numbers), so draws repeat, boards share numbers, and some cells are
  never drawn. The test asserts that the never-wins path was actually hit.
- `test_parts_match_simulation` compares `part1` and `part2` with the
  simulation's first and last winners on 500 more games. Games where the
  answer is ambiguous or undefined are left out, and the test asserts
  that part 2 was actually compared.

`test_example_matches_simulation` and the two example tests anchor both
the simulation and the arithmetic to the statement's 4512 and 1924, and to
the boards and turns it names.

## 5. Complexity

With B boards of 25 cells and D draws: building the turn map is O(D). Each
board is 25 lookups, 10 lines of 5 to take maxes over, and a 25-cell sum,
so the whole thing is O(D + 25B), linear in the input. Both parts are O(B)
scans of the win list.

The literal simulation is O(D · B · 25) cell checks in the worst case: on
the real input, up to 250,000 if every board played to the end, against
the arithmetic's 2,500 lookups.

`bench.py 4`, best of 5 on the real input:

| phase | ms |
| --- | ---: |
| parse | 0.972 |
| part 1 | 0.006 |
| part 2 | 0.007 |
| total | 0.986 |

Parse holds all the work, by design. Timed separately with `timeit` (best
of 5 repeats of 100), `read_game` is 0.44 ms and `wins` is 0.52 ms. The
parts are microseconds because they only scan 100 tuples.

## 6. If I were writing this in Rust

Compiled and run while writing this guide (rustc 1.93.1, edition 2021,
`-O`). It gives 4512 / 1924 on the example and 29440 / 13884 on the real
input.

```rust
use std::collections::HashMap;

type Board = [[u32; 5]; 5];

#[derive(Debug, Clone, Copy, PartialEq)]
struct Win { turn: usize, score: u32 }

fn board_win(board: &Board, draws: &[u32], turns: &HashMap<u32, usize>) -> Option<Win> {
    let never = draws.len();
    let t = board.map(|row| row.map(|n| *turns.get(&n).unwrap_or(&never)));
    let rows = t.iter().map(|r| *r.iter().max().unwrap());
    let cols = (0..5).map(|c| (0..5).map(|r| t[r][c]).max().unwrap());
    let turn = rows.chain(cols).min().unwrap();
    if turn == never {
        return None;
    }
    let unmarked: u32 = (0..25)
        .filter(|&i| t[i / 5][i % 5] > turn)
        .map(|i| board[i / 5][i % 5])
        .sum();
    Some(Win { turn, score: unmarked * draws[turn] })
}
```

The things worth noting:

- **`[[u32; 5]; 5]` is the natural board type.** The size is in the type,
  so the 5x5 check in `read_game` becomes a parse-time conversion that
  either produces a board or fails. `board.map(|row| row.map(...))` turns
  it into a same-shaped grid of turns with no allocation; fixed-size
  arrays live on the stack.
- **`Option<Win>` is the `Win | None` return.** The difference is that
  the compiler makes every caller deal with the `None`. In the Python,
  `part1` filters `None`s out and `part2` rejects them, but nothing forced
  either to.
- **`rows.chain(cols).min()`** is the min-of-maxes without building a
  list of lines. The Python builds `t + [list(col) for col in zip(*t)]`,
  ten small lists, because that reads more directly.
- **Ties.** `min_by_key` and `max_by_key` return *some* extreme element on
  a tie, quietly (the first minimum, the last maximum). A faithful port of
  `score_on_turn` would collect the scores at that turn and check there
  is one. The sketch's `main` does not, which is fine on this input and
  is exactly the silent choice the Python refuses to make.
- **Overflow.** The worst score on a board of numbers 0..99 is under
  25 * 99 * 99 = 245,025, far inside `u32`.

For an embedded framing: the turn grid is a timestamp per cell, and a
board win is the earliest time at which some line of ANDed "marked" bits
goes high. Rather than evaluating those ANDs at every clock, the solution
computes each line's settle time (max of its inputs' arrival times) and
takes the earliest one (min over lines). It is static timing analysis on a
10-output circuit.

## 7. Possible optimization

None worth having; the day is under 1 ms, and nearly all of it is
parsing text into ints.

A sidebar for the curious: the turn map is a `dict`, but the real draws
are a permutation of 0..99, so a 100-entry list indexed by number would
do. It would save a hash per lookup. It would also need a range check the
puzzle doesn't promise and a separate "never drawn" value, and at 2,500
lookups there is nothing to win.

The other direction is a bitmask per board: 25 bits of marks, and ten
precomputed line masks, with a line complete when `marks & mask == mask`.
That is the natural representation if you *do* simulate, and it is the
fastest simulation. But it still visits every draw, where the turn
arithmetic visits every cell once.
