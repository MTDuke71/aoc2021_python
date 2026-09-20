# aoc2021_python

Advent of Code 2021, in Python.

This picks up where [aoc2021_OCaml](https://github.com/MTDuke71/aoc2021_OCaml)
stopped: the language-rotation experiment is over and Advent of Code itself is
the point. The conventions are the ones that settled in `aoc2020_Prolog`'s
Python era, laid out here without a legacy tree to fence off.

## Layout

| Path | What it is |
|---|---|
| `src/dayNN.py` | the solutions — `parse_input` / `part1` / `part2` / `solve` / `main` |
| `tests/test_dayNN.py` | one pytest module per day |
| `tests/conftest.py` | the `real_input` and `check_locked` fixtures |
| `bench.py` | per-phase timings, best and median of N runs |
| `Problem_Statements/days/` | puzzle text, function guides, and `summary_2021.md` |
| `inputs/dayNN.txt` | puzzle inputs (gitignored — AoC asks they not be redistributed) |
| `scripts/` | PowerShell helpers that download statements and inputs and convert the HTML to Markdown |

Days 01–25 start as stubs whose `part1` / `part2` raise `NotImplementedError`.
The tests and the bench both key on that, so an unsolved day shows up as a
skip, never as an answer or a timing.

## Setup

Windows, no WSL. Virtualenv executables live in `Scripts\`, not `bin/`:

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install pytest ruff
```

## Run a day

```
.venv\Scripts\python.exe src\day01.py
```

`INPUT` is resolved from `__file__`, so this works from any directory. Parts
print one at a time: part 1's answer is on screen to submit while part 2 is
still a stub.

## Test

```
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m pytest tests\test_day01.py
```

`pyproject.toml` sets `testpaths` and `pythonpath`, so a test module can just
say `import day03` — no package layout, no `sys.path` juggling.

Inputs are gitignored, so a fresh clone has none. Tests that need one **skip**
rather than fail.

Each test module carries a `LOCKED` tuple of the day's real-input answers:

- `LOCKED = (part1, part2)` — asserted. A refactor that changes an answer fails.
- `LOCKED = (part1, None)` — part 1 asserted; part 2 reported, then skipped.
  The normal state between the two stars.
- `LOCKED = None` — everything reported, then skipped.

An answer goes into `LOCKED` only after adventofcode.com has accepted it. An
answer nobody has submitted never gets asserted against itself, so a green
suite never implies more confidence than somebody actually has.

## Format

```
.venv\Scripts\ruff.exe format .
.venv\Scripts\ruff.exe check .
```

Line length 110.

## Bench

```
.venv\Scripts\python.exe bench.py          # every solved day with an input
.venv\Scripts\python.exe bench.py -n 20 11 # 20 reps, day 11 only
```

Reports best and median per phase. Best-of-N rather than one shot: most days
run in well under a millisecond, where single-run spread is wider than the
differences worth measuring.

## Refreshing a statement

Part 2 of a statement only exists once part 1 is accepted, so the statement
files need re-downloading as days are solved:

```
$env:AOC_SESSION = "your_session_cookie"
.\scripts\download_aoc2021_problems.ps1 -StartDay 1 -EndDay 1 -ProblemsOnly
.\scripts\convert_aoc2021_html_to_md.ps1 -StartDay 1 -EndDay 1 -Overwrite -RemoveHtml
```

`-Overwrite` is required: the converter will not replace an existing statement
without it.

## Solved

Day 0 is a tutorial dry run (AoC 2019 day 1), not an AoC 2021 puzzle; it is
here to prove the pipeline end to end. See
[Problem_Statements/days/summary_2021.md](Problem_Statements/days/summary_2021.md)
for the day-by-day table.
