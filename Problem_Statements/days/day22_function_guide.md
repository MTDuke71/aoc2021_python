# Day 22 Function Guide — Reactor Reboot

Source: [`src/day22.py`](../../src/day22.py) ·
Tests: [`tests/test_day22.py`](../../tests/test_day22.py) ·
Statement: [`day22.md`](day22.md)

Answers (accepted): **587097** / **1359673068597669**.

## 1. The problem

A 3-D grid of unit cubes, one per integer `(x, y, z)`, all off to begin
with. The input is 420 reboot steps, each one `on` or `off` plus an
inclusive cuboid `x=a..b,y=c..d,z=e..f`. A step sets every cube in its
cuboid, and later steps override earlier ones. The answer is how many
cubes end up on.

- **Part 1.** Count only cubes in the initialisation region, −50..50 on
  every axis.
- **Part 2.** Count every cube.

The real input's coordinates reach ±98,724, and part 2's answer is
1.36·10¹⁵ cubes. A set of cubes is out of the question for part 2. One
algorithm, never touching individual cubes, serves both parts. Part 1
just clips the input first.

The real input is built like the statement's examples: steps 0–19 lie
fully inside the region, and steps 20–419 lie fully outside it (measured).
So part 1 is "run the first 20 steps", but the code doesn't rely on that.
It clips every step, and straddling steps are tested on random input.

## 2. Representation: a signed list of cuboids

The on-set is kept as a multiset of cuboids, each with an integer sign:

```
on-cubes  =  Σ sign(b) · [cube ∈ b]       for every box b in the list
count     =  Σ sign(b) · volume(b)
```

This is inclusion–exclusion, written down incrementally. For a new step
with cuboid **C**:

1. For each existing entry `(b, s)` that overlaps C, add `(b ∩ C, −s)`.
2. If the step is `on`, add `(C, +1)`.

After step 1, every cube inside C is counted zero times. Step 2 then
counts the cubes of C once if they are on. Cubes outside C are untouched
because every new entry lies inside C.

### Concrete trace: the statement's small example

Run, not worked out by hand (`count_on` on `SMALL`, printed after each
step):

```
on  10..12³    +1 10..12³ (27)                                   total 27
on  11..13³    +1 10..12³ (27)  −1 11..12³ (8)  +1 11..13³ (27)  total 46
off  9..11³    ... the above ...  −1 10..11³ (8)                 total 38
on  10..10³    ... the above ...  +1 10..10³ (1)                 total 39
```

Step 2: the old box overlaps C in 11..12³, which gets a −1 entry, and
then C is added. 27 − 8 + 27 = 46, the statement's 27 + 19.

Step 3 is more interesting. The `off` box 9..11³ overlaps all three entries:

| existing entry | ∩ 9..11³  | new entry |
| -------------- | --------- | --------- |
| +1 10..12³     | 10..11³   | −1        |
| −1 11..12³     | 11..11³   | +1        |
| +1 11..13³     | 11..11³   | −1        |

The two entries for the single cube `11,11,11` cancel. Because the list
is a `Counter` keyed by the box, they merge into a zero and get deleted.
What's left is one −1 entry of volume 8, giving 46 − 8 = 38, the
statement's "turning off 8 cubes".

Step 4 does the same thing in miniature. The cube `10,10,10` gets −1 from
the first box and +1 from the −1 10..11³ entry, which cancel, and then
+1 because it's an `on` step. Total 39.

### How to read an entry

An entry is a key–value pair, `signed[Cuboid(...)] = sign`. The key is a
region and the value is a sign (on the real input every final entry is +1
or −1: 1,893 and 1,951 of them, measured). An entry doesn't say "these
cubes are on". It's a **stamp** that adds its sign to every cube inside
it. A cube's on/off state is the sum of every stamp covering it, which is
always 0 or 1. A +1 region can contain off cubes if a −1 region also
covers them.

Two `Counter`s with the same shape are in play:

- **`signed`** is the running list, kept across steps.
- **`update`** is a scratch pad, created fresh each step. The step's
  cancelling entries and its `+C` go into `update`, computed against
  `signed` *as it was before the step*. Then
  [lines 109–112](../../src/day22.py) add each key into `signed`
  and delete any key that lands on 0.

An `off` step is just the cancelling entries without the final `+C`.
`if on:` is the only place the code reads the flag.

### A 3-D trace: four overlapping `on` steps

The first four lines of the part 2 example. Call them A, B, C, D. These
numbers are the code's own output, and the final total matches a
brute-force cube set (389,786).

```
A = x -5..47,  y -31..22, z -19..33    53 × 54 × 53 = 151,686
B = x -44..5,  y -27..21, z -14..35    50 × 49 × 50 = 122,500
C = x -49..-1, y -11..42, z -10..38    49 × 54 × 49 = 129,654
D = x -20..34, y -40..6,  z -44..1     55 × 47 × 46 = 118,910
```

**Step 1, on A.** The list is empty. `signed = {A: +1}`, total 151,686.

**Step 2, on B.** One overlap, computed one axis at a time:

```
x: -5..47  ∩ -44..5  = -5..5     11
y: -31..22 ∩ -27..21 = -27..21   49
z: -19..33 ∩ -14..35 = -14..33   48     → A∩B = 11 × 49 × 48 = 25,872
```

`update = {A∩B: −1, B: +1}`. Total 151,686 − 25,872 + 122,500 =
**248,314**. That's |A ∪ B| = A + B − A∩B.

**Step 3, on C.** C overlaps all three entries:

| existing entry | overlap with C                   | volume | add |
| -------------- | -------------------------------- | -----: | :-: |
| +A             | x -5..-1, y -11..22, z -10..33   |  7,480 | −1  |
| −(A∩B)         | x -5..-1, y -11..21, z -10..33   |  7,260 | +1  |
| +B             | x -44..-1, y -11..21, z -10..35  | 66,792 | −1  |

Plus `+C`. That gives 7 entries and a total of **310,956**. This is the
three-set formula, built incrementally:
A + B + C − A∩B − A∩C − B∩C + A∩B∩C. The +1 entry is the corner where
all three meet. Subtracting A∩C and B∩C took that corner away twice, so
it gets added back once.

**Step 4, on D.** D overlaps all seven entries:

| existing entry | overlap with D                      | volume | add |
| -------------- | ----------------------------------- | -----: | :-: |
| +A             | x -5..34, y -31..6, z -19..1        | 31,920 | −1  |
| −(A∩B)         | x -5..5, y -27..6, z -14..1         |  5,984 | +1  |
| +B             | x -20..5, y -27..6, z -14..1        | 14,144 | −1  |
| −(A∩C)         | **x -5..-1, y -11..6, z -10..1**    |  1,080 | +1  |
| +(A∩B∩C)       | **x -5..-1, y -11..6, z -10..1**    |  1,080 | −1  |
| −(B∩C)         | **x -20..-1, y -11..6, z -10..1**   |  4,320 | +1  |
| +C             | **x -20..-1, y -11..6, z -10..1**   |  4,320 | −1  |

Rows 4 and 5 are the same box with opposite signs, and so are rows 6 and
7. Inside D's slab, the part of C that overlaps A lies entirely inside B
as well, so A∩C∩D and A∩B∩C∩D come out identical. The same goes for
B∩C∩D and C∩D. Each pair sums to 0 in `update`, and the commit loop
drops it. Seven rows of work leave six `update` keys, two of them 0:

```
update = {A∩D: −1, A∩B∩D: +1, B∩D: −1, <x-5..-1 …>: 0, <x-20..-1 …>: 0, D: +1}
```

The final list:

| sign | box    |  contributes |
| :--: | ------ | -----------: |
|  +1  | A      |     +151,686 |
|  −1  | A∩B    |      −25,872 |
|  +1  | B      |     +122,500 |
|  −1  | A∩C    |       −7,480 |
|  +1  | A∩B∩C  |       +7,260 |
|  −1  | B∩C    |      −66,792 |
|  +1  | C      |     +129,654 |
|  −1  | A∩D    |      −31,920 |
|  +1  | A∩B∩D  |       +5,984 |
|  −1  | B∩D    |      −14,144 |
|  +1  | D      |     +118,910 |
|      | total  |  **389,786** |

The full four-set inclusion–exclusion formula has 15 terms, one per
non-empty subset of {A, B, C, D}. Here 11 survive, and every term is a
plain box. Merging equal boxes is what trims the formula. At the scale
of the real input, it's the difference between 3,844 entries and 47,492
(§5).

**Why it's no harder in 3-D than in 1-D:** a box is a segment swept
along y and then along z, so the overlap of two boxes is the
per-axis overlap of their three segments. That's always another box,
never an L-shape. The algorithm never has to picture the on-region
itself, which after 420 steps is a messy shape with holes. It only keeps
the stack of signed boxes.

## 3. Function walkthrough

### `Cuboid(x0, x1, y0, y1, z0, z1)`

A `NamedTuple`, so it's hashable and can be a `Counter` key. Ranges are
inclusive, as the statement words them.

- `volume()` = `(x1 − x0 + 1)(y1 − y0 + 1)(z1 − z0 + 1)`. The `+ 1` is the
  inclusive-range tax. `test_volume_is_inclusive` pins 1, 27 and 101³.
- `intersect(other)` takes the per-axis max of the lows and min of the
  highs, and returns `None` if any axis comes out empty. Boxes that touch
  face to face (`0..2` against `3..5`) share no cube, and that's a test case.

### `Step(on, box)` / `parse_input(raw) -> list[Step]`

One `fullmatch` regex per stripped line, so a trailing `\r` never reaches
it. Anything that doesn't match, or a range with lo > hi, raises
`ValueError`.

### `count_on(steps, region=None) -> int`

The algorithm from §2. Each step's updates are collected in a separate
`update` Counter against the *old* list, then merged in. Mutating
`signed` while iterating over it would be a Python error, and it would
also intersect C with its own fresh entries. After merging, zero entries
are deleted.

With `region`, each step's box is clipped to the region first and
dropped if nothing is left.

### `part1` / `part2`

`count_on(steps, INIT_REGION)` and `count_on(steps)`.

## 4. Why it is correct

- **Invariant:** after every step, Σ sign · [cube ∈ b] is 1 for an on
  cube and 0 for an off cube.
  - A cube outside C: no new entry contains it, so its sum is unchanged.
  - A cube inside C: for each old entry `(b, s)` containing it, `b ∩ C`
    also contains it and contributes −s. Its old sum therefore cancels to
    0. An `on` step adds +1 and an `off` step adds nothing.
- **Merging is exact.** `Counter` adds the signs of equal boxes. A zero
  entry contributes nothing to any cube, so deleting it changes nothing.
- **Clipping is exact.** A cube inside the region is covered by a clipped
  step exactly when it's covered by the original step, so its on/off
  history is unchanged. Cubes outside the region are never counted.
- **Pinned in the tests against three independent references:**
  - `literal_count`: a Python `set` of every on cube. 30 random 12-step
    inputs unclipped, and 30 with steps straddling a lopsided region.
  - `grid_count`: a `bytearray` per (x, y) column with z ranges set by
    slice. Checked on the larger example and on the real part 1.
  - `disjoint_count`: a different algorithm. It keeps the on-set as
    *disjoint* boxes and carves each new C out of them (up to 6 pieces
    per box), so nothing ever carries a negative sign. Checked against
    `literal_count` on 30 random inputs, then on the part 2 example and
    on the real part 2 answer.
- The statement's numbers all match: 27 / 46 / 38 / 39 step by step,
  590784, 2758514936282235, and the "just for fun" 474140 (part 1 run on
  the part 2 example).

## 5. Complexity

Each step intersects C with every live entry, so the cost is
Σ over steps of (list length). The list grows when new entries are added
and shrinks only when entries cancel. The worst case is exponential: n
nested overlaps can produce 2ⁿ distinct boxes. On real inputs it stays
small. Measured on the real input:

| part | steps run | final list length | peak | intersections |
| ---- | --------: | ----------------: | ---: | ------------: |
| 1    |        20 |               300 |  300 |         1,940 |
| 2    |       420 |             3,844 | 3,844 |      591,520 |

(The peak equals the final length here, so the list never shrank
overall on this input.)

| phase  |      ms |
| ------ | ------: |
| parse  |   0.678 |
| part 1 |   2.092 |
| part 2 | 330.659 |
| total  | 333.429 |

`bench.py 22`, best of 5 on the real input.

**What merging buys.** The same algorithm with a plain list of
`(box, sign)` pairs, so equal boxes are never merged and zero pairs never
dropped, ends with **47,492** entries instead of 3,844. It took **8.04 s**
instead of 0.33 s (one run, same answer), about 24× slower. Without
merging, every cancellation pair in a dense overlap region survives and
gets intersected again by every later step.

**The disjoint-carving reference** took 383 ms on part 2 (one run), close
to the shipped 331 ms. It wasn't chosen because its correctness argument
needs six carving cases and an ordering argument, while the signed list's
argument is the two-line invariant above.

## 6. If I were writing this in Rust

A sketch; it was not compiled for this guide.

```rust
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
struct Cuboid { lo: [i32; 3], hi: [i32; 3] }   // inclusive

impl Cuboid {
    fn volume(&self) -> i64 {
        (0..3).map(|a| (self.hi[a] - self.lo[a] + 1) as i64).product()
    }
    fn intersect(&self, o: &Cuboid) -> Option<Cuboid> {
        let mut c = *self;
        for a in 0..3 {
            c.lo[a] = c.lo[a].max(o.lo[a]);
            c.hi[a] = c.hi[a].min(o.hi[a]);
            if c.lo[a] > c.hi[a] { return None; }
        }
        Some(c)
    }
}

fn count_on(steps: &[(bool, Cuboid)]) -> i64 {
    let mut signed: HashMap<Cuboid, i64> = HashMap::new();
    for &(on, c) in steps {
        let mut update: HashMap<Cuboid, i64> = HashMap::new();
        for (b, &s) in &signed {
            if let Some(o) = c.intersect(b) { *update.entry(o).or_default() -= s; }
        }
        if on { *update.entry(c).or_default() += 1; }
        for (b, s) in update {
            let e = signed.entry(b).or_default();
            *e += s;
            if *e == 0 { signed.remove(&b); }
        }
    }
    signed.iter().map(|(b, &s)| s * b.volume()).sum()
}
```

- **Integer widths matter here, unlike in Python.** Coordinates fit in
  `i32`, but the largest single step volume in the real input is
  3.47·10¹³ and the answer is 1.36·10¹⁵ (both measured). Those overflow
  `i32` and fit `i64` (max 9.2·10¹⁸) with thousands-fold headroom. Each
  axis length must be widened to `i64` *before* multiplying, as `volume`
  does. Doing the multiply in `i32` and casting afterwards is the classic bug.
- **The borrow checker forces the two-phase update.** Iterating `&signed`
  while inserting into it doesn't compile, so the separate `update` map
  isn't a style choice in Rust. In Python, mutating a dict during
  iteration raises `RuntimeError` at runtime. Rust catches the same bug
  at compile time.
- `[i32; 3]` arrays let `intersect` be a loop over axes. That's the same
  as treating the three axes as a 3-lane SIMD register: per-lane max,
  per-lane min, then a compare that reduces with "any lane empty".

## 7. Possible optimization

**Coordinate compression.** Collect every `x0` and `x1 + 1` (and the
same for y and z), giving 836 / 831 / 834 distinct cut points on the
real input (measured). Paint a compressed boolean grid and sum the cell
volumes. That's ~5.8·10⁸ cells, far too many for pure Python. With numpy
it becomes a sweep over x slabs. Not implemented, since
the repo doesn't use numpy and the shipped code is already 0.33 s.

**Skip whole steps whose box is disjoint from everything** (an AABB
pre-check on a running bounding box of the list). It doesn't help here:
nearly every part 2 step lands in the same ±100k cloud. Not measured.

**A spatial index** (bin the live boxes by coarse x slab) would cut the
591,520 intersection tests to the ones that could overlap, but it adds
bookkeeping when entries are deleted. Not implemented or measured.
