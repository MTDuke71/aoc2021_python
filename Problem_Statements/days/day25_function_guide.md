# Day 25 Function Guide — Sea Cucumber

Source: [`src/day25.py`](../../src/day25.py) ·
Tests: [`tests/test_day25.py`](../../tests/test_day25.py) ·
Statement: [`day25.md`](day25.md)

Answers (accepted): **360** / free star (part 2 returns 0).

## 1. The problem

A grid holds two herds. `>` cucumbers move east and `v` cucumbers move
south. The grid wraps at both edges, so it is a torus. One step has two
halves:

1. the whole east herd looks one cell ahead, then every `>` that saw an
   empty cell moves into it at the same moment;
2. the whole south herd does the same against the map as it is *after* the
   east half.

Part 1 asks for the first step on which nobody moves. Part 2 has no puzzle:
the 50th star is given once the other 49 are held.

The ordering is the whole puzzle. Here is the statement's 4×10 example with
coordinates (row, col):

```text
start        after east half    after south half
..........   ..........         ..........
.>v....v..   .>v....v..         .>........
.......>..   ........>.         ..v....v>.
..........   ..........         ..........
```

- `>` at (1,1) is facing `v` at (1,2). The `v` has not moved yet when
  the east herd looks, so the `>` stays put. Then the `v` drops to (2,2).
- `>` at (2,7) has an empty cell ahead, so it moves to (2,8) during the
  east half. The `v` at (1,7) then sees (2,7) empty and drops into it.

So a south cucumber can follow an east cucumber in the same step, but not
the other way round.

## 2. Representation

`parse_input` returns `Seafloor(height, width, east, south)`, where `east`
and `south` are `frozenset`s of `(row, col)`. The real input is 137×139 =
19043 cells holding 4676 `>` and 4803 `v` (9479 cucumbers, about half the
grid).

Two sets per herd rather than a char grid buys two things:

- **"Simultaneous" is automatic.** The next herd is built as a new set
  while membership tests read the old one, so no cucumber can see a cell
  that another one vacated or filled in the same half-step. The tempting
  alternative is a char grid edited in place during the scan, and it is
  wrong whichever way the scan runs (1×3 rings; checked by running all
  three):

  | start | correct | in place, left→right | in place, right→left |
  |---|---|---|---|
  | `.>.` | `..>` | `>..` — moved, then moved again when the scan reached it | `..>` |
  | `>>.` | `>.>` | `>.>` | `.>>` — the back one followed into the cell the front one just left |

  Each direction passes one case and fails the other. The rule is that a
  cell vacated during this half-step still counts as occupied.
- **States compare with `==`.** `Seafloor` is a NamedTuple of frozensets,
  so "did anything change?" is a single equality test (see section 4).

## 3. Function walkthrough

### `parse_input(raw) -> Seafloor`

`splitlines()` plus a per-line `strip()`, so CRLF input leaves no `\r`.
Blank lines are skipped. Raises `ValueError` on an empty map, a ragged row,
or any character other than `>`, `v` or `.`.

### `move_herd(herd, blocker, ahead) -> frozenset`

This is one half-step. `ahead` maps a cell to the cell it faces (with the
wrap). Each cucumber ends up at `ahead(cell)` if that cell is in neither
`herd` nor `blocker`, and otherwise stays at `cell`. The herd is checked
too because a cucumber is blocked by one of its own kind (`...>>>>>...`
moves only the front one).

### `step(floor) -> Seafloor`

The east half runs `move_herd(east, south, col+1 mod w)`. The south half
then runs `move_herd(south, east', row+1 mod h)`, where `east'` is the
**updated** east herd. Passing `floor.east` there instead would let a `v`
fall into a cell a `>` just moved into, which is the mistake the 4×10
example is designed to catch.

### `render(floor) -> str`

Turns the state back into the statement's notation. The tests compare
renders against the statement's snapshots.

### `part1(parsed)` / `part2(parsed)`

`part1` steps until `step(floor) == floor` and returns that step's number
(1-based: if nobody moves on the first step, the answer is 1). `part2`
returns 0, matching aoc2020's day 25.

## 4. Why it is correct

**Each half-step is literal.** It is the statement's rule ("all consider,
then all move") with "consider" reading the old sets. The tests compare
against the statement's snapshots after steps 1, 2, 5, 10, 40 and 58, the
four-step wrap example, the single-row example and the 4×10 ordering
example.

**Stopping on `==` is the same as stopping on "nobody moved".** A cucumber
that moves lands on a cell its herd did not hold before (it checked that
the cell was empty). So after any move the new set contains a cell the old
one did not, and the state differs. If nobody moves, both sets come back
unchanged. `test_unchanged_state_means_nobody_moved` checks this on every
one of the 360 real steps. It runs a separate char-grid simulator that
counts movers, asserts that the two renders match each step, and asserts
that a mover count of 0 lines up with the states being equal.

**Termination is not guaranteed in general.** A lone `>` on a 1×3 ring
circles forever (pinned). `part1` relies on the puzzle's promise that the
herds jam. On the real input they do, and the slowdown is gradual:

| step | `>` moved | `v` moved |
| ---: | ---: | ---: |
| 1 | 2375 | 2395 |
| 100 | 1618 | 1755 |
| 200 | 1136 | 1003 |
| 300 | 311 | 395 |
| 350 | 3 | 27 |
| 359 | 0 | 1 |
| 360 | 0 | 0 |

Step 359 is a single `v` moving on its own. Summed over all steps, 780,330
moves happen before the jam.

## 5. Complexity

Each step rebuilds both sets: O(cucumbers) hash lookups per step, so
O(steps × cucumbers) overall, which is 360 × 9479 ≈ 3.4 M cucumber-updates.
The cost per step stays flat even when hardly anything moves, because every
cucumber is still checked.

| phase | ms |
| --- | ---: |
| parse | 1.762 |
| part 1 | 600.058 |
| part 2 | 0.000 |
| total | 601.821 |

`bench.py 25`, best of 5 on the real input. That works out to about 1.67 ms
per step, or about 176 ns per cucumber per step. The time goes into tuple
building and set hashing, and that is the cost the sidebar in section 7
removes.

## 6. If I were writing this in Rust

A sketch of the shape; it was not compiled for this guide.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
enum Cell { Empty, East, South }

fn half_step(g: &[Vec<Cell>], herd: Cell, dr: usize, dc: usize) -> (Vec<Vec<Cell>>, bool) {
    let (h, w) = (g.len(), g[0].len());
    let mut next = g.to_vec();
    let mut moved = false;
    for r in 0..h {
        for c in 0..w {
            let (nr, nc) = ((r + dr) % h, (c + dc) % w);
            if g[r][c] == herd && g[nr][nc] == Cell::Empty {
                next[r][c] = Cell::Empty;
                next[nr][nc] = herd;
                moved = true;
            }
        }
    }
    (next, moved)
}
```

- **Read `g`, write `next`.** This double buffer plays the same role as
  Python building a new frozenset. The borrow checker enforces it:
  `g: &[...]` cannot be written, so the in-place mutation mistake from
  section 2 does not compile.
- **Return `moved` rather than comparing grids.** That makes the stopping
  test a flag, not an O(cells) equality. Python can't do the same cheaply
  with a set comprehension, which is one reason it compares states with
  `==`.
- **`usize` and wrap.** Movement only goes forward, so `(r + 1) % h` never
  underflows. Unlike day 11 there is no `r - 1` to guard.
- **Allocation.** A flat `Vec<Cell>` with two buffers swapped each half
  step avoids reallocating. `Cell` as a `u8` makes a step stream about
  19 KB through cache.

Register framing: this is a two-phase clocked update, with the east herd
as one register bank and the south herd as another. Each phase samples
every input and only then latches every output, with the west/north
neighbour feeding each flip-flop. The `next` buffer is the latch, and
reading `g` while writing `next` is setup time before the clock edge.

## 7. Sidebar: row bitmasks

Each row becomes a 139-bit Python int, with bit *c* standing for column
*c*, one int per herd. A half-step then becomes a few word-wide operations
per row instead of one hash per cucumber:

```python
ahead = lambda x: (x >> 1) | ((x & 1) << (w - 1))   # bit c <- bit c+1 (rotate)
fwd   = lambda x: ((x << 1) & mask) | (x >> (w - 1)) # bit c -> bit c+1 (rotate)

mv_e  = [e & ~ahead(e | s) for e, s in zip(E, S)]    # east movers
E     = [(e & ~m) | fwd(m) for e, m in zip(E, mv_e)]
occ   = [e | s for e, s in zip(E, S)]                # uses the NEW east
mv_s  = [S[r] & ~occ[(r + 1) % h] for r in range(h)] # south movers
S     = [(S[r] & ~mv_s[r]) | mv_s[r - 1] for r in range(h)]
```

East movement is a rotate within a row. South movement is "AND with the
row below", with movers arriving one row down. `mv_s[r - 1]` at `r = 0`
reads `mv_s[-1]`, which is the bottom row, and Python's negative indexing
supplies that wrap for free.

Measured on the real input: **31.5 ms** against the set version's
600 ms, best of 5 (`perf_counter`, run outside `bench.py`), about 19×
faster. The full function is `bitboard_part1` in the test module, pinned
to `part1` on the example, three small jamming maps and the real input.

It stays a sidebar because it is opaque. `~ahead(e | s)` makes sense only
once you have pictured the rotate. The set version reads like the
statement, and 600 ms is fine for a puzzle that runs once.

In C or Rust the same idea uses `[u64; 3]` per row (139 bits rounded up to
192), and the rotate has to carry bits across the word boundaries. That is
fiddlier than Python's unbounded ints, but it compiles to straight-line
shifts.

## 8. Possible optimization

Not measured; ideas, not facts.

- **Track only cucumbers that could move.** A cucumber can only start
  moving once the cell ahead of it was vacated. Keeping a frontier of
  "cells ahead that just emptied" would make late steps (3 + 27 movers at
  step 350) cost almost nothing instead of the full 9479. Most of the run
  is busy (step 200 still has more than 2000 movers), so the gain is
  bounded.
- **numpy.** `np.roll` on a uint8 grid gives the "ahead" view for each
  half, and a boolean mask does the move. It does the same work as the
  bitboard with vectorised byte operations instead of bigint shifts.
