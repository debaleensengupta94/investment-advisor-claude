import unittest
from core.models import UserProfile
from core.rules_engine import RulesEngine


def _make_profile(risk, goal, age=35):
    return UserProfile(
        age=age,
        monthly_income=50000,
        monthly_savings=10000,
        risk=risk,
        goal=goal,
    )


class TestRulesEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RulesEngine("config/investment_rules.yaml")

    def test_all_combinations_sum_to_100(self):
        for risk in ("LOW", "MEDIUM", "HIGH"):
            for goal in ("SHORT", "MEDIUM", "LONG"):
                with self.subTest(risk=risk, goal=goal):
                    alloc = self.engine.compute_allocation(_make_profile(risk, goal))
                    total = sum(alloc.model_dump().values())
                    self.assertEqual(total, 100, f"{risk}/{goal} sums to {total}")

    def test_young_age_caps_equity_at_20(self):
        # HIGH/LONG base has equity=50; age=22 should cap it at 20
        profile = _make_profile("HIGH", "LONG", age=22)
        alloc = self.engine.compute_allocation(profile)
        self.assertLessEqual(alloc.equity, 20)
        self.assertEqual(sum(alloc.model_dump().values()), 100)

    def test_senior_age_caps_equity_at_15(self):
        # HIGH/LONG base has equity=50; age=60 should cap it at 15
        profile = _make_profile("HIGH", "LONG", age=60)
        alloc = self.engine.compute_allocation(profile)
        self.assertLessEqual(alloc.equity, 15)
        self.assertEqual(sum(alloc.model_dump().values()), 100)

    def test_normal_age_unchanged(self):
        # Age 35 should not trigger any modifier
        profile = _make_profile("HIGH", "LONG", age=35)
        alloc = self.engine.compute_allocation(profile)
        self.assertEqual(alloc.equity, 50)

    def test_invalid_risk_raises_value_error(self):
        with self.assertRaises(Exception):
            UserProfile(age=30, monthly_income=50000, monthly_savings=10000, risk="INVALID", goal="SHORT")


if __name__ == "__main__":
    unittest.main()
