from typing import Literal
from pydantic import BaseModel, model_validator


class UserProfile(BaseModel):
    age: int
    monthly_income: float
    monthly_savings: float
    risk: Literal["LOW", "MEDIUM", "HIGH"]
    goal: Literal["SHORT", "MEDIUM", "LONG"]


class Allocation(BaseModel):
    fixed_deposit: int
    recurring_deposit: int
    bonds: int
    mutual_funds: int
    equity: int

    @model_validator(mode="after")
    def check_sum(self) -> "Allocation":
        total = (
            self.fixed_deposit
            + self.recurring_deposit
            + self.bonds
            + self.mutual_funds
            + self.equity
        )
        if total != 100:
            raise ValueError(f"Allocation must sum to 100, got {total}")
        return self


class AdvisoryResponse(BaseModel):
    profile: UserProfile
    allocation: Allocation
    explanation: str
    disclaimer: str
    chart_data: dict


class TriageReport(BaseModel):
    timestamp: str
    scores: dict
    issues: list
    overall_score: int
    passed: bool
