"""Kiem tra moi loi giai trong `data/heuristic_output/` co thoa yeu cau de bai khong.

    python3 -m src.run_test
    python3 -m src.run_test --kind light_up
    python3 -m src.run_test --dir data/heuristic_output

Doc tung file JSON (dinh dang giong `data/`, kem `known_solution`), chay ham
kiem tra tuong ung trong check_light_up / check_star_battle,
in bang "de | ket qua | ly do". Thoat voi ma 1 neu co loi giai khong hop le.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.check_light_up import check as check_light_up
from src.check_star_battle import check as check_star_battle
from src.light_up import LightUpProblem
from src.star_battle import StarBattleProblem

CHECKS = {
    "light_up": (LightUpProblem, check_light_up),
    "star_battle": (StarBattleProblem, check_star_battle),
}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Kiem tra loi giai trong output/")
    ap.add_argument("--dir", default=str(ROOT / "data" / "heuristic_output"))
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
