# Day 19 Function Guide — Beacon Scanner

Source: [`src/day19.py`](../../src/day19.py) ·
Tests: [`tests/test_day19.py`](../../tests/test_day19.py) ·
Statement: [`day19.md`](day19.md)

Answers (accepted): **465** / **12149**.

## 1. The problem

Scanners float in 3-D water. Each one reports the beacons within 1000 units
of itself on every axis, in **its own frame**. Each scanner has an unknown
position, and an unknown orientation that is one of the 24 axis-aligned
rotations (face ±x, ±y or ±z, then pick one of 4 "up"s). Scanners can't see
each other. Two scanners that see **at least 12 of the same beacons** can be
locked together, and the overlaps chain into one connected map.

- **Part 1:** assemble the map in scanner 0's frame and count the distinct
  beacons.
- **Part 2:** the largest Manhattan distance between two scanner positions.

The real input has 40 scanners reporting 25–27 beacons each: 1,032 reports
of 465 distinct beacons.

## 2. The key observation: alignment is a vote

A worked example first. In the statement, scanners 0 and 1 share 12
beacons. The first one is

```
scanner 0 sees  (-618, -824, -621)
scanner 1 sees  ( 686,  422,  578)
```

Scanner 1 is turned 180° about y, so the rotation is `R(x, y, z) = (−x, y, −z)`
and `R(686, 422, 578) = (−686, 422, −578)`. The difference
`(−618, −824, −621) − (−686, 422, −578) = (68, −1246, −43)` is scanner 1's
position in scanner 0's frame, which is the statement's answer. Each of the
other 11 shared beacons gives the **same** difference. That's the whole
trick:

> For a candidate rotation R, let every pairing (a from A, b from B) vote for
> the offset `a − R(b)`. With the right R, the true offset gets one vote per
> shared beacon, so at least 12. Unrelated pairings scatter.

For this pair, the offset vote under the right rotation is **12** for
`(68, −1246, −43)`, and the best wrong offset gets **1**. Across every alignment
done on the real input, no losing offset under any rotation ever got more
than **2** votes. Every winner got exactly 12. The threshold has a lot of
margin (all measured, see §6).

It's a correlation peak, like finding a sync word in a bit stream: slide
one frame against the other in every way allowed, count coincidences, and
look for a spike that stands well clear of the noise floor.

## 3. Representation

- `Point = (x, y, z)` tuple.
- `Rotation = (perm, signs)`, meaning `R(p)[k] = signs[k] · p[perm[k]]`. A
  signed axis permutation is exactly a 3×3 matrix with one ±1 per row and
  column. There are 48 of them, and the 24 with determinant +1 are the proper
  rotations. The other 24 are mirror images, and a physical scanner can't be
  in one of those.
- `BeaconMap(scanners, views, beacons)` is what `parse_input` returns:
  - `scanners[i]` is scanner i's position in scanner 0's frame,
  - `views[i]` is scanner i's beacons moved into scanner 0's frame,
  - `beacons` is the union of the views.

  Both parts read it: part 1 counts `beacons`, part 2 scans `scanners`.
  `views` exists so the tests can check the assembly (§5).

The assembly is the expensive part and doesn't depend on which part is
asking, so per the repo convention it lives in `parse_input`. That's why
the bench shows parse ≈ total.

## 4. Function walkthrough

### `_rotations()` / `ROTATIONS`

Walk all 6 permutations × 8 sign patterns and keep the ones with
`parity(perm) × sx·sy·sz = +1`. That product is the determinant of a signed
permutation matrix. The identity comes first, which is the orientation
scanner 0 defines.

### `rotate(p, rotation)`

Three index lookups and three sign multiplies. No matrix multiply.

### `fingerprint(beacons) -> Counter[int]`

The multiset of **squared** distances over every pair of a scanner's beacons.
That's C(26, 2) = 325 entries for a typical scanner. Squared keeps it in
exact integers. A distance doesn't change under rotation or translation, so a
scanner's fingerprint is the same in every frame.

### `could_overlap(fp_a, fp_b)`

`(fp_a & fp_b).total() >= 66`: the size of the multiset intersection. If
two scanners share 12 beacons, the C(12, 2) = 66 pairs among those beacons
show up in both fingerprints, so ≥ 66 is a **necessary** condition. It can
never reject a real neighbour, so it's a safe prefilter, not a heuristic.

### `align(placed, beacons)`

`placed` is an already-placed scanner's beacons in the absolute frame, and
`beacons` is a candidate's raw report. For each of the 24 rotations: rotate
the candidate's beacons, tally the 26 × 26 ≈ 676 offset votes in a
`Counter`, and accept the first rotation whose top offset has ≥ 12 votes.
Returns `(position, beacons moved into the absolute frame)`, or `None`.

### `parse_reports(raw)`

Splits on `--- scanner N ---` headers. Refuses a beacon before any header,
headers out of sequence, a point that isn't three ints, and a scanner that
reports the same beacon twice. Per-line `.strip()` handles CRLF.

### `assemble(reports)`

Breadth-first search from scanner 0. When a scanner gets placed, it's tried
once against every scanner that isn't placed yet: fingerprint check first,
then `align` against the placed scanner's **absolute** beacons, so the new
one comes out directly in scanner 0's frame with no composing of
transforms. Placed scanners join the queue. Anything still unplaced at the
end raises, naming the stragglers.

### `part1`, `part2`

`len(beacons)`; and the max of `|dx| + |dy| + |dz|` over the
C(40, 2) = 780 scanner pairs.

## 5. Why it is correct

**The rotation set.** Pinned two ways: 24 distinct matrices, all with
determinant 1. And independently, closing the three 90° quarter-turns (about
x, y and z) under composition gives exactly the same 24. The statement's
five views of one scanner are each matched point for point by some rotation
of the first.

**The prefilter never drops a real overlap.** On both the example and the
real input, every pair that actually shares ≥ 12 beacons in the finished map
passes `could_overlap`. On the real input it's also exact. It passes the
53 true neighbour pairs out of 780 and nothing else. True pairs share 66
distances (51 pairs) or 67 (2 pairs, one coincidental match). The busiest
non-pair shares 16. And turning the filter off (every pair gets the full
24-rotation vote) gives an identical map. All of that is pinned.

**No false lock.** A mislocked scanner would claim beacons in the wrong
place. The test checks that **each scanner's view is exactly the set of map
beacons inside its ±1000 cube**: nothing missing, nothing extra. A wrong
placement would put beacons inside some correctly placed neighbour's cube
that the neighbour doesn't report, or leave out ones it does. This holds on
the example and the real input.

**How the real input was built.** Any two real scanners share exactly 0, 3,
6 or 12 beacons (pinned). Never 7–11, never 13+, so there are no
near-misses at the threshold either way.

**Against the statement.** All five example scanner positions; the 79-beacon
listing; both 12-beacon overlap listings (0/1 and 1/4); scanner 1's listed
beacons landing on scanner 0's listing in order after `align`; the 2-D
warm-up offset (5, 2); and part 2's 3621, from scanners 2 and 3 with
components 1197 + 1175 + 1249. Plus a re-scrambled example (each scanner
re-expressed in a different rotation) reassembling to the same beacons.

## 6. Complexity

With S scanners and B ≈ 26 beacons each:

- fingerprints: S · C(B, 2) ≈ 40 × 325 distances;
- prefilter: each placed scanner checks every unplaced one. **588**
  `could_overlap` calls on the real input;
- alignment: **39** `align` calls, one per scanner after 0. All 39
  succeed, because the prefilter lets through only true neighbours and BFS
  never retries a placed scanner. Each call tries rotations until the right
  one: **13.1 on average** (2 to 24), at ~676 votes each.

Measured split of assembly (instrumented run): about **20 ms** in the 588
prefilter checks and **52 ms** in the 39 alignments. With the prefilter
switched off, assembly takes **1.41 s** instead of 0.077 s, because then
every non-neighbour costs a full 24 × 676 vote before being rejected.

| phase  |     ms |
| ------ | -----: |
| parse  | 74.660 |
| part 1 |  0.000 |
| part 2 |  0.456 |
| total  | 75.116 |

`bench.py 19`, best of 5 on the real input. Parse is the whole assembly.
Part 1 is a `len()`.

## 7. If I were writing this in Rust

A sketch; it was not compiled for this guide.

```rust
type P = [i32; 3];

#[derive(Clone, Copy)]
struct Rot { perm: [usize; 3], sign: [i32; 3] }

impl Rot {
    fn apply(&self, p: P) -> P {
        [0, 1, 2].map(|k| self.sign[k] * p[self.perm[k]])
    }
}

fn align(placed: &[P], beacons: &[P], rots: &[Rot]) -> Option<(P, Vec<P>)> {
    let mut votes: HashMap<P, u8> = HashMap::with_capacity(placed.len() * beacons.len());
    for r in rots {
        votes.clear();
        let turned: Vec<P> = beacons.iter().map(|&b| r.apply(b)).collect();
        for a in placed {
            for b in &turned {
                let off = [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
                let n = votes.entry(off).or_default();
                *n += 1;
                if *n >= 12 {
                    let moved = turned.iter().map(|t| [0, 1, 2].map(|k| t[k] + off[k])).collect();
                    return Some((off, moved));
                }
            }
        }
    }
    None
}
```

- **Early exit on the 12th vote.** Python's `Counter` tallies everything,
  then asks for the top offset. In Rust the check is free inline, and the
  first offset to reach 12 is the answer, since no wrong offset gets past 2.
- **Rotations as a const table.** The 24 `Rot`s can be computed at compile
  time (a `const fn` over permutations and signs, or a literal table). Then
  `apply` is three loads and three multiplies.
- **The fingerprint as a sorted `Vec<u32>`.** Squared distances fit in
  `u32` here: coordinates are within ±1000 of their scanner, so a squared
  distance is at most 3 × 2000² = 12,000,000. The multiset intersection
  becomes a merge walk over two sorted vectors, with no hashing.
- **Coordinate range.** On the real input the largest absolute coordinate
  is 4,869 for a scanner and 5,524 for a beacon (measured), and the
  largest Manhattan separation is 12,149. `i32` has huge headroom, and
  `i16` would hold any single coordinate here too.

## 8. Possible optimization

**Anchor alignment instead of a full vote. Measured: about 1.9× on
assembly.** The fingerprint already says *which* beacon pairs match.
Choose a squared distance that occurs exactly once in each scanner. That
names a beacon pair `(a1, a2)` in A and `(b1, b2)` in B. The difference
vectors `a2 − a1` and `b2 − b1` must be related by the unknown rotation (up
to which end is which). So the rotation is the one with `R(b2 − b1) = ±(a2 − a1)`,
and then the offset follows from one beacon. Verify by counting how many
moved beacons land in A's set (≥ 12), and move on to the next unique distance
if not. That replaces up to 24 × 676 Counter increments with one candidate
check per rotation and a 26-element set probe.

A scratch prototype of this, swapped in for `align`, reproduced the
identical map on the real input with assembly at **39.7 ms** against
**75.6 ms** for the shipped vote (best of 5, same run). It isn't shipped.
The vote is the explanation of the puzzle, while the anchor method takes a
paragraph to justify. And what's left after it is mostly the fingerprint
and prefilter cost, so the next 2× isn't there.
