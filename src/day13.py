"""Day 13: Transparent Origami.

The input is a list of dots `x,y` on a sheet of transparent paper, then a
list of fold instructions `fold along x=N` or `fold along y=N`.  Folding
along y=N brings the part below the line up onto the part above it; folding
along x=N brings the part right of the line over to the left.

The paper is a set of dots, not a grid.  A fold is a reflection of each dot
past the line, c -> 2N - c, applied to one coordinate.  Dots that land on
the same spot merge into one, which is exactly what putting them back into a
set does, so the "overlapping dots count once" rule is free.

parse_input reads both sections into a frozenset of dots and a tuple of
(axis, line) folds.

Part 1 is the number of dots after the first fold alone.

Part 2 does every fold, and the dots that are left spell eight capital
letters in a 4-wide, 6-tall block font, one blank column between letters.
part2 renders the dots and reads each 5-column cell against GLYPHS, so the
answer is a string, not the int every other day returns.  GLYPHS holds only
the letters seen in this repo's input, copied from its rendering; a letter
it does not know raises with the picture in the message, so a new shape is
read by eye and added, never guessed.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day13.txt"

Dot = tuple[int, int]
Fold = tuple[str, int]
Paper = tuple[frozenset[Dot], tuple[Fold, ...]]

FOLD_PREFIX = "fold along "

GLYPH_WIDTH = 4
GLYPH_HEIGHT = 6

# Each letter as its six rows, top to bottom.
GLYPHS = {
    ("#..#", "#..#", "####", "#..#", "#..#", "#..#"): "H",
    ("#...", "#...", "#...", "#...", "#...", "####"): "L",
    ("###.", "#..#", "###.", "#..#", "#..#", "###."): "B",
    ("#..#", "#..#", "#..#", "#..#", "#..#", ".##."): "U",
    (".##.", "#..#", "#...", "#.##", "#..#", ".###"): "G",
    ("####", "#...", "###.", "#...", "#...", "#..."): "F",
    ("###.", "#..#", "#..#", "###.", "#.#.", "#..#"): "R",
}


def parse_input(raw: str) -> Paper:
    """Dots as a frozenset of (x, y); folds as ("x" | "y", line) in input order."""
    dots: set[Dot] = set()
    folds: list[Fold] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(FOLD_PREFIX):
            axis, sep, value = line.removeprefix(FOLD_PREFIX).partition("=")
            if axis not in ("x", "y") or not sep or not value.isdigit():
                raise ValueError(f"bad fold instruction: {line!r}")
            folds.append((axis, int(value)))
        else:
            if folds:
                raise ValueError(f"dot after the fold instructions: {line!r}")
            x, sep, y = line.partition(",")
            if not (sep and x.isdigit() and y.isdigit()):
                raise ValueError(f"not an x,y dot: {line!r}")
            dots.add((int(x), int(y)))
    return frozenset(dots), tuple(folds)


def fold(dots: frozenset[Dot], instruction: Fold) -> frozenset[Dot]:
    """Reflect every dot past the line onto the kept side; merged dots become one.

    The statement promises no dot sits on a fold line.  It does not say what
    happens when the folded part is longer than the kept part (a dot would
    land at a negative coordinate), so both are refused rather than guessed.
    """
    axis, line = instruction
    i = 0 if axis == "x" else 1
    folded = set()
    for dot in dots:
        c = dot[i]
        if c == line:
            raise ValueError(f"dot {dot} lies on the fold line {axis}={line}")
        if c > 2 * line:
            raise ValueError(f"dot {dot} would fold past the edge at {axis}={line}")
        if c > line:
            dot = (2 * line - c, dot[1]) if i == 0 else (dot[0], 2 * line - c)
        folded.add(dot)
    return frozenset(folded)


def part1(parsed: Paper) -> int:
    dots, folds = parsed
    if not folds:
        raise ValueError("no fold instructions")
    return len(fold(dots, folds[0]))


def fold_all(parsed: Paper) -> frozenset[Dot]:
    dots, folds = parsed
    for instruction in folds:
        dots = fold(dots, instruction)
    return dots


def sheet_size(parsed: Paper) -> tuple[int, int]:
    """(width, height) of the paper once every fold is done.

    The last fold along an axis keeps the part before its line, so that line
    is the finished size on that axis.  An axis never folded is as wide as
    its furthest dot.  Sizing from the folds, not the dots, keeps a blank
    bottom row or right-hand column in the picture.
    """
    dots, folds = parsed
    last = dict(folds)
    width = last.get("x", max((x for x, _ in dots), default=-1) + 1)
    height = last.get("y", max((y for _, y in dots), default=-1) + 1)
    return width, height


def render(dots: frozenset[Dot], width: int, height: int) -> list[str]:
    """`height` rows of '#' and '.', each `width` wide, from (0, 0)."""
    return ["".join("#" if (x, y) in dots else "." for x in range(width)) for y in range(height)]


def read_letters(rows: list[str]) -> str:
    """Decode rendered rows as GLYPH_WIDTH-wide letters, each followed by one blank column."""
    picture = "\n".join(rows)
    step = GLYPH_WIDTH + 1
    if len(rows) != GLYPH_HEIGHT or not rows[0] or len(rows[0]) % step:
        raise ValueError(f"not a row of {GLYPH_WIDTH}x{GLYPH_HEIGHT} letters:\n{picture}")
    width = len(rows[0])
    letters = []
    for left in range(0, width, step):
        if any(row[left + GLYPH_WIDTH] != "." for row in rows):
            raise ValueError(f"no blank column after the letter at x={left}:\n{picture}")
        cell = tuple(row[left : left + GLYPH_WIDTH] for row in rows)
        if cell not in GLYPHS:
            raise ValueError(f"unknown letter at x={left}:\n" + "\n".join(cell) + f"\nin:\n{picture}")
        letters.append(GLYPHS[cell])
    return "".join(letters)


def part2(parsed: Paper) -> str:
    return read_letters(render(fold_all(parsed), *sheet_size(parsed)))


def solve(raw: str) -> tuple[int, str]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    # Printed one part at a time so part 1's answer is on screen to submit
    # while part 2 is still raising NotImplementedError.
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
