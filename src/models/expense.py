from datetime import date
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class Expense(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    amount: float
    category: str
    date: date

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be a positive number")
        return v

    @field_validator("category")
    @classmethod
    def category_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("category must not be empty")
        return v.strip()
