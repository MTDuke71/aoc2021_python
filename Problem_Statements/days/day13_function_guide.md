# Day 13 Function Guide — Transparent Origami

Source: [`src/day13.py`](../../src/day13.py) ·
Tests: [`tests/test_day13.py`](../../tests/test_day13.py) ·
Statement: [`day13.md`](day13.md)

Answers (accepted): **810** / **HLBUBGFR**.

## 1. The problem

The input has two sections: a list of dots `x,y` on a sheet of transparent
paper, then a list of instructions `fold along y=N` or `fold along x=N`.
A `y` fold brings the bottom half up over the top; an `x` fold brings the
right half over to the left. Dots that land on the same spot merge into
one.

- **Part 1:** how many dots are left after the first fold alone?
- **Part 2:** do every fold. The remaining dots spell eight capital
  letters; the answer is those letters.

Trace on the statement's example: 18 dots, then `fold along y=7`. The dot
at `(0, 14)` is 7 rows below the line, so it lands 7 rows above it, at
`(0, 0)`. `(0, 13)` lands at `(0, 1)`. Dots above the line stay put. Some
dots land on top of each other, and 17 remain. `fold along x=5` then leaves
16 dots: the outline of a 5×5 square.

Part 2 is the first day this year whose answer is **a string, not a
number**. CLAUDE.md's contract says `part2 -> int`; this day's `part2`
returns `str`, and `solve` returns `tuple[int, str]`. `bench.py` and
`check_locked` never look at the answer's type, so nothing else needed to
change.

## 2. Representation

`parse_input` returns `Paper = (frozenset[Dot], tuple[Fold, ...])`:

- **Dots** as a frozenset of `(x, y)`. The first fold lines (x=655,
  y=447) imply a 1311×895 sheet, and it holds 983 dots, so a grid would be
  99.9% empty. A set also handles the "overlapping dots merge" rule for
  free: two dots folded onto the same spot are one element when they go
  back into the set.
- **Folds** as `("x" | "y", line)` in input order.

Real input: 983 dots, 12 folds.

## 3. Function walkthrough

### `parse_input(raw) -> Paper`

`splitlines()` plus a per-line `strip()`, so CRLF input leaves no `\r`.
Blank lines are skipped. A line starting with `fold along ` is a fold;
anything else must be `x,y` with both parts non-negative integers.

`ValueError` on: a fold axis other than `x`/`y`, a missing or non-numeric
fold line, a malformed dot, or a dot after the first fold instruction.

### `fold(dots, (axis, line)) -> frozenset[Dot]`

For each dot, take the coordinate on the fold axis, `c`:

- `c < line`: the dot is on the kept side and does not move.
- `c > line`: reflect it, `c → 2·line − c`.

The two error cases are refused, not guessed:

- `c == line`: the statement promises this never happens.
- `c > 2·line`: the folded part is longer than the kept part, and the dot
  would land at a negative coordinate. The statement does not say what
  that means.

`test_real_input_folds_are_well_formed` runs all 12 real folds, which
shows the real input hits neither case.

### `part1(parsed) -> int`

`len(fold(dots, folds[0]))`. Real input: **810**.

### `fold_all(parsed) -> frozenset[Dot]`

Applies every fold in order. On the real input the dot count goes:

| fold | x=655 | y=447 | x=327 | y=223 | x=163 | y=111 | x=81 | y=55 | x=40 | y=27 | y=13 | y=6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| dots after | 810 | 685 | 560 | 461 | 377 | 314 | 255 | 207 | 167 | 140 | 123 | 103 |

### `sheet_size(parsed) -> (width, height)`

The last fold along an axis keeps everything before its line, so that line
*is* the finished size on that axis. On the real input the last `x` fold is
40 and the last `y` fold is 6: a 40×6 sheet, which is eight letters of 5
columns each. An axis that was never folded is as wide as its furthest dot.

Sizing from the folds rather than the dots matters on the example. Its
finished square leaves the bottom two rows empty, and the statement draws
them. Sizing by the furthest dot would drop them.
`test_example_render_matches_statement_including_blank_rows` checks this.

### `render(dots, width, height) -> list[str]`

`height` rows of `#` and `.`, each `width` wide.

### `read_letters(rows) -> str`

The letters are 4 columns wide and 6 tall, with one blank column after
each one. `read_letters` cuts the strip into 5-column cells and looks up
the left 4 columns of each cell in `GLYPHS`, which maps a 6-tuple of row
strings to a letter.

It raises `ValueError` if:

- the strip isn't 6 rows tall, or its width isn't a multiple of 5;
- a cell's fifth column isn't blank;
- a cell isn't in `GLYPHS`. The message includes both the cell and the
  whole picture, so the letter can be read by eye.

**`GLYPHS` holds only the 7 letters this input uses: H, L, B, U, G, F, R.**
Each one was copied from the real input's rendering, not recalled from
memory. A shape nobody here has seen would be an unverified table entry.
An input that needs a new letter raises with the picture, and the letter
gets read and added at that point.

### `part2(parsed) -> str`

`read_letters(render(fold_all(parsed), *sheet_size(parsed)))`.

The real input, folded:

```text
#..#.#....###..#..#.###...##..####.###..
#..#.#....#..#.#..#.#..#.#..#.#....#..#.
####.#....###..#..#.###..#....###..#..#.
#..#.#....#..#.#..#.#..#.#.##.#....###..
#..#.#....#..#.#..#.#..#.#..#.#....#.#..
#..#.####.###...##..###...###.#....#..#.
```

**HLBUBGFR**. `test_real_picture` pins this picture.
`test_read_real_picture` decodes it without needing the input file.

## 4. Why it is correct

**A fold is a reflection.** Folding along `y = L` maps each row to its
mirror across the line: a dot `d` rows below the line ends up `d` rows above
it. Row `L + d` goes to `L − d`, which is `2L − (L + d)`. The other
coordinate is unchanged. So the fold is `c → 2L − c` on one axis, applied
only to dots past the line.

**Merging is set union.** "Overlapping dots count once" means the result
is the *set* of positions occupied after the reflection. `fold` builds
exactly that set.

**The arithmetic matches a literal fold.** `grid_fold` in the tests
implements the statement directly, with no reflection formula. It takes a
2D boolean grid, cuts it at the line, flips the far half and ORs it onto
the near half. `test_set_fold_matches_grid_fold` runs every fold on both
representations and compares them after each step, on the example and on
all 12 real folds.

**The pictures match the statement.** The example's dots after each fold
equal the `#` cells of the statement's two pictures.

## 5. Complexity

Each fold touches every surviving dot once: O(n) per fold, and O(n · f)
for all of them. The real input does 5082 dot visits across 12 folds (the
sum of the counts going into each fold). Rendering is 40 × 6 = 240 set
lookups, and reading is 8 tuple-key lookups.

| phase | ms |
| --- | ---: |
| parse | 0.343 |
| part 1 | 0.114 |
| part 2 | 0.836 |
| total | 1.293 |

`bench.py -n 5 13`, best of 5 on the real input. Inside part 2, measured
separately (best of 20): `fold_all` 0.708 ms, `render` 0.016 ms,
`read_letters` 0.011 ms. Part 2 is almost all folding. The first fold alone
(part 1, 983 dots) costs 0.114 ms, and the next 11 folds handle the
remaining 4099 dot visits.

Parse costs more than part 1 because it does more work per line: string
`startswith`, `partition`, two `isdigit` checks and two `int` calls, then a
set insert.

## 6. If I were writing this in Rust

A sketch of the shape; it was not compiled for this guide.

```rust
#[derive(Clone, Copy)]
enum Axis { X, Y }

fn fold(dots: &mut Vec<(u16, u16)>, axis: Axis, line: u16) {
    for d in dots.iter_mut() {
        let c = match axis { Axis::X => &mut d.0, Axis::Y => &mut d.1 };
        if *c > line { *c = 2 * line - *c; }
    }
    dots.sort_unstable();
    dots.dedup();
}
```

- **`u16` is enough.** The largest dot coordinate is 1307 and the sheet
  edge is 1310. `2·line − c` never goes negative once the parser has
  rejected `c > 2·line`, so unsigned arithmetic stays in range.
- **Vec plus sort/dedup instead of a hash set.** Fold everything in place,
  then sort and dedup once. With 983 dots this is a small sort that stays in
  cache, and there is no hashing at all. Strictly, part 2 doesn't need a
  dedup until the very end: duplicates don't change the final picture. Only
  part 1's count needs them removed.
- **Glyphs as integers.** A 4×6 letter is 24 bits. Pack each cell into a
  `u32` (row-major, `#` = 1) and `GLYPHS` becomes a `match` on constants.
  This is the most natural embedded framing of the day: each letter is a
  24-bit bitmap, and decoding is a compare against a ROM table.

The other embedded framing: a fold is `c' = L − |c − L|`. It needs no
branch, because dots on the kept side satisfy it too (`c < L` gives
`L − (L − c) = c`). `test_reflection_is_line_minus_distance` checks this
form against `fold` for every coordinate up to `2L`.

## 7. Possible optimization

**Compose the folds instead of applying them one by one.** Each fold is a
function of one coordinate, so the 12 folds collapse into two independent
maps, one per axis: x goes through the 6 `x` folds and y through the 6 `y`
folds. Each dot can then be sent to its final position directly, with one
set build at the end instead of twelve. This was not measured. Part 2 is
0.84 ms, so it would save very little, and the step-by-step version matches
the statement's own pictures.

**Skip the glyph table.** `render` alone is enough for a human to read the
answer, and many AoC solutions stop there and print the picture. The table
is what lets `solve` return a value that `LOCKED` can assert. Without it,
the regression test would have to compare pictures, which
`test_real_picture` already does.
