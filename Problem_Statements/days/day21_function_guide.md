# Day 21 Function Guide — Dirac Dice

Source: [`src/day21.py`](../../src/day21.py) ·
Tests: [`tests/test_day21.py`](../../tests/test_day21.py) ·
Statement: [`day21.md`](day21.md)

Answers (accepted): **853776** / **301304993766094**.

## 1. The problem

Two pawns on a circular track of spaces 1..10. A turn rolls a die three
times, moves the pawn that many spaces clockwise, and adds the landing
space to that player's score. Player 1 moves first. The input is just the
two starting spaces (real input: 6 and 10).

- **Part 1.** A deterministic d100 (1, 2, ..., 100, 1, ...). First to
  1000 wins. Answer: losing score × total die rolls.
- **Part 2.** A "quantum" d3. Every roll splits the universe into three
  copies, one per face. First to 21 wins. Answer: how many universes the
  more frequent winner wins.

Part 2's counts are around 10¹⁴ (the real input has 593,229,537,543,293
universes in total), so universes have to be *counted*, never visited one
at a time.

## 2. Part 1: just play it

The statement's opening turns for starts 4 and 8:

```
P1 rolls 1+2+3 = 6    4 -> 10   score 10
P2 rolls 4+5+6 = 15   8 -> 3    score 3
P1 rolls 7+8+9 = 24  10 -> 4    score 14
...
```

The game ends after a few hundred turns: 331 for the example (993 rolls),
308 for the real input. A literal loop is the clearest code and costs
under 0.1 ms. The real input ends with the loser on 924 after 924 rolls,
so the answer is 924² = 853776. That is a coincidence of this input and
nothing in the code depends on it.

## 3. Part 2: two reductions

### 3a. 27 rolls collapse to 7 sums

Only the *sum* of a turn's three rolls affects the game. Of the 27 roll
sequences:

| sum      |  3 |  4 |  5 |  6 |  7 |  8 |  9 |
| -------- | -: | -: | -: | -: | -: | -: | -: |
| sequences|  1 |  3 |  6 |  7 |  6 |  3 |  1 |

These are the coefficients of (x + x² + x³)³. Each turn becomes a 7-way
branch, each branch weighted by its multiplicity. This is `DIRAC_SUMS`,
computed from `product((1, 2, 3), repeat=3)` rather than typed in, and the
table above is pinned by `test_dirac_sums`.

### 3b. The future depends only on a small state

Who wins from a given moment depends only on

```
(mover's position, mover's score, other's position, other's score)
```

Positions take 10 values. Scores below 21 take 21 values, since anything
at 21 or more has already ended the game. That's at most
10 × 21 × 10 × 21 = **44,100** states, however many universes pass
through each one. The real input reaches 15,199 of them, the example
17,512 (pinned).

So `wins(state) -> (mover's wins, other's wins)` gets memoised, and the
universe tree collapses into a table of at most 44,100 rows.

### A concrete trace

Look at the leaves first:

- `wins(5, 20, 3, 0)`: the mover is on 20 points. Every sum lands
  somewhere worth at least 1, so all 27 universes win: **(27, 0)**.
- `wins(10, 11, 1, 20)`: the mover is on space 10 with 11 points. Sums 3..9
  land on spaces 3..9, for scores 14..20, so none of the 7 sums wins. In
  each of those 27 universes the other player (on 20) then wins all 27 of
  theirs: **(0, 27 × 27 = 729)**.

Both values were run, not worked out by hand. Every interior state is the
same sum of 7 children, each weighted by its multiplicity.

## 4. Function walkthrough

### `parse_input(raw) -> Start`

Two lines, `Player N starting position: K`. Returns `Start(p1, p2)`.
Wrong labels, the players in the wrong order, the wrong line count, or a
start outside 1..10 all raise `ValueError`. A per-line `strip()` handles
CRLF.

### `advance(pos, steps) -> int`

`(pos - 1 + steps) % 10 + 1`: shift to 0..9, wrap, shift back. The track
is 1-based and has no space 0, so a pawn landing on the tenth space must
read 10. `advance(4, 6) == 10` is a test case for exactly that.

### `deterministic_die()` / `play_deterministic(start, target=1000)`

A generator over `n % 100 + 1`, and a loop that alternates `player = 1 - player`.
It returns `(losing score, rolls)`. `test_player2_can_win` is a
hand-traced game won by player 2, which guards `score[1 - player]` from
being written as `score[1]`.

### `DIRAC_SUMS`

`((3, 1), (4, 3), (5, 6), (6, 7), (7, 6), (8, 3), (9, 1))`: each sum with
the number of roll sequences that produce it.

### `make_wins(target)` → `wins(pos, score, other_pos, other_score)`

The recursion is written from the **mover's** point of view:

```python
for steps, ways in DIRAC_SUMS:
    new_pos = advance(pos, steps)
    new_score = score + new_pos
    if new_score >= target:
        mine += ways                       # these universes end here
    else:
        their_wins, my_wins = wins(other_pos, other_score, new_pos, new_score)
        mine += ways * my_wins
        theirs += ways * their_wins
```

The recursive call puts the other player in the mover's seat, so its result
comes back as (their wins, my wins) and gets unpacked swapped. One function
serves both players, with no `player` index in the key.

`make_wins` builds a **new** `@cache`d closure for each call instead of
caching one module-level function. With a global cache, `bench.py`'s
reps 2–5 would time a single dictionary hit (`dirac_wins` would read about
0 ms), and calls with different targets would share entries keyed without
the target. `test_fresh_table_per_call` pins this, and so does the bench:
best 19.5 ms against median 20.5 ms, so every rep did the full work.

### `dirac_wins(start, target=21)` / `part2`

`dirac_wins` runs `make_wins(target)(p1, 0, p2, 0)` and returns
(player 1's wins, player 2's wins). `part2` takes the `max`.

## 5. Why it is correct

- **The state is complete.** The die has no memory and the rules don't
  look at history, so two universes in the same 4-tuple state with the same
  player to move have identical futures. Memoising is therefore exact.
- **The merge is exact.** All the universes for one sum go to the same
  child, so counting them once and multiplying by the multiplicity equals
  counting them one by one.
- **Every universe is counted exactly once.** It either ends on this turn
  (a leaf, counted by `ways`) or continues into exactly one child.
- **Pinned against two independent references** in the tests:
  - `literal_dirac`: no memo, no merging. Every single roll splits three
    ways, exactly as the statement words it. It's exponential, so it is
    checked at targets 1, 2, 4, 6 and 8 from four starts.
  - `forward_dirac`: breadth-first over turns, pushing universe counts
    forward through 27 single-roll splits, with absolute player roles. It
    is fast enough for target 21 and agrees on the example, two more
    starts, and the real input.
- The statement's example counts (444356092776315 / 341960390180808)
  match exactly.

## 6. Complexity

Part 2 makes 63,832 calls to `wins` on the real input (15,199 misses plus
48,633 cache hits), each doing at most 7 branches of a few integer
operations. That's O(positions² × target²) states × 7. Part 1 is
O(turns), about 308 here.

A game lasts between 5 and 19 turns (both players' turns counted), as
measured on the real input. That depth is also the recursion depth, so it
stays far below Python's recursion limit.

| phase  |     ms |
| ------ | -----: |
| parse  |  0.001 |
| part 1 |  0.094 |
| part 2 | 19.520 |
| total  | 19.615 |

`bench.py 21`, best of 5 on the real input.

What each reduction buys, measured on the real input (best of 5, same
answer every time):

| variant                                    |     ms |
| ------------------------------------------ | -----: |
| memo, 7 weighted sums (shipped)            |   19.4 |
| memo, 27 single-roll branches              |   67.5 |
| forward by turn, 7 weighted sums           |   79.8 |
| forward by turn, 27 branches (test oracle) |  282.3 |

Merging rolls into sums is worth about 3.5× in either shape. Memo beats
forward stepping because the forward version rebuilds a `Counter` of live
states every turn and keeps each state's player roles apart, while the memo
visits each state once.

## 7. If I were writing this in Rust

A sketch; it was not compiled for this guide.

```rust
const SUMS: [(u8, u64); 7] = [(3, 1), (4, 3), (5, 6), (6, 7), (7, 6), (8, 3), (9, 1)];

// memo[pos][score][other_pos][other_score]; positions 0-based here.
type Memo = [[[[Option<(u64, u64)>; 21]; 10]; 21]; 10];

fn wins(memo: &mut Memo, p: usize, s: usize, op: usize, os: usize) -> (u64, u64) {
    if let Some(r) = memo[p][s][op][os] { return r; }
    let (mut mine, mut theirs) = (0u64, 0u64);
    for &(steps, ways) in &SUMS {
        let np = (p + steps as usize) % 10;
        let ns = s + np + 1;
        if ns >= 21 {
            mine += ways;
        } else {
            let (tw, mw) = wins(memo, op, os, np, ns);
            mine += ways * mw;
            theirs += ways * tw;
        }
    }
    memo[p][s][op][os] = Some((mine, theirs));
    (mine, theirs)
}
```

- **The memo is a fixed 4-D array, not a hash map.** 44,100 entries of
  `Option<(u64, u64)>` comes to about 1 MB, which is too big for the stack.
  Box it (`vec![None; 44_100]` with a computed index) or make it `static`.
  The key turns into an address computation: a lookup ROM indexed by the
  concatenated state fields.
- **`u64` is enough.** The largest count here is 4.4·10¹⁴ against
  `u64::MAX` ≈ 1.8·10¹⁹. Python's ints never overflow, so this question
  doesn't come up there. In Rust it has to be answered, and `checked_mul`
  in a debug build would confirm it.
- **0-based positions** remove the `- 1 ... + 1` from `advance`. The score
  adds `np + 1` instead.

## 8. Possible optimization

**Bottom-up table.** Scores only increase, so you can fill the table from
high scores to low without recursion: iterate both scores from 20 down to
0 and every position pair. That's the same 44,100 cells (including
unreachable ones the memo skips) with no call overhead. In Python the loop
overhead would probably cancel the gain. Not measured.

**Players are independent until the race.** Each player's sequence of
turns does not depend on the other's rolls. You could count, per player,
the universes that reach 21 on exactly their k-th turn (and those still
short after k turns), then combine: P1 wins on turn k when P1 finishes
then and P2 is still short after k−1 turns. Two small per-player DPs
replace the joint 4-D state. It's elegant, but the joint memo is already
20 ms, and this needs care with the per-turn universe multipliers. Not
implemented.
