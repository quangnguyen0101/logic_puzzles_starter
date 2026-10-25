"""Kiem tra mot loi giai Light Up co thoả yeu cau de bai khong.

Quy tac (theo de bai):
  1. Bong den chi dat tren o trang ('.'), khong dat len tuong hay o cam.
  2. Khong co hai bong den chieu nhau tren cung hang/cot khi giua chung khong co tuong.
  3. Moi o trang khong co bong deu duoc chieu sang (boi mot bong tren hang hoac cot,
     khong bi tuong chan).
  4. Moi tuong so n co dung n bong den ke (4 huong).

Ham chinh: check(problem, solution) -> (ok: bool, ly_do: str)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.light_up import LightUpProblem


def _on_board(problem: LightUpProblem, r: int, c: int) -> bool:
    return 0 <= r < problem.rows and 0 <= c < problem.cols


def check(problem: LightUpProblem, solution) -> tuple[bool, str]:
    if not solution:
        return False, "khong co loi giai"

    bulbs = set()
    for cell in solution:
        if not (isinstance(cell, (list, tuple)) and len(cell) == 2):
            return False, f"toa do khong hop le: {cell!r}"
        r, c = int(cell[0]), int(cell[1])
        if not _on_board(problem, r, c):
            return False, f"toa do ngoai ban: ({r}, {c})"
        if problem.grid[r][c] != ".":
            return False, f"dat bong len o khong trong ({r}, {c}): {problem.grid[r][c]!r}"
        if (r, c) in bulbs:
            return False, f"bong trung lap ({r}, {c})"
        bulbs.add((r, c))

    for r, c in bulbs:
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            rr, cc = r + dr, c + dc
            while _on_board(problem, rr, cc) and problem.grid[rr][cc] == ".":
                if (rr, cc) in bulbs:
                    return False, f"hai bong chieu nhau: ({r}, {c}) va ({rr}, {cc})"
                rr, cc = rr + dr, cc + dc

    for r in range(problem.rows):
        for c in range(problem.cols):
            if problem.grid[r][c] != "." or (r, c) in bulbs:
                continue
            lit = False
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                rr, cc = r + dr, c + dc
                while _on_board(problem, rr, cc) and problem.grid[rr][cc] == ".":
                    if (rr, cc) in bulbs:
                        lit = True
                        break
                    rr, cc = rr + dr, cc + dc
                if lit:
                    break
            if not lit:
                return False, f"o ({r}, {c}) khong duoc chieu sang"

    for r in range(problem.rows):
        for c in range(problem.cols):
            cell = problem.grid[r][c]
            if not cell.isdigit():
                continue
            need = int(cell)
            got = sum(
                1
                for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0))
                if (r + dr, c + dc) in bulbs
            )
            if got != need:
                return False, f"tuong ({r}, {c}) can {need} bong, co {got}"

    return True, f"hop le ({len(bulbs)} bong)"


def _selftest() -> int:
    problem = LightUpProblem.from_json(ROOT / "data/light_up/lu-7x7-normal-sample.json")
    solution = problem.known_solution or []
    ok, reason = check(problem, solution)
    assert ok, reason

    bad = [list(x) for x in solution][:-1]
    ok2, _ = check(problem, bad)
    assert not ok2, "phai phat hien loi giai thieu bong"

    ok3, _ = check(problem, [[0, 3]])
    assert not ok3, "phai phat hien bong dat len tuong"
    print("OK", reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
