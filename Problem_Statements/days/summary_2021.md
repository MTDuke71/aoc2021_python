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
| 00 | [The Tyranny of the Rocket Equation](day00.md) | ✅ | 3481005 | 5218616 |  |  |  |  | Dry run; [guide](day00_function_guide.md). Part 1 sums `mass // 3 - 2`; part 2 iterates that on its own output until a step is no longer positive. |
| 01 | [Sonar Sweep](day01.md) | ✅ | 1791 | 1822 |  |  |  |  | [guide](day01_function_guide.md). Both parts are `count_increases(depths, gap)`: gap 1, then gap 3, since adjacent three-wide windows share two readings and the sum comparison reduces to `d[i+3] > d[i]`. |
| 02 | [Dive!](day02.md) | ✅ | 2070300 | 2078985210 | 0.186 | 0.036 | 0.056 | 0.278 | [guide](day02_function_guide.md). Commands parse to signed `(forward, dive)` deltas. Both parts are one loop over them; part 1 accumulates `depth += dive`, part 2 `aim += dive` then `depth += aim * forward`. Part 2's product fits `i32` with only ~3% headroom. |
| 03 | [Binary Diagnostic](day03.md) | ⬜ |  |  |  |  |  |  |  |
| 04 | [Giant Squid](day04.md) | ⬜ |  |  |  |  |  |  |  |
| 05 | [Hydrothermal Venture](day05.md) | ⬜ |  |  |  |  |  |  |  |
| 06 | [Lanternfish](day06.md) | ⬜ |  |  |  |  |  |  |  |
| 07 | [The Treachery of Whales](day07.md) | ⬜ |  |  |  |  |  |  |  |
| 08 | [Seven Segment Search](day08.md) | ⬜ |  |  |  |  |  |  |  |
| 09 | [Smoke Basin](day09.md) | ⬜ |  |  |  |  |  |  |  |
| 10 | [Syntax Scoring](day10.md) | ⬜ |  |  |  |  |  |  |  |
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
