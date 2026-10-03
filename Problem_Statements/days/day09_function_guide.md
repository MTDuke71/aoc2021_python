# Day 09 Function Guide — Smoke Basin

Source: [`src/day09.py`](../../src/day09.py) ·
Tests: [`tests/test_day09.py`](../../tests/test_day09.py) ·
Statement: [`day09.md`](day09.md)

Answers (accepted): **423** / **1198704**.

## 1. The problem

The input is a heightmap: a grid of digits 0-9. Part 1 asks for the *low
points* (cells strictly lower than all their up/down/left/right neighbours)
and sums height + 1 over them. Part 2 asks for the *basins*: everything that
drains down to each low point, where 9s are ridges that belong to nothing.
Multiply the three biggest basin sizes.

Trace on the statement example (5 x 10):

```text
2199943210      low points: (0,1)=1  (0,9)=0  (2,2)=5  (4,6)=5
3987894921      risk = 2 + 1 + 6 + 6 = 15
9856789892
8767896789      basins: 3, 9, 14, 9
9899965678      top three: 9 * 14 * 9 = 1134
```

The 5 at (2,2) is low because its neighbours are 8 (up), 6 (down), 8 (left)
and 6 (right); the 2 at (0,0) is not, because its right neighbour is 1.

## 2. Representation

`parse_input` returns `Grid = list[list[int]]`, indexed `grid[row][col]`. A
row that is not all ASCII digits, or rows of different width, raise
`ValueError`. Blank lines are skipped. `strip()` per line handles CRLF.

Cells are addressed by `(row, col)` tuples. The real input is 100 x 100:
206 low points, 2571 nines, 7429 other cells.

## 3. Function walkthrough

### `neighbours(grid, r, c)`

Yields the in-bounds cells among up, down, left, right: 2 for a corner, 3 for
an edge, 4 inside. Doing the bounds check here lets every caller ignore the
edge rule. Both parts share it.

### `low_points(grid) -> list[(row, col)]`

Every cell whose height is strictly below all its neighbours. Strict matters:
on a plateau of equal heights nobody is lower than anybody, so no cell
qualifies (`test_part1_edges`: `11/11` gives 0). A single-cell grid has no
neighbours, so `all([])` is true and it counts as low.

### `part1(grid)`

`sum(grid[r][c] + 1)` over the low points. Real input: 206 low points, **423**.

### `basin_sizes(grid) -> list[int]`

Flood fill from each low point with an explicit stack, stepping to any
unclaimed neighbour that is not a 9. A shared `claimed` set stops a cell being
counted twice. If a low point turns out to be already claimed, two minima sit
in one non-9 region, which breaks the premise that each basin has one low
point, so it raises `ValueError` rather than return a wrong count.

Trace on the statement's top-left basin, start (0,1)=1:

```text
(0,1)=1  neighbours: (0,0)=2 take, (0,2)=9 wall, (1,1)=9 wall
(0,0)=2  neighbours: (1,0)=3 take, (0,1) claimed
(1,0)=3  neighbours: (0,0) claimed, (2,0)=9 wall, (1,1)=9 wall
size = 3
```

### `part2(grid)`

Sort the sizes and multiply the last three with `math.prod`. Fewer than three
basins raises `ValueError`. Real input top three: 102, 104, 113, product
**1198704**.

## 4. Why it is correct

Part 2 leans on one shortcut: *a basin is a connected region of non-9 cells,
and each such region contains exactly one low point.* The statement defines a
basin by flowing downhill; the fill instead just never crosses a 9.

That holds on puzzle inputs by the statement's promise, but it is not a
theorem about every grid. `0101` has low points at both 0s, and the 1s join
them into one region, so the two "basins" would be double counted. So the
shortcut is checked, not claimed:

- `basin_sizes` raises if a low point lands in an already-filled region
  (`test_two_low_points_in_one_region_is_an_error`, using `0101`).
- `test_real_input_one_low_point_per_region` checks on the real input that
  the number of basins equals the number of low points (206) and that the
  sizes sum to every non-9 cell (7429 = 10000 - 2571).

Together those say every non-9 cell is in exactly one basin and every basin
has exactly one low point, on the input actually being solved.

## 5. Complexity

`low_points` visits each cell once (up to 4 comparisons). The fill visits each
non-9 cell once (4 neighbour checks). Both are O(R*C).

| phase | ms |
| --- | ---: |
| parse | 0.602 |
| part 1 | 10.118 |
| part 2 | 17.378 |
| total | 28.097 |

`bench.py -n 5 9`, best of 5 on the real input. Part 2 calls `low_points`
again (measured separately: 10.6 ms), so about 7.6 ms of its time is the fill
itself and the rest is repeating part 1's scan.

## 6. If I were writing this in Rust

A sketch of the shape; it was not compiled for this guide.

```rust
fn low_points(g: &[Vec<u8>]) -> Vec<(usize, usize)> {
    let (h, w) = (g.len(), g[0].len());
    let mut out = vec![];
    for r in 0..h {
        for c in 0..w {
            let v = g[r][c];
            let low = (r == 0 || v < g[r - 1][c])
                && (r + 1 == h || v < g[r + 1][c])
                && (c == 0 || v < g[r][c - 1])
                && (c + 1 == w || v < g[r][c + 1]);
            if low { out.push((r, c)); }
        }
    }
    out
}
```

- **Grid as `Vec<Vec<u8>>`**, or one flat `Vec<u8>` indexed `r * w + c`. Flat
  is the cache-friendly version, and what an embedded C reader would write.
- **Edges and `usize`.** `r - 1` at 0 panics in debug builds, so you guard
  with `r == 0 ||` as above. Python's `neighbours` generator does that job in
  one place.
- **Short-circuit `&&`** plays the role of Python's `all(...)`.
- **Flood fill** is a `Vec<(usize, usize)>` stack plus a `Vec<bool>` visited
  array rather than a set of tuples.

Embedded framing: this is a 4-neighbour stencil over a frame buffer, and the
edge cases are the usual border problem. A sentinel border of 9s would remove
the bounds checks, and 9 is already the "wall" value.

## 7. Possible optimization

None of these were measured; they are ideas, not facts.

**Pad with 9s.** A border of 9s around the grid removes every bounds check,
and cannot change the answer since a 9 is never low and never in a basin.

**One labelling pass.** Label connected non-9 regions in a single sweep
instead of finding low points and then filling from each.

**Share `low_points` between parts.** Part 2 repeats part 1's scan. Low points
are a derived structure that does not depend on which part asks, so building
them in `parse_input` would fit CLAUDE.md's rule. Left as is for readability.
