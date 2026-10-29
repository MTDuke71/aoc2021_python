# Day 15 Function Guide — Chiton

Source: [`src/day15.py`](../../src/day15.py) ·
Tests: [`tests/test_day15.py`](../../tests/test_day15.py) ·
Statement: [`day15.md`](day15.md)

Answers (accepted): **508** / **2872**.

## 1. The problem

The input is a square grid of digits 1–9, the risk of each cell. Walk from
the top-left cell to the bottom-right in up/down/left/right steps. A path's
total risk is the sum of the cells it **enters**: the start cell is never
entered, so its risk never counts.

- **Part 1:** the lowest total risk across the 100 × 100 input grid.
- **Part 2:** the same on the full cave. The input is one tile of a 5 × 5
  arrangement (500 × 500). Each tile is the original with every risk raised
  by (tile row + tile column), wrapping 10 → 1, 11 → 2, and so on.

The statement's example: the best path costs **40**, then **315** on the
50 × 50 tiled version.

## 2. Representation

`parse_input` returns `Grid = tuple[tuple[int, ...], ...]`, one tuple of ints
per row. Tuples rather than lists because nothing mutates the grid, and
`tile()` returns the same type, so `lowest_risk` takes either one.

Dijkstra's bookkeeping lives inside `lowest_risk`:

- `best`: a dict from `(row, col)` to the lowest risk found so far.
- `heap`: a `heapq` list of `(risk, row, col)`. Python compares tuples
  element by element, so the heap is ordered by risk first. Equal risks are
  broken by row, then column, which is deterministic and doesn't matter.

The graph is never built. A cell's neighbours are computed on the fly, and
the cost of an edge is the risk of the cell it leads **into**. Graph people
call that a *node-weighted* grid, and it matters in §4.

Real input: 100 × 100, all digits 1–9, no zeros. 1 and 9 are the most
common, with 1844 and 1788 cells each.

## 3. Function walkthrough

### `parse_input(raw) -> Grid`

`splitlines()` plus a per-line `strip()`, so a CRLF input leaves no `\r`.
Blank lines are dropped. Raises `ValueError` on empty input, on rows of
different lengths, and on any row that isn't ASCII digits 1–9.

**0 is refused**, even though part 1 would handle it fine. Part 2's rule only
says what happens *above 9* (wrap to 1), and `tile()`'s arithmetic assumes
1–9: it would turn a 0 on the first tile into a 9. The parser checks the
precondition rather than letting `tile()` quietly produce a wrong map.

### `lowest_risk(grid) -> int`

Textbook Dijkstra with lazy deletion and an early exit:

1. Push `(0, 0, 0)`: the start costs nothing.
2. Pop the lowest-risk entry. If it is the target, return its risk.
3. If the popped risk is worse than `best` for that cell, it is stale; skip
   it. (On this puzzle that never happens; see §4.)
4. For each in-bounds neighbour, offer `risk + grid[nr][nc]`. If that beats
   `best`, record it and push.

Trace on the example. The heap is shown as `risk@(row,col)`, smallest first:

| pop | cell   | risk | pushes                 | heap afterwards (front)                |
| --: | ------ | ---: | ---------------------- | -------------------------------------- |
|   1 | (0, 0) |    0 | 1@(1,0), 1@(0,1)       | 1@(0,1) 1@(1,0)                        |
|   2 | (0, 1) |    1 | 4@(1,1), 7@(0,2)       | 1@(1,0) 4@(1,1) 7@(0,2)                |
|   3 | (1, 0) |    1 | 3@(2,0)                | 3@(2,0) 4@(1,1) 7@(0,2)                |
|   4 | (2, 0) |    3 | 6@(3,0), 4@(2,1)       | 4@(1,1) 4@(2,1) 6@(3,0) 7@(0,2)        |
|   5 | (1, 1) |    4 | 12@(1,2)               | 4@(2,1) 6@(3,0) 7@(0,2) 12@(1,2)       |
|   6 | (2, 1) |    4 | 10@(3,1), 7@(2,2)      | 6@(3,0) 7@(0,2) 7@(2,2) 10@(3,1) …     |

The search spreads out from the corner as a "flood" of rising risk: pops
come off in non-decreasing order (0, 1, 1, 3, 4, 4, 6, …), and the cheap
cells down the left edge, where the statement's highlighted path starts, are
taken first. The target comes off the heap at 40.

If the heap empties without reaching the target, the function raises
`AssertionError`. That cannot happen on a rectangular grid, because every
cell is connected to every other.

### `tile(grid, times) -> Grid`

Builds the full map: tile `(i, j)` is the original with every risk raised by
`i + j`, wrapped. The wrap is `(v + i + j - 1) % 9 + 1`:

- Shift 1..9 down to 0..8, add mod 9, shift back up.
- `8 + 1` → `(8 + 1 - 1) % 9 + 1 = 9`. `9 + 1` → `(9 + 1 - 1) % 9 + 1 = 1`.
  `8 + 4` → `(11) % 9 + 1 = 3`.

The comprehension runs tile-row `i`, then source row, then tile-column `j`,
then each value, which lays the output out row-major.

### `part1(parsed)` / `part2(parsed)`

`lowest_risk(parsed)` and `lowest_risk(tile(parsed, 5))`. Real input:
**508** and **2872**.

## 4. Why it is correct

**Dijkstra applies.** Every step costs 1–9, never negative. Dijkstra's
invariant: when a cell is popped, every cell with a lower risk has already
been popped, so nothing still on the heap can lead back to it more cheaply.
The first time the target is popped, its risk is final.

**Why not a simple DP over rows?** The tempting shortcut is to fill the grid
top-left to bottom-right, with each cell taking the cheaper of "from above"
and "from the left". That assumes the best path only moves right and down.
It is right on the example (it gets 40 there too), but it is not right in
general:

- `SNAKE` in the tests is a 7 × 5 grid with two walls of 9s, each two rows
  deep. The cheap route goes right, down, **left** across the middle, down,
  then right. Dijkstra gets 18; right/down DP gets 26.
- On the real input the DP is also wrong: **510** instead of 508 for part 1
  and **2875** instead of 2872 for part 2. Both best paths dip up or left
  somewhere.

`test_right_down_dp_is_not_enough` and
`test_right_down_dp_fails_on_real_input` pin both.

**A cell's first push is already final.** Instrumenting `lowest_risk` on the
real input shows **zero stale heap entries**: every cell is pushed exactly
once (part 1: 9,999 pushes for 10,000 cells; part 2: 249,999 for 250,000).
That isn't luck. It follows from the grid being node-weighted:

- Entering cell X costs `grid[X]`, the same from every neighbour.
- Neighbours are popped in order of their own risk. Say A is popped before
  B, so `risk(A) ≤ risk(B)`.
- Then A offers X `risk(A) + grid[X]`, and B's later offer
  `risk(B) + grid[X]` can never be lower.

So whichever neighbour reaches X first gives it its final risk, and the
`risk > best` stale check never fires here. It stays in the code because it
is what makes the function correct Dijkstra on *any* weighted graph, and it
costs one comparison. `test_every_cell_is_pushed_once` pins the
property on the example, the snake grid and both real maps, by counting
`heappush` calls per cell.

**Checked against an independent solver.** `relax_to_fixpoint` in the tests
is a Bellman-Ford-style sweep. It sets every cell to (cheapest neighbour +
own risk) and repeats until a full sweep changes nothing. It shares no code
with Dijkstra and doesn't care about move direction. It agrees on the
example (40), the snake (18), the real part 1 grid (508, in 0.10 s) and the
tiled example (315). It also gets **2872** on the real 500 × 500 map, but
takes 8.8 s there, so that check was run once by hand for this guide and is
not in the suite.

**The tiling matches the statement.** `test_tile_example_matches_statement`
compares `tile(example, 5)` against the statement's full 50 × 50 map, digit
for digit. `test_wrap_formula_matches_literal_rule` checks the modular
formula against "add 1, k times, wrap 10 to 1" for every risk 1–9 and every
shift 0–8.

## 5. Complexity

Dijkstra with a binary heap: O(N log N) for N cells (each cell pushed and
popped once, four neighbour checks each). N is 10⁴ for part 1 and 2.5 × 10⁵
for part 2. The heap stays small, because only the frontier is on it: at
most **231** entries in part 1 and **919** in part 2.

| phase  |      ms |
| ------ | ------: |
| parse  |   0.785 |
| part 1 |  10.377 |
| part 2 | 347.700 |
| total  | 358.862 |

`bench.py -n 5 15`, best of 5 on the real input.

Part 2 has 25× the cells and takes 33.5× the time. Measured separately (best
of 5): `tile()` is **14.7 ms** of that, and Dijkstra on the 500 × 500 map is
**326 ms**, which is 32× part 1's 10.2 ms on 25× the cells. The extra is in
line with the log factor, plus a `best` dict that has outgrown the CPU cache.
That last point is plausible but not measured.

This is the first 2021 day to cost more than a few milliseconds. Nearly all
of it is interpreter overhead per cell: one heap push, one heap pop, one
tuple build, four bounds checks and four dict lookups.

## 6. If I were writing this in Rust

A sketch of the shape; it was not compiled for this guide.

```rust
use std::cmp::Reverse;
use std::collections::BinaryHeap;

fn lowest_risk(grid: &[u8], w: usize, h: usize) -> u32 {
    let mut best = vec![u32::MAX; w * h];
    let mut heap = BinaryHeap::new();
    best[0] = 0;
    heap.push(Reverse((0u32, 0usize)));
    while let Some(Reverse((risk, i))) = heap.pop() {
        if i == w * h - 1 { return risk; }
        if risk > best[i] { continue; }
        let (r, c) = (i / w, i % w);
        let mut offer = |j: usize| {
            let nxt = risk + grid[j] as u32;
            if nxt < best[j] { best[j] = nxt; heap.push(Reverse((nxt, j))); }
        };
        if r > 0     { offer(i - w); }
        if r + 1 < h { offer(i + w); }
        if c > 0     { offer(i - 1); }
        if c + 1 < w { offer(i + 1); }
    }
    unreachable!()
}
```

- **Flat arrays, not maps.** A cell is `r * w + c`. `best` is a `Vec<u32>`
  initialised to `u32::MAX`, which replaces the Python dict and its `.get`
  default. On part 2 that is 1 MB for `best` and 250 KB of `u8` risks; both
  fit in L2 on most machines.
- **`BinaryHeap` is a max-heap**, hence the `Reverse`. This is the most
  common Dijkstra slip in Rust.
- **Don't materialise the tiles.** In Rust the cheap move is to compute a
  tiled cell's risk on demand, `(grid[(r % h0) * w0 + c % w0] + r / h0 + c / w0 - 1) % 9 + 1`,
  rather than build the 500 × 500 copy. In Python `tile()` is the clearer
  choice, and at 14.7 ms it is 4% of part 2.

Embedded framing: risks are 1–9 and paths are short, so the whole frontier
lives within a band of about 10 consecutive risk values. That is the setup
for the bucket queue below. It is a fixed ring of FIFOs indexed by
`risk % 10`, exactly the kind of structure you'd put in a firmware timer
wheel.

## 7. Possible optimization

**Bucket queue (Dial's algorithm).** Every edge costs 1–9, so when the
search is popping risk *d*, every entry on the heap is in *d … d + 9*. Ten
FIFO lists indexed by `risk % 10` replace the heap. A push is an append, a
pop is "take from the current bucket, or advance to the next non-empty
one". That turns O(log N) heap operations into O(1). Not implemented or
measured here. In CPython the win is probably smaller than the asymptotics
suggest, because `heapq` is C code and a Python-level bucket loop is not.

**Drop the stale check / mark at push time.** §4 shows the first push of a
cell is final on node-weighted grids. So `best` could be a plain `seen` set
filled at push time, with no comparison on pop. That is a valid
simplification *for this puzzle's graph shape only*. It was left out
because the general version is the one worth keeping in your head, and the
saving is one comparison per pop.

**A\* toward the corner.** Manhattan distance to the target × 1 (the
cheapest possible risk) is an admissible heuristic. It would skip some of
the cells far from the diagonal. Here the target is the farthest cell from
the start, and both runs pop every single cell before reaching it (10,000
of 10,000; 250,000 of 250,000), so there is room to prune. How much A\*
would actually save was not measured.
