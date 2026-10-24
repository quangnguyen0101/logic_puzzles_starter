"""Kiem tra moi loi giai trong `output/` co thoả yeu cau de bai khong.

    python3 src/heuristic/test_heuristic.py
    python3 src/heuristic/test_heuristic.py --kind light_up
    python3 src/heuristic/test_heuristic.py --dir src/heuristic/output

Doc tung file JSON (dinh dang giong `data/`, kem `known_solution`), chay ham
kiem tra tuong ung trong test_heuristic_light_up / test_heuristic_star_battle,
in bang "de | ket qua | ly do". Thoat voi ma 1 neu co loi giai khong hop le.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.heuristic import test_heuristic_light_up, test_heuristic_star_battle
from src.light_up import LightUpProblem
from src.star_battle import StarBattleProblem

CHECKS = {
    "light_up": (LightUpProblem, test_heuristic_light_up.check),
    "star_battle": (StarBattleProblem, test_heuristic_star_battle.check),
}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Kiem tra loi giai trong output/")
    ap.add_argument("--dir", default=str(ROOT / "src" / "heuristic" / "output"))
    ap.add_argument("--kind", choices=sorted(CHECKS), help="chi kiem tra mot bai")
    args = ap.parse_args(argv)

    base = Path(args.dir)
    kinds = [args.kind] if args.kind else sorted(CHECKS)
    total = passed = failed = skipped = 0

    for kind in kinds:
        cls, check = CHECKS[kind]
        folder = base / kind
        files = sorted(folder.glob("*.json")) if folder.is_dir() else []
        if not files:
            continue
        print(f"== {kind}: {len(files)} file ==")
        for path in files:
            total += 1
            data = json.loads(path.read_text(encoding="utf-8"))
            solution = data.get("known_solution")
            if not solution:
                skipped += 1
                print(f"{path.stem:28} --       chua co loi giai")
                continue
            problem = cls.from_json(path)
            ok, reason = check(problem, solution)
            if ok:
                passed += 1
            else:
                failed += 1
            print(f"{path.stem:28} {'thoa' if ok else 'KHONG':8} {reason}")

    print(f"\n{passed}/{total - skipped} loi giai thoa, {failed} khong thoa, {skipped} chua co")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
