"""Day 20: Trench Map.

The input is a 512-entry lookup table (the "enhancement algorithm") and a
small image of light (#) and dark (.) pixels sitting in an infinite dark
plane.  One enhancement replaces every pixel with table[n], where n is the
9-bit number read off the 3x3 window around it, row by row, MSB first.

The catch is the infinite part.  Far from the image every window is all
dark (n = 0) or all light (n = 511), so the whole outside becomes table[0]
or table[511] in one step.  If table[0] is '#', the outside lights up after
step 1 and (if table[511] is '.') goes dark again after step 2.  So an Image
is a finite grid *plus* the one value every pixel outside it has.  Each
enhancement grows the grid by one pixel per side (a pixel just outside can
see into the grid), and the new background is the table entry for an
all-background window.

enhance() reads the 9-bit index as three 3-bit row codes: for each row,
precompute the code of every horizontal triple, then a pixel's index is
top << 6 | mid << 3 | bottom.  That is a shift register per row instead of
nine lookups per pixel.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day20.txt"

PIXEL = {".": 0, "#": 1}


@dataclass(frozen=True)
class Image:
    """A finite grid of 0/1 pixels; every pixel outside it equals `background`."""

    rows: tuple[tuple[int, ...], ...]
    background: int = 0


class Puzzle(NamedTuple):
    algorithm: tuple[int, ...]  # 512 entries, 0 or 1
    image: Image


def parse_pixels(line: str) -> tuple[int, ...]:
    try:
        return tuple(PIXEL[ch] for ch in line)
    except KeyError as err:
        raise ValueError(f"not a pixel row: {line!r}") from err


def parse_input(raw: str) -> Puzzle:
    """Algorithm (may be wrapped over several lines), blank line, image."""
    lines = [line.strip() for line in raw.strip().splitlines()]
    if "" not in lines:
        raise ValueError("expected a blank line between the algorithm and the image")
    split = lines.index("")
    algorithm = parse_pixels("".join(lines[:split]))
    if len(algorithm) != 512:
        raise ValueError(f"algorithm has {len(algorithm)} entries, expected 512")
    if algorithm[0] == 1 and algorithm[511] == 1:
        # Background lights up after step 1 and stays lit: every count is infinite.
        raise ValueError("algorithm maps both the all-dark and all-light window to light")

    rows = tuple(parse_pixels(line) for line in lines[split + 1 :] if line)
    if not rows or len({len(row) for row in rows}) != 1:
        raise ValueError("image must be a non-empty rectangle")
    return Puzzle(algorithm, Image(rows))


def triples(row: list[int]) -> list[int]:
    """3-bit code of each horizontal window: out[c] = row[c] << 2 | row[c+1] << 1 | row[c+2]."""
    return [row[c] << 2 | row[c + 1] << 1 | row[c + 2] for c in range(len(row) - 2)]


def enhance(image: Image, algorithm: tuple[int, ...]) -> Image:
    """One enhancement step: the output grid is one pixel larger on every side."""
    bg = image.background
    width = len(image.rows[0])
    # Pad by two: output pixel (r, c) of the grown grid is centred on padded
    # pixel (r + 1, c + 1), so its window always lies inside the padding.
    blank = [bg] * (width + 4)
    padded = [blank, blank] + [[bg, bg, *row, bg, bg] for row in image.rows] + [blank, blank]
    codes = [triples(row) for row in padded]

    rows = tuple(
        tuple(algorithm[top << 6 | mid << 3 | bot] for top, mid, bot in zip(above, here, below, strict=True))
        for above, here, below in zip(codes, codes[1:], codes[2:])
    )
    return Image(rows, algorithm[511 * bg])


def enhance_n(image: Image, algorithm: tuple[int, ...], steps: int) -> Image:
    for _ in range(steps):
        image = enhance(image, algorithm)
    return image


def lit(image: Image) -> int:
    if image.background:
        raise ValueError("infinitely many lit pixels: the background is lit")
    return sum(map(sum, image.rows))


def part1(puzzle: Puzzle) -> int:
    return lit(enhance_n(puzzle.image, puzzle.algorithm, 2))


def part2(puzzle: Puzzle) -> int:
    return lit(enhance_n(puzzle.image, puzzle.algorithm, 50))


def solve(raw: str) -> tuple[int, int]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
