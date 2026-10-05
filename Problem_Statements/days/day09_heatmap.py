r"""Render the day 9 height map as a PNG, with the low points marked.

Run from anywhere:  .venv\Scripts\python.exe Problem_Statements/days/day09_heatmap.py
Needs matplotlib (not a solution dependency).
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import day09

OUT = Path(__file__).resolve().parent / "day09_heatmap.png"


def main() -> None:
    grid = day09.parse_input(day09.INPUT.read_text())
    lows = day09.low_points(grid)

    fig, ax = plt.subplots(figsize=(9, 8), dpi=100)
    # Heights 0-8 ride cividis (stopping short of its yellow end); 9s are white.
    colours = [*plt.get_cmap("cividis")(np.linspace(0, 0.9, 9)), (1, 1, 1, 1)]
    im = ax.imshow(grid, cmap=ListedColormap(colours), norm=BoundaryNorm(range(11), 10))
    ax.scatter(
        [c for _, c in lows],
        [r for r, _ in lows],
        s=14,
        facecolors="none",
        edgecolors="red",
        linewidths=0.8,
        label=f"low points ({len(lows)})",
    )
    ax.set_title("Day 9: Smoke Basin height map")
    ax.legend(loc="upper right", framealpha=0.9)
    cbar = fig.colorbar(im, ax=ax, label="height", ticks=np.arange(10) + 0.5)
    cbar.ax.set_yticklabels(range(10))
    fig.tight_layout()
    fig.savefig(OUT)
    print(f"wrote {OUT} ({len(lows)} low points)")


if __name__ == "__main__":
    main()
