import unittest
from pathlib import Path

from src.heuristic_light_up import heuristic_light_up
from src.heuristic_star_battle import heuristic_star_battle
from src.light_up import LightUpProblem
from src.solver import solve
from src.star_battle import StarBattleProblem


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

CASES = [
    (StarBattleProblem, heuristic_star_battle, DATA / "star_battle" / "sb-5x5-normal-sample.json"),
    (StarBattleProblem, heuristic_star_battle, DATA / "star_battle" / "sb-6x6-shapeless-sample.json"),
    (LightUpProblem, heuristic_light_up, DATA / "light_up" / "lu-7x7-normal-sample.json"),
]


class TestHeuristic(unittest.TestCase):
    def test_solution_is_goal(self):
        for cls, algo, path in CASES:
            with self.subTest(puzzle=path.stem):
                problem = cls.from_json(path)
                result = solve(problem, algo)
                assert result is not None

                self.assertIsNotNone(result["solution"], path.stem)
                state = problem.state_from_coords(result["solution"])
                self.assertTrue(problem.is_goal(state), path.stem)

    def test_result_contract(self):
        for cls, algo, path in CASES:
            with self.subTest(puzzle=path.stem):
                result = solve(cls.from_json(path), algo)
                assert result is not None

                self.assertIn("solution", result)
                self.assertIn("expanded", result)
                self.assertIn("steps", result)
                self.assertGreater(result["expanded"], 0)
                self.assertEqual(len(result["steps"]), len(result["solution"]))

    def test_unsolvable_light_up_returns_none(self):
        problem = LightUpProblem.from_dict(
            {
                "name": "wall_1_no_room",
                "type": "light_up",
                "rows": 1,
                "cols": 1,
                "grid": [["1"]],
            }
        )

        result = solve(problem, heuristic_light_up)
        assert result is not None

        self.assertIsNone(result["solution"])

    def test_algorithms_are_callable_with_problem_only(self):
        problem = StarBattleProblem.from_json(CASES[0][2])

        result = heuristic_star_battle(problem)
        assert result is not None

        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
