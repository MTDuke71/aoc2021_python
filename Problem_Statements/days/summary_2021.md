# AoC 2021 Summary

**Part 1 / Part 2 columns hold submitted, accepted answers** -- the same values
as `LOCKED` in `tests/test_dayNN.py`. A day whose answers have not been accepted
by adventofcode.com stays blank, whatever the code currently prints.

**Parse / P1 / P2 / Total are milliseconds** from `bench.py`, best of 5 on the
real input, recorded when the day was finished. Total is the sum of the three
bests. `bench.py` skips a day until both parts are written, so a 🟡 row has no
timings.

Day 0 is a tutorial dry run (AoC 2019 day 1), not an AoC 2021 puzzle. It is here
to prove the pipeline end to end: module, tests, locked answers, bench.

Status: ✅ both answers accepted · 🟡 in progress: code written, not every answer accepted yet · ⬜ not started.

| Day | Puzzle | Status | Part 1 | Part 2 | Parse | P1 | P2 | Total | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 00 | [The Tyranny of the Rocket Equation](day00.md) | ✅ | 3481005 | 5218616 | 0.009 | 0.007 | 0.064 | 0.081 | Dry run; [guide](day00_function_guide.md). Part 1 sums `mass // 3 - 2`; part 2 iterates that on its own output until a step is no longer positive. |
| 01 | [Sonar Sweep](day01.md) | ✅ | 1791 | 1822 | 0.175 | 0.087 | 0.083 | 0.346 | [guide](day01_function_guide.md). Both parts are `count_increases(depths, gap)`: gap 1, then gap 3, since adjacent three-wide windows share two readings and the sum comparison reduces to `d[i+3] > d[i]`. |
| 02 | [Dive!](day02.md) | ✅ | 2070300 | 2078985210 | 0.186 | 0.036 | 0.056 | 0.278 | [guide](day02_function_guide.md). Commands parse to signed `(forward, dive)` deltas. Both parts are one loop over them; part 1 accumulates `depth += dive`, part 2 `aim += dive` then `depth += aim * forward`. Part 2's product fits `i32` with only ~3% headroom. |
| 03 | [Binary Diagnostic](day03.md) | ✅ | 2648450 | 2845944 | 0.337 | 0.527 | 0.323 | 1.187 | [guide](day03_function_guide.md). Parse keeps the bit width alongside the ints. Part 1: gamma sets each bit on a strict majority of 1s, epsilon is gamma XOR the all-ones mask (ties raise). Part 2: filter survivors MSB-first by most/least common bit; the two tie rules are mirror images, so the ratings split at the first bit. Part 2 is cheaper than part 1 (~8k vs 12k value visits). |
| 04 | [Giant Squid](day04.md) | ✅ | 29440 | 13884 | 0.972 | 0.006 | 0.007 | 0.986 | [guide](day04_function_guide.md). No simulation: map each cell to its draw turn; a line completes at its max, a board wins at the min over its 10 lines, unmarked = cells with a later turn. Parse builds every board's `Win(turn, score)`; part 1 takes the min turn, part 2 the max (ties with different scores, or a board that never wins, raise). |
| 05 | [Hydrothermal Venture](day05.md) | ✅ | 5167 | 17604 | 0.444 | 23.981 | 41.408 | 65.832 | [guide](day05_function_guide.md). Each segment walks with a unit step (sign dx, sign dy), which covers exactly the grid points of a 0/45/90-degree line (other angles raise), into a `Counter`; answer is points with count >= 2. Part 1 filters to axis-aligned, part 2 takes all. Time scales with points walked (107k vs 183k). |
| 06 | [Lanternfish](day06.md) | ✅ | 373378 | 1682576647495 | 0.057 | 0.028 | 0.074 | 0.159 | [guide](day06_function_guide.md). Fish are interchangeable, so state is a 9-slot histogram by timer; a day is a rotate-left plus adding the wrapped slot 0 into slot 6. Both parts are `population(counts, days)` (80, then 256), constant work per day. |
| 07 | [The Treachery of Whales](day07.md) | ✅ | 328318 | 89791146 | 0.138 | 0.046 | 0.198 | 0.382 | [guide](day07_function_guide.md). Part 1 target is the median (minimises sum of absolute distances); part 2 cost is d(d+1)/2, whose optimum lies within half a step of the mean, so try floor(mean) and floor(mean)+1. Both shortcuts are pinned against a full search over every target. |
| 08 | [Seven Segment Search](day08.md) | ✅ | 274 | 1012089 | 0.721 | 0.041 | 0.611 | 1.373 | [guide](day08_function_guide.md). Patterns parse to frozensets of wires. Part 1 counts output patterns of length 2, 3, 4 or 7 (digits 1, 7, 4, 8). Part 2 decodes without recovering the wire map: length gives 1/7/4/8, then overlap with the known 1 and 4 separates {2,3,5} and {0,6,9}. The rule is pinned against all 5040 wirings and a brute-force permutation solver. |
| 09 | [Smoke Basin](day09.md) | ✅ | 423 | 1198704 | 0.602 | 10.118 | 17.378 | 28.097 | [guide](day09_function_guide.md). Grid of ints. Part 1 sums height+1 over cells strictly lower than every orthogonal neighbour. Part 2 flood-fills from each low point through non-9 cells (a basin is a connected non-9 region holding exactly one low point, checked on the real input) and multiplies the top three sizes. |
| 10 | [Syntax Scoring](day10.md) | ✅ | 323613 | 3103006161 | 0.403 | 0.004 | 0.067 | 0.473 | [guide](day10_function_guide.md). Parse runs the bracket stack over every line and keeps the first wrong closer plus the unclosed openers; both parts are lookups over that. Part 1 sums a points table over the corrupted lines. Part 2 reads each incomplete line's stack top-down as a base-5 number and takes the median (odd count checked on the real input). |
| 11 | [Dumbo Octopus](day11.md) | ⬜ |  |  |  |  |  |  |  |
| 12 | [Passage Pathing](day12.md) | ⬜ |  |  |  |  |  |  |  |
| 13 | [Transparent Origami](day13.md) | ⬜ |  |  |  |  |  |  |  |
| 14 | [Extended Polymerization](day14.md) | ⬜ |  |  |  |  |  |  |  |
| 15 | [Chiton](day15.md) | ⬜ |  |  |  |  |  |  |  |
| 16 | [Packet Decoder](day16.md) | ⬜ |  |  |  |  |  |  |  |
| 17 | [Trick Shot](day17.md) | ⬜ |  |  |  |  |  |  |  |
| 18 | [Snailfish](day18.md) | ⬜ |  |  |  |  |  |  |  |
| 19 | [Beacon Scanner](day19.md) | ⬜ |  |  |  |  |  |  |  |
| 20 | [Trench Map](day20.md) | ⬜ |  |  |  |  |  |  |  |
| 21 | [Dirac Dice](day21.md) | ⬜ |  |  |  |  |  |  |  |
| 22 | [Reactor Reboot](day22.md) | ⬜ |  |  |  |  |  |  |  |
| 23 | [Amphipod](day23.md) | ⬜ |  |  |  |  |  |  |  |
| 24 | [Arithmetic Logic Unit](day24.md) | ⬜ |  |  |  |  |  |  |  |
| 25 | [Sea Cucumber](day25.md) | ⬜ |  |  |  |  |  |  |  |
