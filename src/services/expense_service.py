from __future__ import annotations

from typing import List, Optional
from uuid import uuid4

from fastapi import HTTPException

from src.models.expense import Expense
from src.schemas.expense_schema import ExpenseCreate, ExpenseResponse, TotalResponse
from src.storage.json_storage import load_expenses, save_expenses


def _to_response(expense: Expense) -> ExpenseResponse:
    return ExpenseResponse(
        id=str(expense.id),
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        date=expense.date,
    )


def _as_dict(expense: Expense) -> dict:
    return {
        "id": str(expense.id),
        "title": expense.title,
        "amount": expense.amount,
        "category": expense.category,
        "date": expense.date.isoformat(),
    }


def create_expense(payload: ExpenseCreate) -> ExpenseResponse:
    expenses = load_expenses()
    new_expense = Expense(
        id=uuid4(),
        title=payload.title,
        amount=payload.amount,
        category=payload.category,
        date=payload.date,
    )
    expenses.append(_as_dict(new_expense))
    save_expenses(expenses)
    return _to_response(new_expense)


def get_expenses(category: Optional[str] = None) -> List[ExpenseResponse]:
    raw = load_expenses()
    results = []
    for item in raw:
        expense = Expense(**item)
        if category is None or expense.category.lower() == category.lower():
            results.append(_to_response(expense))
    return results


def get_total(category: Optional[str] = None) -> TotalResponse:
    expenses = get_expenses(category=category)
    total = round(sum(e.amount for e in expenses), 2)
    return TotalResponse(total=total, category=category)


def delete_expense(expense_id: str) -> None:
    expenses = load_expenses()
    original_count = len(expenses)
    updated = [e for e in expenses if e["id"] != expense_id]
    if len(updated) == original_count:
        raise HTTPException(status_code=404, detail=f"Expense '{expense_id}' not found")
    save_expenses(updated)
