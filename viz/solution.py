"""Ve de bai kem loi giai (known_solution).

    python3 viz/solution.py data/heuristic_output/star_battle
    python3 viz/solution.py data/light_up/lu-7x7-normal-sample.json -o hinh.png
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from viz.core import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:], with_solution=True))
