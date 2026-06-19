import yaml
from core.models import Allocation, UserProfile


class RulesEngine:
    def __init__(self, rules_file: str = "config/investment_rules.yaml"):
        with open(rules_file, "r") as f:
            data = yaml.safe_load(f)
        # Build lookup: (risk, goal) -> allocation dict
        self._rules: dict[tuple[str, str], dict] = {}
        for rule in data["rules"]:
            key = (rule["risk"], rule["goal"])
            self._rules[key] = rule["allocation"]
        self._age_modifiers = data["age_modifiers"]

    def compute_allocation(self, profile: UserProfile) -> Allocation:
        key = (profile.risk, profile.goal)
        if key not in self._rules:
            raise ValueError(f"No rule found for risk={profile.risk}, goal={profile.goal}")

        alloc = dict(self._rules[key])  # copy so we don't mutate the source

        # Apply age modifier
        young = self._age_modifiers["young"]
        senior = self._age_modifiers["senior"]

        if profile.age < young["max_age"]:
            cap = young["equity_cap"]
            if alloc["equity"] > cap:
                excess = alloc["equity"] - cap
                alloc["equity"] = cap
                alloc["fixed_deposit"] += excess

        elif profile.age > senior["min_age"]:
            cap = senior["equity_cap"]
            if alloc["equity"] > cap:
                excess = alloc["equity"] - cap
                alloc["equity"] = cap
                # Redistribute excess equally between fixed_deposit and bonds
                half = excess // 2
                remainder = excess - half
                alloc["fixed_deposit"] += half
                alloc["bonds"] += remainder

        # Normalise: handle any rounding drift so sum == 100
        total = sum(alloc.values())
        if total != 100:
            diff = 100 - total
            # Add/subtract difference from fixed_deposit (most conservative bucket)
            alloc["fixed_deposit"] += diff

        assert sum(alloc.values()) == 100, f"Allocation sum is {sum(alloc.values())}, expected 100"

        return Allocation(
            fixed_deposit=alloc["fixed_deposit"],
            recurring_deposit=alloc["recurring_deposit"],
            bonds=alloc["bonds"],
            mutual_funds=alloc["mutual_funds"],
            equity=alloc["equity"],
        )
