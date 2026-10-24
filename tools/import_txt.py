"""Chuyen bo de .txt (dinh dang cua nhom) sang JSON cua repo nay.

    python3 tools/import_txt.py --src /duong/dan/inputs

Moi file .txt -> mot file .json trong data/. File .sol.txt canh do (neu co)
duoc dung lam known_solution.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


COORD_NOTE = "zero-based [row, col], (0, 0) is the top-left cell"


def dumps(data: dict) -> str:
    """Giong dinh dang file cua repo: moi hang so lieu nam tren mot dong."""
    text = json.dumps(data, ensure_ascii=False, indent=2)
    text = re.sub(
        r"\[\s*([^\[\]{}]*?)\s*\]",
        lambda m: "["
        + ", ".join(x.strip() for x in m.group(1).split(","))
        + "]",
        text,
    )
    return text + "\n"


def parse_txt(path: Path) -> dict:
    sections: dict[str, list[str]] = {}
    key = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        head = line.split()
        if len(head) == 1 and head[0].isalpha():
            key = head[0]
            sections[key] = []
        elif 2 <= len(head) <= 3 and head[0] == "size":
            sections["size"] = head[1:]
        elif len(head) == 2 and head[0] == "stars":
            sections["stars"] = [head[1]]
        else:
            sections[key].append(line)
    return sections


def coords_from_solution(path: Path):
    if not path.exists():
        return None
    rows = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return [[r, c] for r, row in enumerate(rows) for c, ch in enumerate(row.split()) if ch == "*"]


def convert(path: Path) -> tuple[str, dict]:
    sec = parse_txt(path)
    dims = [int(x) for x in sec["size"]]
    rows = dims[0]
    cols = dims[1] if len(dims) > 1 else dims[0]
    sol = coords_from_solution(path.with_suffix(".sol.txt"))
    name = path.stem

    if "grid" in sec:
        grid = [list(row) for row in sec["grid"]]
        if len(grid) != rows or any(len(r) != cols for r in grid):
            raise SystemExit(f"{path}: luoi {len(grid)}x{len(grid[0])} khac khai bao {rows}x{cols}")
        data = {
            "name": name,
            "type": "light_up",
            "rows": rows,
            "cols": cols,
            "grid": grid,
            "coordinates": COORD_NOTE,
            "known_solution": sol or [],
        }
        return "light_up", data

    stars = int(sec["stars"][0])
    if "regions" in sec:
        data = {
            "name": name,
            "type": "star_battle",
            "variant": "normal",
            "rows": rows,
            "cols": cols,
            "stars_per_unit": stars,
            "regions": [
                [int(x) - 1 for x in row.split()] for row in sec["regions"]
            ],
            "blocked_cells": [],
            "known_solution": sol or [],
        }
    else:
        walls = [[r, c] for r, row in enumerate(sec["walls"]) for c, ch in enumerate(row.split()) if ch == "X"]
        data = {
            "name": name,
            "type": "star_battle",
            "variant": "shapeless",
            "rows": rows,
            "cols": cols,
            "stars_per_unit": stars,
            "blocked_cells": walls,
            "known_solution": sol or [],
        }
    return "star_battle", data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True, help="thu muc inputs (co star_battle/ va light_up/)")
    ap.add_argument("--dst", default="data", help="thu muc data cua repo")
    args = ap.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    written = 0

    for puzzle in ("star_battle", "light_up"):
        out_dir = dst / puzzle
        out_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted((src / puzzle).glob("*.txt")):
            if path.name.endswith(".sol.txt"):
                continue
            kind, data = convert(path)
            if kind != puzzle:
                raise SystemExit(f"{path}: loai {kind} nam nham thu muc")
            (out_dir / f"{path.stem}.json").write_text(
                dumps(data), encoding="utf-8"
            )
            written += 1

    print(f"da ghi {written} file json vao {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
