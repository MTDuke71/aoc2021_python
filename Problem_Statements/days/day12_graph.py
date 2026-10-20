r"""Render the day 12 cave map as a JPG node diagram.

Run from anywhere:  .venv\Scripts\python.exe Problem_Statements/days/day12_graph.py
Needs Graphviz's `dot` on PATH (not a solution dependency).

Big caves are boxes, small caves ellipses; start is green, end red.  Edges are
drawn from the raw input, untrimmed: the edges parse_input drops (into start,
out of end) are still edges of the map, they just can never be used.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import day12

OUT = Path(__file__).resolve().parent / "day12_graph.jpg"


def to_dot(raw: str, part1: int, part2: int) -> str:
    edges = sorted({tuple(sorted(line.strip().split("-"))) for line in raw.splitlines() if line.strip()})
    caves = sorted({cave for edge in edges for cave in edge})
    lines = [
        "graph caves {",
        '  layout=neato; overlap=false; splines=true; sep="+12"; bgcolor=white; pad=0.3;',
        f'  label="Day 12: Passage Pathing\\n{len(caves)} caves, {len(edges)} edges'
        f'; {part1} paths (part 1), {part2} (part 2)"; labelloc=t; fontsize=18; fontname=Helvetica;',
        "  node [fontname=Helvetica, fontsize=14, style=filled, penwidth=1.5];",
        "  edge [color=gray35, penwidth=1.3];",
    ]
    for cave in caves:
        if cave == day12.START:
            attrs = 'shape=doublecircle, fillcolor="#7fd17f"'
        elif cave == day12.END:
            attrs = 'shape=doublecircle, fillcolor="#f08080"'
        elif day12.is_small(cave):
            attrs = 'shape=ellipse, fillcolor="#e8eef7"'
        else:
            attrs = 'shape=box, fillcolor="#4a6fa5", fontcolor=white, fontsize=16, penwidth=2.5'
        lines.append(f'  "{cave}" [{attrs}];')
    lines += [f'  "{a}" -- "{b}";' for a, b in edges]
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    raw = day12.INPUT.read_text()
    p1, p2 = day12.solve(raw)
    subprocess.run(["dot", "-Tjpg", "-Gdpi=150", "-o", str(OUT)], input=to_dot(raw, p1, p2), text=True, check=True)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
