# Day 05 Function Guide — Hydrothermal Venture

Source: [`src/day05.py`](../../src/day05.py) ·
Tests: [`tests/test_day05.py`](../../tests/test_day05.py) ·
Statement: [`day05.md`](day05.md)

Answers (accepted): **5167** / **17604**.

## 1. The problem

The input is a list of line segments on an integer grid, `x1,y1 -> x2,y2`,
both endpoints included. A point is dangerous when two or more segments
cover it.

- **Part 1:** count the dangerous points, using only horizontal and
  vertical segments.
- **Part 2:** the same count, using every segment. The statement promises
  that the extra segments are diagonals at exactly 45 degrees.

Trace on the example's second segment, `8,0 -> 0,8`. dx = -8 and dy = +8,
so each step is (-1, +1), and there are max(|dx|, |dy|) = 8 steps after
the start:

```text
(8,0) (7,1) (6,2) (5,3) (4,4) (3,5) (2,6) (1,7) (0,8)     9 points
```

Walk every segment the same way and count visits per point. Point (4,4)
is visited three times: by this segment, by `9,4 -> 3,4` (horizontal) and
by `0,0 -> 8,8` (the other diagonal). That is the `3` in the middle of
row 4 of the statement's part 2 diagram:

```text
row 4, part 1:  .112111211      (4,4) = 1: only the horizontal counts
row 4, part 2:  .112313211      (4,4) = 3, (6,4) = 3
```

In part 1 the two diagonals are ignored, so (4,4) drops to 1. The answer
is the number of points with a count of 2 or more: 5 in the example for
part 1, 12 for part 2.

## 2. Representation

`parse_input` returns `list[Segment]`, where `Segment` is a
`NamedTuple(x1, y1, x2, y2)` holding the endpoints as written. It does not
reorder them or put the smaller coordinate first. The walk works in
either direction, so normalizing would only lose information. On the real
input, 254 of the 500 segments run "backwards" (x decreasing, or y
decreasing on a vertical).

Nothing more is derived at parse time. The coverage counts depend on which
part is asking, since part 1 filters and part 2 does not, so they are
built per part.

Coverage is a `Counter[(x, y)]`, a sparse map from point to visit count.
The real input spans coordinates 10–990, so a dense 1000x1000 grid would
also work. Section 7 measures that alternative.

The real input is 500 segments: 166 horizontal, 172 vertical and 162 exact
45-degree diagonals. None is at any other angle, and none is a single
point. Segment lengths run from 2 to 974 points, 366 on average.

## 3. Function walkthrough

### `Segment.axis_aligned`

`x1 == x2 or y1 == y2`. This is part 1's filter. A zero-length segment
(one point) counts as axis-aligned, which is the only sensible reading: a
single point is also a length-0 horizontal line.

### `sign(n) -> int`

`(n > 0) - (n < 0)`: -1, 0 or +1. Python has no built-in signum for ints.
The bool subtraction is the usual idiom.

### `points(seg) -> Iterator[Point]`

The walk from section 1:

1. dx, dy = end minus start.
2. If both are non-zero and |dx| != |dy|, raise. The segment is at some
   other angle, and a unit step would walk the wrong points (see
   section 4).
3. Step (sign dx, sign dy), max(|dx|, |dy|) + 1 times, starting at
   (x1, y1).

The `+ 1` is the "both ends included" rule. A zero-length segment gives
one point, not zero (`test_points`).

It is a generator. Points go straight into the `Counter` and are never
stored as a list per segment.

### `parse_input(raw) -> list[Segment]`

Strips each line, which removes CRLF's `\r`, and skips blanks. Each line
must `fullmatch` `\d+,\d+ -> \d+,\d+`, with the whitespace around the
arrow optional. `fullmatch` rather than `search` means trailing junk like a
second arrow is rejected, not silently ignored
(`test_malformed_input_is_an_error`).

### `overlaps(segments) -> int`

Walks every segment into one `Counter`, then counts the values that are
>= 2. It takes any iterable, so part 1 can hand it a generator
expression.

### `part1` and `part2`

```python
part1:  overlaps(s for s in segments if s.axis_aligned)
part2:  overlaps(segments)
```

Part 2 is part 1 without the filter. The work for part 2 was already in
place: `points` handled 45-degree lines from the start, because the part 1
input already contained them and needed some rule for them.

## 4. Why it is correct

**The walk visits exactly the covered grid points.** Take a segment with
|dx| = |dy| = n, or with one of them 0 and the other n. Points
(x1 + i*sx, y1 + i*sy) for i = 0..n are all on the segment, all distinct,
and include both ends. Could the walk miss one? A covered integer point
must be collinear with the ends and between them. On a horizontal or
vertical line, the integer points between the ends are exactly the n + 1
the walk visits. On a 45-degree line, x and y change together one-for-one,
so a point on it with integer x is at i = |x - x1| and has integer y too.
Again there are n + 1 of them.

At any other angle this breaks. `0,0 -> 2,1` has a unit step of (1, 1),
which would reach (2, 2), a point not on the segment at all. That is why
`points` raises instead.

`test_unit_step_walk_is_exactly_the_lattice_points` pins this, per the
standing rule. On 300 seeded random segments (horizontal, vertical, both
diagonal slopes, both directions, including zero length), it compares the
walk with a brute-force scan of the bounding box. The scan keeps every
integer point that passes a cross-product collinearity test. The test
also checks the walk has no repeats and starts and ends on the endpoints.

**Only grid points count.** `0,0 -> 1,1` and `0,1 -> 1,0` cross at
(0.5, 0.5). Geometrically they intersect, but neither covers an integer
point the other covers, so there is no overlap. The statement's diagrams
count grid cells, and this matches them
(`test_diagonals_crossing_between_lattice_points_do_not_overlap`).

**Counting points, not pairs.** A point covered by three segments is one
dangerous point, not three pairs (`test_overlap_counts_points_not_pairs`).
Counting values >= 2 in the `Counter` gets this for free.

**The example diagrams are reproduced exactly.** `render` in the tests
draws the `Counter` as the statement does. `test_example_axis_diagram` and
`test_example_full_diagram` compare both 10x10 pictures character for
character. That checks every cell of the example, not just the totals 5
and 12.

## 5. Complexity

Work is one hash-map update per point walked, so O(total segment length),
plus a scan of the distinct points.

| | part 1 | part 2 |
| --- | ---: | ---: |
| segments | 338 | 500 |
| points walked | 107,142 | 182,975 |
| distinct points | 101,811 | 163,877 |
| covered >= 2 | 5,167 | 17,604 |
| max coverage | 4 | 5 |

Coverage is thin. In part 2, 146,273 points are covered once, 16,202
twice, 1,315 three times, 82 four times and 5 five times.

`bench.py 5`, best of 5 on the real input:

| phase | ms |
| --- | ---: |
| parse | 0.444 |
| part 1 | 23.981 |
| part 2 | 41.408 |
| total | 65.832 |

This is the first day where the parts outweigh the parse, and time scales
with points walked. Part 2 walks 1.71x as many points as part 1 and takes
1.73x as long, about 224–226 ns per point in both. Part 2 re-walks the
338 axis segments that part 1 already walked. `solve` pays for that; the
alternative is in section 7.

Timed separately (`timeit`, best of 5 repeats of 5), just generating
part 2's points and discarding them takes 20.0 ms of the 39.1 ms part 2
took in that run, 51%. About half the cost is the generator producing
tuples, and half is hashing them into the `Counter`.

## 6. If I were writing this in Rust

Compiled and run while writing this guide (rustc 1.93.1, edition 2021,
`-O`). It gives 5 / 12 on the example and 5167 / 17604 on the real input.

```rust
#[derive(Debug, Clone, Copy)]
struct Segment { x1: i32, y1: i32, x2: i32, y2: i32 }

impl Segment {
    fn axis_aligned(&self) -> bool { self.x1 == self.x2 || self.y1 == self.y2 }

    fn points(&self) -> impl Iterator<Item = (i32, i32)> {
        let (dx, dy) = (self.x2 - self.x1, self.y2 - self.y1);
        assert!(dx == 0 || dy == 0 || dx.abs() == dy.abs(), "{self:?} is not 0/45/90 degrees");
        let (sx, sy) = (dx.signum(), dy.signum());
        let (x1, y1) = (self.x1, self.y1);
        (0..=dx.abs().max(dy.abs())).map(move |i| (x1 + i * sx, y1 + i * sy))
    }
}

fn overlaps<'a>(segs: impl Iterator<Item = &'a Segment>) -> usize {
    let mut cover: HashMap<(i32, i32), u32> = HashMap::new();
    for s in segs {
        for p in s.points() {
            *cover.entry(p).or_insert(0) += 1;
        }
    }
    cover.values().filter(|&&n| n >= 2).count()
}

// part 1: overlaps(segs.iter().filter(|s| s.axis_aligned()))
// part 2: overlaps(segs.iter())
```

The things worth noting:

- **`i32::signum` is built in.** The Python needs its own `sign`.
- **Signed coordinates on purpose.** The input is all non-negative, so
  `u32` looks natural. But dx and dy are differences and go negative, and
  `(x1 + i * sx)` with `sx = -1` would need casts everywhere. `i32`
  throughout avoids that.
- **`0..=n` is the "both ends included" rule.** The Python writes it as
  `range(n + 1)`. In Rust the inclusive range says it directly, and
  forgetting the `=` is the same off-by-one as forgetting the `+ 1`.
- **`impl Iterator` + `move` closure** is the Python generator: lazy, and
  no per-segment `Vec`. The `move` copies `x1, y1, sx, sy` into the
  closure so the iterator doesn't borrow `self`.
- **`entry(p).or_insert(0) += 1`** is `Counter`'s `+= 1`: one lookup that
  inserts if missing.

For an embedded framing: `points` is Bresenham's line algorithm for the
three slopes where it never has to make a decision. The error term is
always zero, so the step is a constant (±1, ±1) and the inner loop is two
adds. Any other slope would need the error accumulator, which this puzzle
never asks for.

## 7. Possible optimization

The day runs in about 66 ms. That is slow next to days 01–04, but there
is no real need to change it. Two measured alternatives:

**Dense grid instead of a `Counter`.** A 1000x1000 `bytearray` indexed by
`y * 1000 + x`, counting a point as dangerous on the visit that takes it
to exactly 2. It gives the same 17604, and on part 2 it takes 31.9 ms
against the `Counter`'s 39.1 ms in the same run (best of 5 repeats of 5),
about 18% faster. The saving is modest because the walk itself, not the
hash, is half the cost. It also bakes the coordinate range into the code,
which the puzzle never promises.

**Walk each segment only once for `solve`.** Part 2's coverage is part 1's
coverage plus the diagonals. Two `Counter`s (axis, diagonal) built once
would let part 1 read the first and part 2 merge the second in. That cuts
`solve`'s walked points from 290,117 (107,142 + 182,975) to 182,975. It is
not done because it moves part-specific work into parse, and it couples
the parts for a saving of roughly the part 1 time.

Beyond that, the real speedup is not walking points at all: intersect the
segments pairwise and handle collinear overlaps as interval arithmetic.
That is O(n²) in segments (125k pairs) rather than O(total length), but
it has fiddly cases: collinear overlaps, three segments meeting at one
point, and diagonals crossing between grid points (section 4). For
coordinates under 1000 the brute-force walk is the right tool.
