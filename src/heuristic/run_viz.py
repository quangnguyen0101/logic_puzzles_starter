"""Phan ve hinh dung chung cho viz_puzzle.py va viz_solution.py.

Hai file CLI chi goi `main(argv, with_solution=...)`:

    viz_puzzle.py    -> ve de bai (khong co loi giai)
    viz_solution.py  -> ve de bai kem loi giai (known_solution)

Chi can matplotlib de ve; phan mo hinh va test khong phu thuoc vao file nay.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.light_up import LightUpProblem
from src.star_battle import StarBattleProblem

CELL = 0.4
GRID = "#8a8a8a"
INK = "#1a1a1a"
WALL = "#3b3b3b"


def _palette(n: int) -> list[tuple[float, float, float]]:
    from matplotlib.colors import hsv_to_rgb

    out = []
    for i in range(max(n, 1)):
        h = (i * 0.6180339887498949) % 1.0
        s = 0.45 if i % 2 else 0.75
        out.append(tuple(hsv_to_rgb((h, s, 0.98))))
    return out


def _figure(rows: int, cols: int):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(cols * CELL, rows * CELL))
    ax.set_xlim(0, cols)
    ax.set_ylim(rows, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax, plt


def _cells(ax, rows: int, cols: int, lw: float = 0.8) -> None:
    from matplotlib.patches import Rectangle

    for r in range(rows):
        for c in range(cols):
            ax.add_patch(
                Rectangle((c, r), 1, 1, fill=False, lw=lw, edgecolor=GRID, zorder=3)
            )


def _bulb(ax, r: int, c: int, size: float = 0.30) -> None:
    from matplotlib.patches import Circle

    ax.add_patch(Circle((c + 0.5, r + 0.5), size, color="#f4c430", zorder=4))
    ax.add_patch(
        Circle(
            (c + 0.5, r + 0.5), size, fill=False, lw=0.8,
            edgecolor="#8a6d00", zorder=5,
        )
    )


def _star(ax, r: int, c: int) -> None:
    ax.text(
        c + 0.5, r + 0.5, "*", ha="center", va="center_baseline",
        fontsize=17, color=INK, zorder=4,
    )


def draw(problem, solution=None, path: str | Path = "out.png", dpi: int = 150):
    from matplotlib.patches import Rectangle

    rows, cols = problem.rows, problem.cols
    fig, ax, plt = _figure(rows, cols)

    if isinstance(problem, StarBattleProblem):
        if problem.blocked_cells:
            for r, c in problem.blocked_cells:
                ax.add_patch(Rectangle((c, r), 1, 1, color=INK, zorder=1))
        else:
            assert problem.regions is not None
            ids = {
                v: i
                for i, v in enumerate(sorted({x for row in problem.regions for x in row}))
            }
            colors = _palette(len(ids))
            for r in range(rows):
                for c in range(cols):
                    ax.add_patch(
                        Rectangle((c, r), 1, 1, color=colors[ids[problem.regions[r][c]]], zorder=1)
                    )
    else:
        for r in range(rows):
            for c in range(cols):
                cell = problem.grid[r][c]
                if cell != ".":
                    ax.add_patch(Rectangle((c, r), 1, 1, color=WALL, zorder=1))
                    if cell != "#":
                        ax.text(
                            c + 0.5, r + 0.5, cell, ha="center", va="center",
                            fontsize=13, color="white", fontweight="bold", zorder=4,
                        )

    _cells(ax, rows, cols)

    if solution:
        place = _bulb if isinstance(problem, LightUpProblem) else _star
        for r, c in solution:
            place(ax, r, c)

    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(fig)
    return Path(path)


def _problem_class(kind: str):
    return LightUpProblem if kind == "light_up" else StarBattleProblem


def _selftest(with_solution: bool) -> int:
    import tempfile

    from PIL import Image

    problem = LightUpProblem.from_json(ROOT / "data/light_up/lu-7x7-normal-sample.json")
    out = Path(tempfile.gettempdir()) / f"viz-selftest-{int(with_solution)}.png"
    draw(problem, problem.known_solution if with_solution else None, out, dpi=60)
    im = Image.open(out).convert("RGB")
    raw = im.tobytes()
    px = [raw[i:i + 3] for i in range(0, len(raw), 3)]
    assert len(set(px)) > 10, "anh chi co mot mau"
    has_bulb = any(c[0] > 200 and c[1] > 150 and c[2] < 120 for c in px)
    if with_solution:
        assert has_bulb, "khong thay bong den"
    else:
        assert not has_bulb, "de bai khong duoc co bong den"
    print("OK", out, im.size)
    return 0


def main(argv: list[str], with_solution: bool) -> int:
    label = "loi giai" if with_solution else "de bai"
    ap = argparse.ArgumentParser(description=f"Ve {label} tu file JSON")
    ap.add_argument("input", nargs="?", help="file .json hoac thu muc chua cac file .json")
    ap.add_argument("--selftest", action="store_true", help="tu kiem tra roi thoat")
    ap.add_argument("-o", "--out", help="file anh ra, hoac thu muc (mac dinh figs/<kind>/<loai>)")
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest(with_solution)
    if not args.input:
        ap.error("thieu file hoac thu muc input")

    src = Path(args.input)
    files = sorted(src.glob("*.json")) if src.is_dir() else [src]
    if not files:
        print(f"khong co file .json trong {src}")
        return 1

    sub = "solution" if with_solution else "puzzle"
    drawn = skipped = 0
    for f in files:
        kind = json.loads(f.read_text(encoding="utf-8"))["type"]
        problem = _problem_class(kind).from_json(f)
        solution = problem.known_solution if with_solution else None
        if with_solution and not solution:
            skipped += 1
            continue
        if len(files) == 1 and args.out:
            out = Path(args.out)
        else:
            out_dir = Path(args.out) if args.out else ROOT / "figs" / kind / sub
            out_dir.mkdir(parents=True, exist_ok=True)
            out = out_dir / f"{f.stem}.png"
        print("ve", draw(problem, solution, out, args.dpi))
        drawn += 1
    if skipped:
        print(f"bo qua {skipped} de chua co known_solution")
    return 0
