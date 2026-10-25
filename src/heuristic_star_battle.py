"""A* cho Star Battle.

Trang thai dung chung dinh dang cua repo: tuple bitmask, moi phan tu mot hang.
Nut goc la ban co trong, moi buoc dat mot ngoi sao.

h(n) = so sao con thieu = stars_per_unit * rows - g.  Day la chan duoi dung
(moi buoc chi dat duoc mot sao) nen A* khong bao gio bo qua loi giai ngan hon.
Vi f = g + h la hang so, thu tu mo rong do buoc tie-break quyet dinh: uu tien
nut ma hang sap xep duoc it lua chon nhat va o dat sao "an" duoc nhieu rang buoc
nhat. Cach nay giu duoc tinh dung dan cua A* trong khi van hut duoc khong gian
tim kiem nho cat nhanh cua is_valid_state.

    from src.star_battle import StarBattleProblem
    from src.solver import solve
    from src.heuristic_star_battle import heuristic_star_battle

    problem = StarBattleProblem.from_json("data/star_battle/sb-5x5-normal-01.json")
    result = solve(problem, heuristic_star_battle)
"""

from __future__ import annotations

import heapq
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.star_battle import StarBattleProblem


def _candidates(problem: StarBattleProblem, state: tuple[int, ...], row: int):
    """Cac bo cot co the dat du sao cho hang `row`, sap theo do "an" rang buoc."""
    k = problem.stars_per_unit
    cols = problem.cols
    free = [
        c for c in range(cols)
        if not (state[row] >> c) & 1 and (row, c) not in problem.blocked_cells
    ]
    if len(free) < k:
        return []

    col_count = [0] * cols
    for mask in state:
        for c in range(cols):
            if (mask >> c) & 1:
                col_count[c] += 1
    region_count: dict[object, int] = {}
    if problem.regions is not None:
        for r, mask in enumerate(state):
            for c in range(cols):
                if (mask >> c) & 1:
                    rid = problem.regions[r][c]
                    region_count[rid] = region_count.get(rid, 0) + 1

    scored = []
    for combo in combinations(free, k):
        filled = 0
        ok = True
        seen_cols = set()
        for c in combo:
            if col_count[c] >= k or c in seen_cols:
                ok = False
                break
            seen_cols.add(c)
            filled += 1 if col_count[c] + 1 == k else 0
            if problem.regions is not None:
                rid = problem.regions[row][c]
                used = region_count.get(rid, 0) + sum(
                    1 for cc in combo if cc <= c and problem.regions[row][cc] == rid
                )
                if used > k:
                    ok = False
                    break
                if used == k:
                    filled += 1
        if ok:
            mask = 0
            for c in combo:
                mask |= 1 << c
            scored.append((filled, mask))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored


def heuristic_star_battle(problem: StarBattleProblem):
    rows, cols, k = problem.rows, problem.cols, problem.stars_per_unit
    total = rows * k
    start: tuple[int, ...] = tuple([0] * rows)

    if problem.is_goal(start):
        return {"solution": [], "expanded": 0, "steps": [], "generated": 1, "frontier_peak": 1}

    counter = 0
    heap = [(total, 0, 0, counter, start)]
    seen = {start}
    expanded = 0
    generated = 1
    peak = 1

    while heap:
        _, neg_fill, _, _, state = heapq.heappop(heap)
        expanded += 1

        row = next((r for r in range(rows) if state[r].bit_count() < k), None)
        if row is None:
            if problem.is_goal(state):
                return {
                    "solution": problem.coords_from_state(state),
                    "expanded": expanded,
                    "steps": _steps(problem, state),
                    "generated": generated,
                    "frontier_peak": peak,
                }
            continue

        for score, mask in _candidates(problem, state, row):
            nxt = state[:row] + (state[row] | mask,) + state[row + 1:]
            if nxt in seen:
                continue
            if not problem.is_valid_state(nxt, partial=True):
                continue
            seen.add(nxt)
            generated += 1
            g = sum(m.bit_count() for m in nxt)
            h = total - g
            counter += 1
            heapq.heappush(heap, (g + h, -score, h, counter, nxt))
            peak = max(peak, len(heap))

    return {"solution": None, "expanded": expanded, "steps": [], "generated": generated, "frontier_peak": peak}


def _steps(problem: StarBattleProblem, state: tuple[int, ...]) -> list[dict]:
    out = []
    for r, c in problem.coords_from_state(state):
        out.append({"row": r, "col": c})
    return out


def main(argv: list[str] | None = None) -> int:
    import argparse

    from src.solver import solve

    ap = argparse.ArgumentParser(description="Giai Star Battle bang A*")
    ap.add_argument("input", help="file JSON cua de bai")
    args = ap.parse_args(argv)

    problem = StarBattleProblem.from_json(args.input)
    result = solve(problem, heuristic_star_battle)
    print(f"{problem.name}: {problem.rows}x{problem.cols}, mo rong {result['expanded']} nut")
    if not result["solution"]:
        print("khong tim thay loi giai")
        return 1
    state = problem.state_from_coords(result["solution"])
    print(problem.render(state))
    print("is_goal:", problem.is_goal(state))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
