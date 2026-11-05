# Day 17 Function Guide — Trick Shot

Source: [`src/day17.py`](../../src/day17.py) ·
Tests: [`tests/test_day17.py`](../../tests/test_day17.py) ·
Statement: [`day17.md`](day17.md)

Answers (accepted): **3655** / **1447**.

## 1. The problem

A probe starts at `(0, 0)` and is launched with an integer velocity
`(vx, vy)`. Each step:

1. `x += vx`, `y += vy`
2. drag: `vx` moves 1 toward 0 (and stays at 0 once it gets there)
3. gravity: `vy -= 1`

The input is one line, a target rectangle:

```
target area: x=209..238, y=-86..-59
```

A launch **hits** if the probe's position is inside the rectangle *after
some step*. Positions are only checked at the end of each step, so a probe
can fly through the box between two steps and still miss. The statement's
`17,-4` does that.

- **Part 1:** the highest `y` reached by any trajectory that hits.
- **Part 2:** how many distinct launch velocities hit.

## 2. The key observation: the axes are independent

x depends only on `vx` and the step number `t`; y depends only on `vy` and
`t`. Nothing couples them. So:

> `(vx, vy)` hits ⇔ there is a step `t` at which x is in the x band **and**
> y is in the y band.

Work out each axis on its own: for each `vx`, the set of steps it spends
inside the x band, and for each `vy`, the set of steps inside the y band.
A launch hits exactly when its two sets overlap. It's like two
independent counters you sample on the same clock: a pair is good if
there's a tick where both read in range.

Statement example (`x=20..30, y=-10..-5`), launch `7,2`:

| t | x (vx=7) | in x band? | y (vy=2) | in y band? |
| -: | -: | :-: | -: | :-: |
| 1 | 7 | | 2 | |
| 2 | 13 | | 3 | |
| 3 | 18 | | 3 | |
| 4 | 22 | ✓ | 2 | |
| 5 | 25 | ✓ | 0 | |
| 6 | 27 | ✓ | −3 | |
| 7 | 28 | ✓ | −7 | ✓ |
| 8+ | 28 (stalled) | ✓ | −12 | below, gone |

`x_steps(7)` = {4, 5, 6, …} (it stalls at 28, inside the band), `y_steps(2)`
= [7]. They share t = 7, so it's a hit.

## 3. Representation

- `parse_target(raw) -> Target`: a `NamedTuple(x_min, x_max, y_min, y_max)`
  read with one anchored regex.
- `parse_input(raw) -> list[(vx, vy)]`: **every hitting launch.** Both
  parts are reductions over that one list (max apex, count), so per the
  repo rule it's built in parse, not recomputed per part.

`parse_target` refuses anything outside the quadrant `x > 0`, `y < 0`
(real inputs are always there). The velocity bounds below depend on it.
A target left of the origin is just a mirror image, but there's no point
writing code for an input AoC never hands out.

## 4. Function walkthrough

### The search box

Only a finite box of velocities can possibly hit:

- **`vx` in `1..x_max`.** `vx ≤ 0` never moves right. `vx > x_max`
  overshoots the far edge on step 1, and x only ever grows.
- **`vy` in `y_min..-y_min-1`.** `vy < y_min` is below the box after step
  1 and only falls further. For the top: a probe fired up at `vy` rises and
  falls symmetrically. It crosses `y = 0` again at step `2·vy + 1`, now
  moving at `-(vy + 1)`, so the next step lands at `y = -(vy + 1)`. If
  `vy ≥ -y_min`, that's already below `y_min` and it skips the box
  entirely.

Real input: 238 `vx` × 172 `vy` = 40,936 candidates.

`test_hits_matches_brute_force` pins those bounds. A literal simulator
searches a box padded 50 past them on every side (20 on the real input),
negative `vx` included, and must find exactly the same set.

### `y_steps(vy, target) -> list[int]`

Simulates y alone until the probe is below the band, and records the steps
it's inside. Once below and falling it never comes back, so the loop is
finite. Real input: 138 of the 172 `vy` have a non-empty list, and the
longest flight is `vy = 85`, in the band only at **t = 172**.

### `x_steps(vx, target, t_max) -> set[int]`

The same for x, with one difference. Drag stops x at the triangular number
`vx(vx+1)/2`, and if that's inside the band, the probe is "in x range" at
every step forever. So the caller passes a cap `t_max`: the latest step at
which *any* `vy` is in the y band (172 on the real input). Past that, no y
partner exists. 92 of the 238 `vx` ever touch the band.

### `hits(target) -> list[(vx, vy)]`

Builds both per-axis tables, drops velocities whose set is empty, then tests
every remaining pair for overlap with `set.isdisjoint`. Real input:
92 × 138 = 12,696 pairs tested, **1447** hits.

### `apex(vy)`

`vy + (vy − 1) + … + 1 = vy(vy+1)/2` for `vy > 0`; for `vy ≤ 0` the highest
point is the launch point, 0.

### `part1(shots)` / `part2(shots)`

`max(apex(vy) for _, vy in shots)` and `len(shots)`.

## 5. Why it is correct

**Hits.** The axis split is exact, not an approximation: the update rules
for x and y share nothing but the step counter. Every candidate in the
search box is classified, and §4 explains why nothing outside the box can
hit. Two independent checks back this up:

- the literal simulator over a padded box (above), on five small targets
  and the real input;
- the statement's 112-velocity listing for part 2, pasted verbatim into the
  test and compared as a **set**, not just a count.

`hits` builds its list from dict keys, so it can't contain a velocity
twice. `test_hits_has_no_duplicates` pins that, since part 2 is a bare
`len()`.

**Part 1 has a closed form, and it's conditional.** The highest possible
shot is `vy = -y_min - 1` (85): it lands exactly on the bottom row `y_min`
at step `2·vy + 2` = 172. That only works if *some* `vx` is still in the x
band at step 172, and only a `vx` that has stopped moving can be. That
needs a triangular number inside `x_min..x_max`:

- Real input: 20·21/2 = **210** and 21·22/2 = **231** are both in
  209..238. `vx = 20` enters the band at step 19 (20+19+…+2 = 209) and sits
  at 210 from step 20 on.
- So part 1 = 85·86/2 = **3655**, the formula `y_min(y_min+1)/2`.

Per standing rule 1, the shortcut is pinned rather than just written here.
`test_part1_closed_form` checks the formula against the search on four
targets. One of them (`x=5..5`, which no triangular number reaches) is the
counterexample: there the formula overestimates and the test asserts that
it does. The shipping code uses the search, not the formula, so it's right
either way.

**A floor for part 2.** Any `(vx, vy)` that is itself inside the target
rectangle hits on step 1. That's the full 30 × 28 = 840 block, and all 840
are among the 1447. The other 607 take more than one step.

## 6. Complexity

Let `X = x_max` and `Y = |y_min|`.

- `y_steps` over `2Y` velocities, each flight up to `2Y` steps: O(Y²).
- `x_steps` over `X` velocities, each capped at `t_max ≤ 2Y`: O(X·Y).
- Pair test: up to (live vx) × (live vy) set-disjointness checks, each
  bounded by the smaller set.

All tiny here: tens of thousands of cheap operations.

| phase  |    ms |
| ------ | ----: |
| parse  | 1.721 |
| part 1 | 0.085 |
| part 2 | 0.000 |
| total  | 1.806 |

`bench.py 17`, best of 5 on the real input.

All the work is in parse, which builds the hit list. Part 1 is one pass of
1447 `apex` calls. Part 2 is `len()`, below the bench's three-decimal
resolution.

For comparison, simulating every candidate in the box directly (the test
suite's literal simulator, which stops early once the probe heads away from
the band) takes **25.3 ms** best of 5 for the same 1447. The axis split is
about 14× faster, mostly because each axis is simulated once per velocity
(238 + 172 runs) instead of once per pair (40,936 runs).

## 7. If I were writing this in Rust

A sketch; it was not compiled for this guide.

```rust
struct Target { x_min: i32, x_max: i32, y_min: i32, y_max: i32 }

type Mask = [u64; 3];  // bit t set = in band at step t; t_max = 2·|y_min| = 172 < 192

fn y_mask(vy: i32, t: &Target) -> Mask { /* simulate y, set bit t while in band */ }
fn x_mask(vx: i32, t: &Target, t_max: usize) -> Mask { /* same for x, capped */ }
fn overlaps(a: &Mask, b: &Mask) -> bool { a.iter().zip(b).any(|(p, q)| p & q != 0) }
fn empty(m: &Mask) -> bool { m.iter().all(|&w| w == 0) }

fn hits(t: &Target) -> Vec<(i32, i32)> {
    let t_max = 2 * (-t.y_min) as usize;
    let ys: Vec<(i32, Mask)> = (t.y_min..-t.y_min)
        .map(|vy| (vy, y_mask(vy, t)))
        .filter(|(_, m)| !empty(m))
        .collect();
    let mut out = Vec::new();
    for vx in 1..=t.x_max {
        let xm = x_mask(vx, t, t_max);
        out.extend(ys.iter().filter(|(_, ym)| overlaps(&xm, ym)).map(|&(vy, _)| (vx, vy)));
    }
    out
}
```

- **Step sets as bitmasks.** This is the register-level version of the
  Python `set`s: bit `t` set means "in band at step t". With `t_max = 172`,
  a mask is three `u64` words, and the overlap test is three ANDs and an
  OR. That's exactly what `set.isdisjoint` is doing, minus the hashing.
- **`i32` is plenty.** Coordinates stay within a few hundred and the apex is
  3655.
- **No `Result` needed past parsing.** The quadrant check lives in
  `parse_target`; after that, every loop is bounded by construction.

## 8. Possible optimization

**Part 1 in O(1).** Return `y_min(y_min+1)/2` when a triangular number lies
in the x band, and fall back to the search otherwise. It's not worth it:
the search has to run for part 2 anyway, and part 1 already costs 0.085 ms
on top of it. The tests pin the formula, so it's there if ever needed.

**Bitmask step sets in Python.** Python ints are arbitrary-width bitmasks,
so `y_steps`/`x_steps` could return `int`s with bit `t` set, and the overlap
test becomes `xm & ym != 0`. That's the same idea as the Rust sketch. It
wasn't measured: parse is 1.7 ms, and readable sets are worth more than
whatever it would save.
