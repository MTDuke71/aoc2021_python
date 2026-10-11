# Day 11 Function Guide — Dumbo Octopus

Source: [`src/day11.py`](../../src/day11.py) ·
Tests: [`tests/test_day11.py`](../../tests/test_day11.py) ·
Statement: [`day11.md`](day11.md)

Answers (accepted): **1683** / **788**.

## 1. The problem

A 10x10 grid of octopuses, each with an energy level 0–9. One step:

1. every octopus gains 1;
2. any octopus above 9 flashes, giving each of its eight neighbours
   (diagonals count) another 1, which can push them above 9 too;
3. every octopus that flashed drops to 0.

An octopus flashes at most once per step. Part 1 counts the flashes over
100 steps. Part 2 asks for the first step on which all 100 flash together.

Trace on the statement's small grid, one step:

```text
start     after +1        cascade                          after reset
11111     2  2  2  2  2   the eight 10s flash; each one    34543
19991     2 10 10 10  2   bumps its neighbours.  The       40004
19191     2 10  2 10  2   centre takes 8 bumps: 2 -> 10,   50005
19991     2 10 10 10  2   so it flashes as well.           40004
11111     2  2  2  2  2   9 flashes in all.                34543
```

The top-left corner touches one ring cell (2 + 1 = 3), its right-hand
neighbour touches two (4), the top-middle cell three (5). The centre began
the step at 1 and still flashed: that is the cascade.

## 2. Representation

`parse_input` returns `Grid = list[list[int]]`, one row of ints per line,
the same shape as day 9. There is no derived structure worth building at
parse time: both parts are simulations from the starting grid.

`step` mutates the grid in place, so `part1` and `part2` each take a
row-by-row copy first. Without that, part 2 would start from part 1's
step-100 grid and report an answer 100 too small. Pinned by
`test_part1_does_not_mutate_parsed` and `test_part2_does_not_mutate_parsed`.

During the cascade a cell's energy is allowed to run past 9. It is not
clamped, and there is no separate "has flashed" set: energy above 9 *is*
the flag.

## 3. Function walkthrough

### `parse_input(raw) -> Grid`

`splitlines()` plus a per-line `strip()`, so CRLF input leaves no `\r`.
Blank lines skip. A non-digit or a ragged row raises `ValueError`.

### `neighbours(grid, r, c)`

Yields the in-bounds cells of the 3x3 block around `(r, c)`, minus the
centre: 8 for an interior cell, 5 on an edge, 3 in a corner.

### `step(grid) -> int`

Three loops, one per phase of the statement:

1. Add 1 to every cell. A cell that lands on exactly 10 goes on the
   `flashing` stack.
2. Pop a cell, count one flash, add 1 to each neighbour. A neighbour that
   lands on exactly 10 goes on the stack.
3. Set every cell above 9 to 0.

Returns the flash count for the step.

### `part1(parsed)`

Copy the grid, call `step` 100 times, sum the returns. Real input: **1683**.

### `part2(parsed)`

Copy the grid and call `step` until one call returns the number of cells;
the answer is how many calls that took. Real input: **788**.

Before each step it stores the grid as a tuple of tuples in `seen` and
raises `ValueError` if the state is already there. See section 4 for why
that is the right stopping rule. An empty grid raises too, since "all zero
of them flashed" would otherwise answer 1.

## 4. Why it is correct

**Once per step.** A cell is pushed when its energy becomes *exactly* 10.
Within a step energy only goes up (the reset is phase 3), so each cell
passes through 10 at most once and is pushed at most once. A cell that has
already flashed keeps absorbing bumps (11, 12, ...) without re-entering
the stack. `test_octopus_flashes_once_per_step` pins it on a 3x3 of 9s: 9
flashes, not more, though the centre is bumped 8 times after flashing.

**Order does not matter.** The stack pops in an arbitrary order, but a
cell's final energy for the step is its start + 1 + the number of
neighbours that flashed, whatever the order, and it flashes exactly when
that exceeds 9. So the set of flashers is the same for any pop order; a
queue would give the same answer.

**Reset after, not during.** If a flasher were zeroed as it flashed, a
later neighbouring flash would lift it to 1. `test_flashed_octopus_stays_at_zero`
pins this on `98`: the 9 flashes, pushes the 8 over, and must still end
at 0.

**Counting.** A flasher ends the step at 0; a non-flasher gained at least
1, so it cannot. The number of zeros after a step therefore equals the
flash count, which gives an independent check on `step`'s return value:
`test_step_flash_count_matches_zeros` runs it for 100 steps of the example.

**Part 2 terminates.** Nothing guarantees an arbitrary grid ever
synchronises. The two-cell grid `05` does not:

```text
05 -> 16 -> 27 -> 38 -> 49 -> 60 -> 71 -> 82 -> 93 -> 05
                          left flashes         right flashes
```

It is back where it started after 9 steps, with the cells having flashed
on different steps. The grid has finitely many states and `step` is
deterministic, so every run either hits a full flash or revisits a state,
and a revisit means the run loops forever without one. `part2` raises on
the revisit. Pinned by `test_part2_grid_that_never_synchronises_is_an_error`.

**After synchronising.** A full flash leaves all zeros, and from all zeros
the grid is quiet for nine steps and flashes in full on the tenth, forever.
Pinned by `test_synchronised_grid_flashes_every_10_steps`.

Statement checks pinned: the example grids after steps 1, 2, 3, 10, 100,
193, 194 and 195; 204 flashes after 10 steps; 1656 after 100; first full
flash at 195, with no earlier step reaching 100.

## 5. Complexity

A step touches all 100 cells twice (increment, reset) and does up to 8
neighbour bumps per flash. Part 1 is 100 steps; part 2 is 788 steps on
the real input, during which 12583 octopuses flash and `step` makes 86779
neighbour bumps.

| phase | ms |
| --- | ---: |
| parse | 0.008 |
| part 1 | 3.769 |
| part 2 | 29.081 |
| total | 32.858 |

`bench.py -n 5 11`, best of 5 on the real input. Part 2 is 7.7x part 1
for 7.88x the steps, so cost is per step. Part 2 re-simulates the first
100 steps that part 1 already ran; see section 7.

On the real input 132 of the 788 steps have no flash at all, and the
busiest step before the last one has 97 flashes.

## 6. If I were writing this in Rust

A sketch of the shape; it was not compiled for this guide.

```rust
type Grid = [[u8; 10]; 10];

fn step(g: &mut Grid) -> usize {
    let mut stack = Vec::with_capacity(100);
    for r in 0..10 {
        for c in 0..10 {
            g[r][c] += 1;
            if g[r][c] == 10 { stack.push((r, c)); }
        }
    }
    let mut flashes = 0;
    while let Some((r, c)) = stack.pop() {
        flashes += 1;
        for (nr, nc) in neighbours(r, c) {
            g[nr][nc] += 1;
            if g[nr][nc] == 10 { stack.push((nr, nc)); }
        }
    }
    for cell in g.iter_mut().flatten() {
        if *cell > 9 { *cell = 0; }
    }
    flashes
}
```

- **Fixed array, `Copy`.** `[[u8; 10]; 10]` is 100 bytes on the stack and
  `Copy`, so "each part works on its own copy" is a plain `let mut g = grid;`
  rather than the Python row-by-row copy.
- **Width.** A cell peaks at 18 inside a cascade: 10 when it flashes plus
  8 neighbours. The real input does reach 18. `u8` has room to spare, and
  a 5-bit field would do.
- **`&mut Grid` in the signature.** The in-place mutation that the Python
  only documents in a comment is visible in the type.
- **Neighbour bounds.** `usize` cannot go negative, so `r - 1` at row 0
  panics in debug. `checked_sub`, or a one-cell border of sentinel cells
  (a 12x12 array), avoids per-neighbour bounds tests.
- **Cycle check.** `HashSet<Grid>` works directly, since arrays of `u8`
  are `Hash + Eq`.

Embedded framing: the "exactly 10" push is an edge-triggered interrupt,
not a level-triggered one. The cell stays above threshold for the rest of
the step, but only the rising edge through 10 queues work. The phase 3
reset is the clear-on-read at the end of the cycle.

## 7. Possible optimization

**Drop the `seen` set.** Measured on the real input: part 2 without the
cycle check runs in 28.1 ms against 28.9 ms with it (best of 5, `timeit`),
so the guard costs under 1 ms and stays.

The rest were not measured; they are ideas, not facts.

**One simulation for both parts.** Run a single loop, record the flash
total at step 100 and stop at the first full flash. That saves part 2 the
100 steps part 1 already did, but it only works when the full flash comes
after step 100, and it welds the two parts together against the
`part1(parsed)` / `part2(parsed)` convention.

**Flat list with a border.** A 12x12 flat list with a sentinel ring and
eight precomputed index offsets removes the bounds checks and the
generator in `neighbours`, which is where most of the per-bump cost is
likely to be.

**numpy.** Whole-grid increment and a convolution-style neighbour sum per
cascade round. Probably not a win at 10x10, where call overhead dominates.
