 

# Day 20 Function Guide — Trench Map

Source: [`src/day20.py`](../../src/day20.py) ·
Tests: [`tests/test_day20.py`](../../tests/test_day20.py) ·
Statement: [`day20.md`](day20.md) ·
Stepper: [`day20_stepper.html`](day20_stepper.html) (single-steps the
enhancement and decodes any pixel's window; the example is built in, paste
your input to see the background flip)

Answers (accepted): **4964** / **13202**.

## 1. The problem

The input has two sections:

1. A 512-character lookup table of `#` (light) and `.` (dark), the
   "image enhancement algorithm". The example wraps it over several lines;
   the real input has it on one.
2. A small image (100×100 in the real input) sitting in an **infinite**
   plane of dark pixels.

One enhancement step replaces every pixel at once. For each pixel, read the
3×3 window centred on it row by row, top-left first, as a 9-bit number with
`#` = 1. The new pixel is `table[n]`.

The statement's trace for the centre pixel of the example:

```
# . . # .
#[. . .].      row 1: . . .  -> 000
#[# . .]#      row 2: # . .  -> 100
.[. # .].      row 3: . # .  -> 010
. . # # #
```

`000 100 010` is `0b000100010 = 34`, and `table[34]` is `#`, so the centre
pixel becomes light.

- **Part 1:** lit pixels after 2 steps (example: 35).
- **Part 2:** lit pixels after 50 steps (example: 3351).

## 2. The trap: the infinite background flips

Far from the image, every window is uniform. All dark means `n = 0`, all
light means `n = 511`. So after one step the *entire* infinite outside
becomes `table[0]`, and after the next step it becomes `table[0]` or
`table[511]` depending on what it was.

In the example, `table[0]` is `.`, so the outside stays dark forever and
the naive "outside is always dark" approach works. In the real input:

| step | outside before | window index | outside after                   |
| ---: | -------------- | -----------: | ------------------------------- |
|    1 | dark           |            0 | `table[0]` = **lit**    |
|    2 | lit            |          511 | `table[511]` = **dark** |
|    3 | dark           |            0 | lit                             |
|   … |                |              |                                 |

After an odd number of steps infinitely many pixels are lit. Both parts ask
about an even step count (2 and 50), so both answers are finite. Code that
treats the outside as always dark gets the example right and the real input
wrong: the pixels at the edge of the grid see dark neighbours that are
actually lit. `test_real_input_background_flips` pins the alternation over 4
steps.

If both `table[0]` and `table[511]` were `#`, the outside would light on
step 1 and never go dark, so no count would be finite. `parse_input`
refuses that table.

## 3. Representation

```python
@dataclass(frozen=True)
class Image:
    rows: tuple[tuple[int, ...], ...]   # finite grid of 0/1
    background: int = 0                  # value of every pixel outside it

class Puzzle(NamedTuple):
    algorithm: tuple[int, ...]           # 512 entries of 0/1
    image: Image
```

The infinite image is a finite grid **plus one bit**: everything outside
the grid is the same value. That holds at the start (all dark) and stays
true after every step, because every outside window is uniform.

Each step grows the grid by one pixel per side. A pixel just outside the
old grid has a window that reaches into it, so it can differ from the
background. A pixel two out sees only background. After 50 steps the
100×100 grid is 200×200.

Pixels are ints rather than bools so they can be shifted straight into the
index.

## 4. Function walkthrough

### `parse_input(raw) -> Puzzle`

Strips every line (CRLF-safe), splits at the first blank line, and joins the
algorithm lines, so the wrapped example and the one-line real input parse
the same way. Refuses: no blank line, an algorithm that isn't 512 entries, a
character other than `#`/`.`, an empty or ragged image, and the
permanently-lit table described above.

### `triples(row) -> list[int]`

The 3-bit code of every horizontal window in a row:

```
row      = [0, 1, 1, 0, 1]
triples  = [011, 110, 101] = [3, 6, 5]
```

`out[c]` covers `row[c..c+2]`, so the output is two shorter than the row.

### `enhance(image, algorithm) -> Image`

1. Pad the grid by **two** pixels of background on every side. The output
   grid is one larger per side than the input, and every output pixel's
   window has to sit inside the padded array. Output pixel `(r, c)` is
   centred on padded pixel `(r+1, c+1)`.
2. `codes = [triples(row) for row in padded]`: one 3-bit code per
   horizontal window.
3. Output pixel `(r, c)` is `algorithm[top << 6 | mid << 3 | bot]`, where
   `top`, `mid`, `bot` are `codes[r][c]`, `codes[r+1][c]`, `codes[r+2][c]`.
   That is the statement's "read three rows of three, MSB first", with each
   row's three bits computed once and shared by the three output rows that
   use it.
4. New background: `algorithm[511 * bg]`, i.e. `algorithm[0]` if the
   outside was dark, `algorithm[511]` if it was lit.

### `enhance_n(image, algorithm, steps)` / `lit(image)`

`enhance_n` loops. `lit` sums the grid, and raises if the background is
lit, since that count is infinite.

### `part1` / `part2`

`lit(enhance_n(..., 2))` and `lit(enhance_n(..., 50))`. Part 2 redoes part 1's
two steps; sharing them would save about 4 ms of 214.

## 5. Why it is correct

- **Grid plus background is exact.** Induction on steps. At step 0 every
  pixel outside the grid is dark. If every pixel outside the grid equals
  `bg`, then every pixel two or more out from the grid has a uniform window
  and becomes `table[511·bg]`. The pixels one out are inside the grown
  grid and are computed explicitly. So after the step every pixel outside
  the new grid equals the new background.
- **The index is the statement's.** `top << 6 | mid << 3 | bot` with each
  row read left to right as 3 bits is the 9-bit row-major number. Pinned
  directly by `test_statement_index_34`.
- **Checked against a literal simulation.** The tests' `literal_lit` builds
  a dict over a window with 3·steps of margin and does nine lookups per
  pixel, exactly as worded. It agrees on lit count and background for 20
  random images over 1–4 steps (half with a flipping table), for the real
  input at 2 steps (part 1) and at 10 steps. The statement's two 15×15
  pictures are matched character for character.

Lit counts on the real input after even steps, as measured: 4964 after 2,
6062 after 10, 13202 after 50.

## 6. Complexity

Let `S` be the step count and `n` the starting side (100). Step `k` computes
a `(n+2k)²` grid, so the total is Σ(n+2k)² for k = 1..S: about
**1.18 million pixels** for part 2 (measured), O(S·(n+S)²). Each pixel is a
few shifts and ORs and one table lookup, after one pass per row to build
its codes.

| phase  |      ms |
| ------ | ------: |
| parse  |   0.417 |
| part 1 |   3.982 |
| part 2 | 214.294 |
| total  | 218.693 |

`bench.py 20`, best of 5 on the real input.

Part 2 is 54× part 1 because it covers 1.18M pixels against part 1's
21,220 (102² + 104²).

For comparison, the same grid-plus-background approach with nine bounds-checked
lookups per pixel took **1435 ms** for 50 steps against 221 ms for the
row-code version (best of 3, same answer). The shared row codes are
about 6.5× faster.

## 7. If I were writing this in Rust

A sketch; it was not compiled for this guide.

```rust
struct Image { rows: Vec<Vec<u8>>, background: u8 }

fn enhance(img: &Image, alg: &[u8; 512]) -> Image {
    let bg = img.background;
    let w = img.rows[0].len() + 4;
    let pad = |r: Option<&Vec<u8>>| -> Vec<u8> {
        let mut v = vec![bg; w];
        if let Some(row) = r { v[2..w - 2].copy_from_slice(row); }
        v
    };
    let padded: Vec<Vec<u8>> = [None, None].into_iter()
        .chain(img.rows.iter().map(Some))
        .chain([None, None])
        .map(pad)
        .collect();
    // 3-bit horizontal codes: a 3-bit shift register run along each row.
    let codes: Vec<Vec<u16>> = padded.iter()
        .map(|row| row.windows(3).map(|t| (t[0] << 2 | t[1] << 1 | t[2]) as u16).collect())
        .collect();
    let rows = codes.windows(3)
        .map(|c| (0..c[0].len()).map(|i| alg[(c[0][i] << 6 | c[1][i] << 3 | c[2][i]) as usize]).collect())
        .collect();
    Image { rows, background: alg[if bg == 1 { 511 } else { 0 }] }
}
```

- **It's a 9-bit shift register.** The window index is three 3-bit row
  registers concatenated. In hardware terms it's a 3×3 convolution
  addressing a 512×1 ROM. `windows(3)` on both axes is the Rust spelling.
- **`[u8; 512]` for the table.** The length is part of the type, so the
  bounds check on `alg[idx]` can't fail for a 9-bit `idx` (the compiler may
  still emit it).
- **Background as a field, not an `Option`.** It's always defined; the
  only failure (infinite lit count) belongs in `lit()` returning
  `Option<usize>` or `Result`.

## 8. Possible optimization

**Rows as big integers.** Pack each padded row into one Python int (bit
`c` = pixel `c`). Then `(row >> c) & 7` is the triple at column `c` without
building a list, and the three-row index is still `top << 6 | mid << 3 | bot`.
It removes the `triples` lists but leaves a Python-level loop per pixel, so
the gain is likely modest. Not measured.

**Only track lit pixels.** A set of lit coordinates is the textbook
representation, but with a flipping background "lit" means different
things on odd and even steps. You end up storing "pixels that differ from
the background" and flipping the meaning each step. It is no faster than
the grid, since about a third of the 200×200 grid is lit at the end
(13202 of 40,000).

**numpy.** With a 2-D array, the index is the sum of nine shifted slices
times powers of two, and the lookup is `alg[index]` in one fancy-index.
That moves the per-pixel loop into C and would likely be much faster. Not measured; numpy isn't a
dependency of this repo, and 214 ms is fine.
