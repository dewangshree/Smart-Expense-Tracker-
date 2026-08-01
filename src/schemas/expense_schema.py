from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1)
    amount: float
    category: str = Field(..., min_length=1)
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


class ExpenseResponse(BaseModel):
    id: str
    title: str
    amount: float
    category: str
    date: date


class TotalResponse(BaseModel):
    total: float
    category: Optional[str] = None
