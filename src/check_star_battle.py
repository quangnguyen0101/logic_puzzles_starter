"""Kiem tra mot loi giai Star Battle co thoả yeu cau de bai khong.

Quy tac (theo de bai):
  1. Sao chi dat tren o trong (khong dat len o bi chan).
  2. Moi hang co dung `stars_per_unit` sao.
  3. Moi cot co dung `stars_per_unit` sao.
  4. Moi vung co dung `stars_per_unit` sao (bo qua voi de shapeless khong co vung).
  5. Khong co hai sao ke nhau, ke ca duong cheo.

Ham chinh: check(problem, solution) -> (ok: bool, ly_do: str)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.star_battle import StarBattleProblem


def check(problem: StarBattleProblem, solution) -> tuple[bool, str]:
    if not solution:
        return False, "khong co loi giai"

    stars = set()
    for cell in solution:
        if not (isinstance(cell, (list, tuple)) and len(cell) == 2):
            return False, f"toa do khong hop le: {cell!r}"
        r, c = int(cell[0]), int(cell[1])
        if not (0 <= r < problem.rows and 0 <= c < problem.cols):
            return False, f"toa do ngoai ban: ({r}, {c})"
        if (r, c) in problem.blocked_cells:
            return False, f"dat sao len o bi chan ({r}, {c})"
        if (r, c) in stars:
            return False, f"sao trung lap ({r}, {c})"
        stars.add((r, c))

    need = problem.stars_per_unit
    for r in range(problem.rows):
        got = sum(1 for sr, _ in stars if sr == r)
        if got != need:
            return False, f"hang {r} co {got} sao, can {need}"
    for c in range(problem.cols):
        got = sum(1 for _, sc in stars if sc == c)
        if got != need:
            return False, f"cot {c} co {got} sao, can {need}"

    if problem.regions is not None:
        counts: dict[int, int] = {}
        for r, c in stars:
            region = problem.regions[r][c]
            counts[region] = counts.get(region, 0) + 1
        for region in {x for row in problem.regions for x in row}:
            if counts[region] != need:
                return False, f"vung {region} co {counts[region]} sao, can {need}"

    for r, c in stars:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if (dr, dc) != (0, 0) and (r + dr, c + dc) in stars:
                    return False, f"hai sao ke nhau: ({r}, {c}) va ({r + dr}, {c + dc})"

    return True, f"hop le ({len(stars)} sao)"


def _selftest() -> int:
    for name in ("sb-5x5-normal-sample", "sb-6x6-shapeless-sample"):
        problem = StarBattleProblem.from_json(ROOT / "data/star_battle" / f"{name}.json")
        solution = problem.known_solution or []
        ok, reason = check(problem, solution)
        assert ok, f"{name}: {reason}"

        bad = [list(x) for x in solution][:-1]
        ok2, _ = check(problem, bad)
        assert not ok2, f"{name}: phai phat hien loi giai thieu sao"
        print("OK", name, reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
